import json

from django.contrib.auth import login, authenticate, logout, get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

User = get_user_model()

# Create your views here.
def hello(request):
    return JsonResponse({'message': 'hello world'})

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            username = data.get('username')
            password = data.get('password')
            first_name = data.get('first_name')
            last_name = data.get('last_name')

            if not email or not password or not username:
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({'error': 'Email already in use'}, status=400)

            user = User.objects.create_user(
                email=email,
                username=username,
                first_name=first_name or '',
                last_name=last_name or '',
                password=password
            )
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
