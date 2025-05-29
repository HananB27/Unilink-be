import json

from django.contrib.auth import login, authenticate, logout, get_user_model
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt

from apps.users.models import ROLES
from db.graph.graph_models import User as UserNode, Company, University, Department

User = get_user_model()

# Create your views here.
def hello(request):
    return JsonResponse({'message': 'hello world'})

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                email = request.POST.get('email')
                username = request.POST.get('username')
                password = request.POST.get('password')
                first_name = request.POST.get('first_name')
                last_name = request.POST.get('last_name')
                role = request.POST.get('role')
                profile_picture = request.FILES.get('profile_picture')

                if role not in dict(ROLES):
                    return JsonResponse({'error': 'invalid role'}, status=400)

                if not email or not password or not username:
                    return JsonResponse({'error': 'Missing required fields'}, status=400)

                if User.objects.filter(email=email).exists():
                    return JsonResponse({'error': 'Email already in use'}, status=400)

                user = User.objects.create_user(
                    email=email,
                    username=username,
                    first_name=first_name or '',
                    last_name=last_name or '',
                    password=password,
                    profile_picture=profile_picture,
                    role=role
                )

                try:
                    if role == 'company':
                        Company(name=username).save()
                    elif role == 'university':
                        University(name=username).save()
                    elif role == 'department':
                        Department(name=username).save()
                except Exception as graph_error:
                    user.delete()
                    return JsonResponse({'error': f'Neo4j error: {str(graph_error)}'}, status=500)

                return JsonResponse({'message': 'User created successfully'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only POST allowed'}, status=405)

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')

            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({'message': 'Logged in'}, status=200)
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Only POST allowed'}, status=405)

@csrf_exempt
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'message': 'Logged out'}, status=200)
    return JsonResponse({'error': 'Only POST allowed'}, status=405)

@csrf_exempt
def delete_user(request, user_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    debug_log = []

    try:
        with transaction.atomic():
            if not user_id:
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            user = User.objects.get(id=user_id)
            role = getattr(user, 'role', None)
            username = user.username
            email = user.email

            debug_log.append(f"User found: ID={user.id}, email={email}, username={username}, role={role}")

            # Delete profile picture
            if user.profile_picture:
                if default_storage.exists(user.profile_picture.name):
                    default_storage.delete(user.profile_picture.name)
                    debug_log.append("Profile picture deleted from storage.")
                else:
                    debug_log.append("Profile picture file does not exist in storage.")
            else:
                debug_log.append("User has no profile picture.")

            if role == 'company':
                node = Company.nodes.get_or_none(name=username)
                if node:
                    node.delete()
                    debug_log.append("Company node deleted.")
                else:
                    debug_log.append("Company node not found.")
            elif role == 'university':
                node = University.nodes.get_or_none(name=username)
                if node:
                    node.delete()
                    debug_log.append("University node deleted.")
                else:
                    debug_log.append("University node not found.")
            elif role == 'department':
                node = Department.nodes.get_or_none(name=username)
                if node:
                    node.delete()
                    debug_log.append("Department node deleted.")
                else:
                    debug_log.append("Department node not found.")
            else:
                debug_log.append(f"No representable node deletion needed for role: {role}")

            # Delete UserNode in Neo4j
            graph_user = UserNode.nodes.get_or_none(name=username)
            if graph_user:
                graph_user.delete()
                debug_log.append("UserNode deleted.")
            else:
                debug_log.append("UserNode not found.")

            # Delete from Django
            user.delete()
            debug_log.append("Django user deleted.")

            return JsonResponse({
                'message': 'User deleted',
                'debug_log': debug_log
            }, status=200)

    except User.DoesNotExist:
        return JsonResponse({'error': 'User does not exist'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
