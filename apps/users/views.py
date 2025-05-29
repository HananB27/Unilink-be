import json

from django.contrib.auth import login, authenticate, logout, get_user_model
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from apps.users.models import ROLES
from db.graph.graph_models import User as UserNode, Company

User = get_user_model()

# Create your views here.
def hello(request):
    return JsonResponse({'message': 'hello world'})

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        try:
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
                    comp_graph=Company(name=username, email=email, profile_picture=profile_picture).save()
                    user_graph=UserNode(email=email, name=username.strip(), role=role).save()
                    user_graph.represents.connect(comp_graph)
                else:
                    UserNode(email=email, name=f"{first_name} {last_name}".strip(), role=role).save()
            except Exception as graph_error:
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
        print("[DEBUG] Method not POST")
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    try:
        print(f"[DEBUG] user_id received: {user_id}")
        if not user_id:
            print("[DEBUG] No user_id provided")
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        user = User.objects.get(id=user_id)
        print(f"[DEBUG] User found: ID={user.id}, email={user.email}, username={user.username}, role={getattr(user, 'role', None)}")

        user_email = user.email
        username = user.username
        role = getattr(user, 'role', None)

        # Delete profile picture
        if user.profile_picture:
            print(f"[DEBUG] User has profile picture: {user.profile_picture.name}")
            if default_storage.exists(user.profile_picture.name):
                default_storage.delete(user.profile_picture.name)
                print("[DEBUG] Profile picture deleted from storage")
            else:
                print("[DEBUG] Profile picture file does not exist in storage")
        else:
            print("[DEBUG] User has no profile picture")

        # Delete Company node if role is 'company'
        if role == 'company':
            print(f"[DEBUG] Attempting to delete Company node for name={username}")
            company_node = Company.nodes.get_or_none(name=username)
            if company_node:
                company_node.delete()
                print("[DEBUG] Company node deleted")
            else:
                print("[DEBUG] Company node not found")

        # Delete graph user node
        print(f"[DEBUG] Attempting to delete UserNode with name={username}")
        graph_user = UserNode.nodes.get_or_none(name=username)
        if graph_user:
            graph_user.delete()
            print("[DEBUG] UserNode deleted")
        else:
            print("[DEBUG] UserNode not found")

        # Delete the user from relational DB
        user.delete()
        print("[DEBUG] Django user deleted")

        return JsonResponse({'message': 'User deleted'}, status=200)

    except User.DoesNotExist:
        print("[ERROR] User not found in DB")
        return JsonResponse({'error': 'User does not exist'}, status=404)
    except Exception as e:
        print(f"[ERROR] Unexpected exception: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)
