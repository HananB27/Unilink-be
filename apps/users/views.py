import json

from django.contrib.auth import login, authenticate, logout, get_user_model
from neomodel import db
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from neomodel.exceptions import DoesNotExist as NeoModelDoesNotExist, MultipleNodesReturned
from django.http import JsonResponse
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt

from apps.users.models import ROLES, Users
from db.graph.graph_models import User as UserNode, Company, University, Department, User
from utils.embeddings import embed_text

DjangoUser = get_user_model()

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

                if DjangoUser.objects.filter(email=email).exists():
                    return JsonResponse({'error': 'Email already in use'}, status=400)

                user = DjangoUser.objects.create_user(
                    email=email,
                    username=username,
                    first_name=first_name or '',
                    last_name=last_name or '',
                    password=password,
                    profile_picture=profile_picture,
                    role=role
                )

                text = f"{first_name or ''} {last_name or ''} {role} {username or ''}"
                embedding_vector = embed_text(text)

                if embedding_vector:
                    user.embedding = embedding_vector
                    user.save(update_fields=["embedding"])

                try:
                    if role == 'company':
                        Company(name=username, email=email).save()
                    elif role == 'university':
                        University(name=username, email=email).save()
                    elif role == 'department':
                        Department(name=username, email=email).save()
                except Exception as graph_error:
                    user.delete()
                    return JsonResponse({'error': f'Neo4j error: {str(graph_error)}'}, status=500)
                token = RefreshToken.for_user(user)
                return JsonResponse({
                    'message': 'User created successfully',
                    'access': str(token.access_token),
                    'refresh': str(token),
                }, status=201)
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
                token = RefreshToken.for_user(user)
                return JsonResponse({
                    'message': 'Logged in',
                    'access': str(token.access_token),
                    'refresh': str(token),
                }, status=200)
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

            user = DjangoUser.objects.get(id=user_id)
            role = getattr(user, 'role', None)
            username = user.username
            email = user.email

            debug_log.append(f"User found: ID={user.id}, email={email}, username={username}, role={role}")

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

    except DjangoUser.DoesNotExist:
        return JsonResponse({'error': 'User does not exist'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_node_and_type_by_email(email):
    """
    Attempts to find a Neomodel node by email across different account types.
    Returns (node, node_type_string) or (None, None).
    """
    email = email.lower().strip()  # Normalize email

    # Prioritize specific OfficialAccounts before generic User
    try:
        company_node = Company.nodes.get_or_none(email=email)
        if company_node: return company_node, 'Company'
    except MultipleNodesReturned:
        return None, 'Error'  # Should be unique
    try:
        university_node = University.nodes.get_or_none(email=email)
        if university_node: return university_node, 'University'
    except MultipleNodesReturned:
        return None, 'Error'
    try:
        department_node = Department.nodes.get_or_none(email=email)
        if department_node: return department_node, 'Department'
    except MultipleNodesReturned:
        return None, 'Error'
    try:
        user_node = UserNode.nodes.get_or_none(email=email)
        if user_node: return user_node, 'User'
    except MultipleNodesReturned:
        return None, 'Error'

    return None, None


# Helper function to connect/disconnect based on roles and types
def manage_relationship(requester_node, requester_type, requester_role, target_node, target_type, action):
    """
    Manages the specific relationship between requester and target based on their types and roles.
    `action` can be 'connect' or 'disconnect'.
    Returns (True, "message") on success, (False, "error message") on failure or unsupported.
    """
    try:
        message_prefix = "Successfully" if action == 'connect' else "Successfully removed"
        error_prefix = "Failed to" if action == 'connect' else "Failed to remove"

        # Helper for checking/performing connection
        def _check_and_perform(rel_manager, rel_name):
            if action == 'connect':
                if rel_manager.relationship(target_node):
                    return False, f"Already {rel_name} this {target_type}."
                rel_manager.connect(target_node)
                return True, f"{message_prefix} {rel_name} {target_node.name}."
            else:  # disconnect
                if not rel_manager.relationship(target_node):
                    return False, f"Not {rel_name} this {target_type}."
                rel_manager.disconnect(target_node)
                return True, f"{message_prefix} {rel_name} from {target_node.name}."

        # Helper for checking/performing INCOMING connection (when target has the RelationshipTo)
        def _check_and_perform_incoming(target_rel_manager, rel_name, rel_initiator_node):
            if action == 'connect':
                # Check if the incoming relationship already exists from the specific initiator
                if target_rel_manager(rel_initiator_node).relationship(rel_initiator_node):
                    return False, f"{target_node.name} is already {rel_name} this {rel_initiator_node.name}."
                target_rel_manager(rel_initiator_node).connect(rel_initiator_node)
                return True, f"{message_prefix} {target_node.name} to be {rel_name} {rel_initiator_node.name}."
            else:  # disconnect
                if not target_rel_manager(rel_initiator_node).relationship(rel_initiator_node):
                    return False, f"{target_node.name} is not {rel_name} this {rel_initiator_node.name}."
                target_rel_manager(rel_initiator_node).disconnect(rel_initiator_node)
                return True, f"{message_prefix} {target_node.name} from being {rel_name} {rel_initiator_node.name}."

        # The core logic is now wrapped in a Neomodel transaction
        with db.transaction:
            if requester_type == 'User':
                if target_type == 'User':
                    return _check_and_perform(requester_node.connected_with, 'connected with')

                elif target_type == 'University':
                    if requester_role == 'student':
                        return _check_and_perform(requester_node.affiliated_with, 'affiliated with')
                    elif requester_role == 'professor':
                        return _check_and_perform(requester_node.employed_at,
                                                  'employed at')  # Assuming professors use employed_at for universities
                    else:
                        return False, f"Unsupported role '{requester_role}' for connecting to a university."

                elif target_type == 'Company':
                    return _check_and_perform(requester_node.employed_at, 'employed at')

                elif target_type == 'Department':
                    if requester_role == 'professor':
                        return _check_and_perform(requester_node.works_in_department, 'works in department')
                    else:
                        return False, f"Only professors can connect to departments. Your role is '{requester_role}'."

                else:
                    return False, "Unsupported target type for User requester."

            elif requester_type in ['Company', 'University', 'Department']:  # Official Account types
                if target_type == 'User':
                    # This means an OfficialAccount is "connecting" to a regular user.
                    # The relationship would originate from the User (e.g., employed_at, affiliated_with).
                    # So, we manage the *incoming* relationship on the UserNode.
                    if target_node.role == 'student' and requester_type == 'University':
                        return _check_and_perform_incoming(target_node.affiliated_with, 'affiliated with',
                                                           requester_node)
                    elif target_node.role == 'professor' and requester_type == 'University':
                        return _check_and_perform_incoming(target_node.employed_at, 'employed at', requester_node)
                    elif requester_type == 'Company':
                        return _check_and_perform_incoming(target_node.employed_at, 'employed at', requester_node)
                    elif target_node.role == 'professor' and requester_type == 'Department':  # NEW Rule: Department to Professor
                        return _check_and_perform_incoming(target_node.works_in_department, 'works in department',
                                                           requester_node)
                    else:
                        return False, f"Unsupported connection from {requester_type} to User role '{target_node.role}'."

                elif target_type in ['Company',
                                     'University']:  # Official Account to Official Account (excluding Department targets)
                    # Departments are only connected to Universities directly (as target for BELONGS_TO)
                    # and professors. Not other official accounts through ASSOCIATED_WITH.
                    if requester_type == 'Department':  # Department can only BELONG_TO University
                        if target_type == 'University':
                            return _check_and_perform(requester_node.belongs_to, 'belongs to')
                        else:
                            return False, f"Department can only belong to a University. Cannot associate with {target_type}."

                    # Other Official Accounts can ASSOCIATE_WITH each other
                    else:  # Company or University requester
                        return _check_and_perform(requester_node.associated_with, 'associated with')

                elif target_type == 'Department':  # Official Account to Department
                    if requester_type == 'University':  # University can have a Department BELONG_TO it
                        # This implies the relationship is `Department -[BELONGS_TO]-> University`.
                        # So, if University is requester and Department is target, we manage incoming on Department
                        return _check_and_perform_incoming(target_node.belongs_to, 'belongs to', requester_node)
                    else:
                        return False, f"Only Universities can 'associate' with Departments (via BELONGS_TO). {requester_type} cannot connect to {target_type}."

                else:
                    return False, "Unsupported target type for Official Account requester."
            else:
                return False, "Unsupported requester type."

    except Exception as e:
        # The `with db.transaction:` block automatically handles rollback on exception
        return False, f"{error_prefix} connection: {str(e)}"


# --- Remaining views (truncated for brevity) ---
# ... (your hello, signup, login_view, logout_view, delete_user functions) ...

@api_view(['POST'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def add_friend(request, target_email):
    current_user_email = request.user.email
    current_user_email = current_user_email.lower().strip()  # Normalize

    # Validate target_email format
    if not isinstance(target_email, str) or '@' not in target_email:
        return JsonResponse({'message': 'Invalid target email format.'}, status=400)
    target_email = target_email.lower().strip()  # Normalize

    if current_user_email == target_email:
        return JsonResponse({'message': 'You cannot connect with yourself.'}, status=400)

    # 1. Get Requester Node and Type
    requester_node, requester_type = get_node_and_type_by_email(current_user_email)
    if requester_node is None:
        return JsonResponse({'message': 'Requester user not found in graph database or invalid type.'}, status=404)
    if requester_type == 'Error':
        return JsonResponse({'message': 'Multiple graph nodes found for requester email. Data inconsistency.'},
                            status=500)

    # Get Requester Role from Django User (for User nodes)
    requester_role = None
    if requester_type == 'User':
        try:
            django_requester = DjangoUser.objects.get(email=current_user_email)
            requester_role = django_requester.role
        except DjangoUser.DoesNotExist:
            return JsonResponse({'message': 'Requester user found in graph but not in relational DB.'}, status=404)
        except Exception as e:
            return JsonResponse({'message': f'Error getting requester role from relational DB: {str(e)}'}, status=500)

    # 2. Get Target Node and Type
    target_node, target_type = get_node_and_type_by_email(target_email)
    if target_node is None:
        return JsonResponse({'message': 'Target user not found in graph database or invalid type.'}, status=404)
    if target_type == 'Error':
        return JsonResponse({'message': 'Multiple graph nodes found for target email. Data inconsistency.'}, status=500)

    # 3. Manage Relationship
    success, message = manage_relationship(requester_node, requester_type, requester_role, target_node, target_type,
                                           'connect')

    if success:
        return JsonResponse({'message': message}, status=200)
    else:
        # Determine appropriate status code based on message
        if "Already " in message:  # "Already connected", "Already employed" etc.
            return JsonResponse({'message': message}, status=409)  # Conflict
        elif "Unsupported" in message or "Cannot" in message or "Only " in message or "not explicitly defined" in message:
            return JsonResponse({'message': message}, status=400)  # Bad Request/Not Implemented
        else:
            return JsonResponse({'message': message}, status=500)


@api_view(['DELETE'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def remove_friend(request, target_email):
    current_user_email = request.user.email
    current_user_email = current_user_email.lower().strip()  # Normalize

    # Validate target_email format
    if not isinstance(target_email, str) or '@' not in target_email:
        return JsonResponse({'message': 'Invalid target email format.'}, status=400)
    target_email = target_email.lower().strip()  # Normalize

    if current_user_email == target_email:
        return JsonResponse({'message': 'You cannot disconnect from yourself.'}, status=400)

    # 1. Get Requester Node and Type
    requester_node, requester_type = get_node_and_type_by_email(current_user_email)
    if requester_node is None:
        return JsonResponse({'message': 'Remover user not found in graph database or invalid type.'}, status=404)
    if requester_type == 'Error':
        return JsonResponse({'message': 'Multiple graph nodes found for remover email. Data inconsistency.'},
                            status=500)

    # Get Requester Role from Django User (for User nodes)
    requester_role = None
    if requester_type == 'User':
        try:
            django_requester = DjangoUser.objects.get(email=current_user_email)
            requester_role = django_requester.role
        except DjangoUser.DoesNotExist:
            return JsonResponse({'message': 'Remover user found in graph but not in relational DB.'}, status=404)
        except Exception as e:
            return JsonResponse({'message': f'Error getting remover role from relational DB: {str(e)}'}, status=500)

    # 2. Get Target Node and Type
    target_node, target_type = get_node_and_type_by_email(target_email)
    if target_node is None:
        return JsonResponse({'message': 'Target user not found in graph database or invalid type.'}, status=404)
    if target_type == 'Error':
        return JsonResponse({'message': 'Multiple graph nodes found for target email. Data inconsistency.'}, status=500)

    # 3. Manage Relationship
    success, message = manage_relationship(requester_node, requester_type, requester_role, target_node, target_type,
                                           'disconnect')

    if success:
        return JsonResponse({'message': message}, status=200)
    else:
        # Determine appropriate status code based on message
        if "Not " in message:  # "Not connected", "Not employed" etc.
            return JsonResponse({'message': message}, status=404)  # Not Found
        elif "Unsupported" in message or "Cannot" in message or "Only " in message or "not explicitly defined" in message:
            return JsonResponse({'message': message}, status=400)  # Bad Request/Not Implemented
        else:
            return JsonResponse({'message': message}, status=500)
