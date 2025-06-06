import os

from PIL.TiffTags import TAGS_V2
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import authentication_classes, permission_classes, api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from Unilink_be import settings
from apps.posts.models import Posts, PostTags, Tags
from apps.posts.serializer import PostSerializer
from db.graph.graph_models import Post, User, Tag, OfficialAccount
from utils.embeddings import embed_text

Users = get_user_model()

def check_permission(request, obj):
    if request.method in ['GET', 'HEAD', 'OPTIONS']:
        return True, None
    if hasattr(obj, 'user') and obj.user == request.user:
        return True, None
    else:
        return False, JsonResponse({'message': 'You do not have permission to perform this action.'}, status=403)

def get_graph_account_node(email, user_role):
    if user_role in ['department', 'company', 'admin', 'university']:
        node = OfficialAccount.nodes.get_or_none(email=email)
        if not node:
            raise ValueError(f"Official account node not found for email: {email}")
    else:
        node = User.nodes.get_or_none(email=email)
        if not node:
            raise ValueError(f"User node not found for email: {email}")

    print(f"{node} ======================= THIS IS THE NODE==========================")
    return node

@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
@csrf_exempt
def get_posts(request):
    if request.method != 'GET':
        return JsonResponse({'message': 'Method not allowed'}, status=405)

    queryset = Posts.objects.all().order_by('-created_at')

    author_id = request.GET.get('author_id')
    if author_id:
        try:
            queryset = queryset.filter(user__id=author_id)
        except ValueError:
            return JsonResponse({'message': 'Invalid author id'}, status=400)
        except Posts.DoesNotExist: # Use specific exception for clarity
            return JsonResponse({'message': 'Author not found'}, status=404)

    serializer = PostSerializer(queryset, many=True, context={'request': request})
    return JsonResponse(serializer.data, safe=False, status=200)

@api_view(['POST'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
@csrf_exempt
def create_post(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Method not allowed'}, status=405)

    try:
        data = request.data.copy()
        tag_names = data.pop('tags', [])
    except Exception as e:
        return JsonResponse({'message': f'Error parsing request data: {str(e)}'}, status=400)

    user_email = request.user.email
    if not user_email:
        return JsonResponse({'message': 'Authenticated user email is missing.'}, status=400)

    try:
        django_user_obj = Users.objects.get(email=user_email)
    except Users.DoesNotExist:
        return JsonResponse({'message': 'User not found in relational database.'}, status=404)
    except Exception as e:
        return JsonResponse({'message': f'Error fetching user from relational DB: {str(e)}'}, status=500)

    user_role = getattr(django_user_obj, 'role', 'student')
    with transaction.atomic():
        serializer = PostSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=django_user_obj)

            post_instance = serializer.instance
            text_to_embed = f"{post_instance.title or ''} {post_instance.content}"
            embedding_vector = embed_text(text_to_embed)

            if embedding_vector:
                post_instance.embedding = embedding_vector
                post_instance.save(update_fields=['embedding'])

            try:
                account_node = get_graph_account_node(user_email, user_role)

                graph_post = Post(
                    post_id=str(serializer.data['id']),
                    content=serializer.data['content'],
                    title=serializer.data['title'],
                    image=serializer.data['image'],
                    created_at=timezone.now(),
                    updated_at=serializer.data['updated_at'],
                ).save()

                account_node.posted.connect(graph_post)

                # Handle tags
                for tag_name in tag_names:
                    clean_name = tag_name.strip().lower()
                    if not clean_name:
                        continue

                    tag_obj, _ = Tags.objects.get_or_create(name=clean_name)
                    PostTags.objects.get_or_create(post=serializer.instance, tag=tag_obj)

                    tag_node = Tag.nodes.get_or_none(name=clean_name)
                    if not tag_node:
                        tag_node = Tag(name=clean_name).save()
                    graph_post.tagged_with.connect(tag_node)

            except ValueError as ve:
                transaction.set_rollback(True)
                return JsonResponse({'message': str(ve)}, status=400)
            except Exception as e:
                transaction.set_rollback(True)
                return JsonResponse({'message': f'Error creating graph post: {str(e)}'}, status=400)

            return JsonResponse(serializer.data, status=201)
        else:
            return JsonResponse(serializer.errors, status=400)

@api_view(['PUT'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
@csrf_exempt
def update_post(request, id):
    try:
        post = Posts.objects.get(id=id)
    except Posts.DoesNotExist:
        return JsonResponse({'message': 'Post not found'}, status=404)

    has_permission, response = check_permission(request, post)
    if not has_permission:
        return response

    serializer = PostSerializer(post, data=request.data, partial=True, context={'request': request})
    if serializer.is_valid():
        serializer.save()

        graph_post = Post.nodes.get_or_none(post_id=id)
        if graph_post:
            if 'content' in request.data:
                graph_post.content = request.data['content']
            if 'title' in request.data:
                graph_post.title = request.data['title']
            graph_post.save()

        return JsonResponse(serializer.data, status=200)
    return JsonResponse(serializer.errors, status=400)


@api_view(['DELETE'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
@csrf_exempt
def delete_post(request, uid):
    try:
        post = Posts.objects.get(id=uid)
    except Posts.DoesNotExist:
        return JsonResponse({'message': 'Post not found'}, status=404)

    has_permission, response = check_permission(request, post)
    if not has_permission:
        return response

    image_path = None
    if post.image:
        image_path = os.path.join(settings.MEDIA_ROOT, post.image.name)

    try:
        graph_post = Post.nodes.get_or_none(post_id=str(uid))
        if graph_post:
            graph_post.delete()

        if post.image:
            image_path = os.path.join(settings.MEDIA_ROOT, post.image.name)
            if os.path.exists(image_path):
                os.remove(image_path)

        post.delete()
    except Exception as e:
        return JsonResponse({'message': f'Error deleting post or image: {str(e)}'}, status=500)

    return JsonResponse({'message': 'Post deleted successfully'}, status=204)
