import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from db.graph.graph_models import University, Department
from utils.embeddings import embed_text
from .models import Universities, Departments


# Create your views here.
@csrf_exempt
def create_university(request):
    if request.method == 'POST':
        try:

            name = request.POST.get('name')
            location = request.POST.get('location')
            profile_picture = request.FILES.get('profile_picture')

            if not name or not location or not profile_picture:
                return JsonResponse({'error':'missing name or location or profile_picture'}, status=400)

            try:
                University(name=name, location=location, profile_picture=profile_picture).save()
            except Exception as graph_error:
                return JsonResponse({'error': f'Neo4j error: {str(graph_error)}'}, status=500)

            university = Universities.objects.create(
                    name=name,
                    location=location,
                    profile_picture=profile_picture
                )

            text = f"{name} located in {location}"
            embedding_vector = embed_text(text)

            if embedding_vector:
                university.embedding = embedding_vector
                university.save(update_fields=["embedding"])

            profile_picture = request.build_absolute_uri(university.profile_picture) if university.profile_picture else None

            return JsonResponse({
                'id': university.id,
                'name': university.name,
                'location': university.location,
                'profile_picture': profile_picture
            }, status=201)

        except Exception as e:
            return JsonResponse({'error':str(e)}, status=500)
    return JsonResponse({'error':'invalid request'}, status=400)

@csrf_exempt
def get_universities(request):
    try:
        if request.method == 'GET':
            universities = Universities.objects.all().values('id', 'name', 'location', 'profile_picture')
            return JsonResponse({'universities':list(universities)}, status=200)
        return JsonResponse({'error':'invalid request'}, status=400)
    except Exception as e:
        return JsonResponse({'error':str(e)}, status=500)

@csrf_exempt
def delete_university(request, university_id):
    try:
        university = Universities.objects.get(id=university_id)
        uniGraph=University.nodes.get(name=university.name)

        for department in Department.nodes.filter():
            if department.belongs_to.is_connected(uniGraph):
                department.delete()

        if uniGraph:
            uniGraph.delete()
        else:
            return JsonResponse({'error':'university not found'}, status=404)


        university.delete()
        return JsonResponse({'success': True}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def edit_university(request, university_id):
    try:
        university = Universities.objects.get(id=university_id)

        new_name = request.POST.get('name')
        new_location = request.POST.get('location')
        new_profile_picture = request.FILES.get('profile_picture')

        profile_picture = request.build_absolute_uri(new_profile_picture) if new_profile_picture else None

        if new_name:
            university.name = new_name
        if new_location:
            university.location = new_location
        if new_profile_picture:
            university.profile_picture = profile_picture
        university.save()

        uniGraph=University.nodes.get(name=university.name)

        if uniGraph:
            if new_name:
                uniGraph.name = new_name
            if new_location:
                uniGraph.location = new_location
            if new_profile_picture:
                uniGraph.profile_picture = profile_picture
            uniGraph.save()
        return JsonResponse({'success': True}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def get_university(request, university_id):
    try:
        if request.method == 'GET':
            university = Universities.objects.get(id=university_id)
            profile_picture = request.build_absolute_uri(university.profile_picture) if university.profile_picture else None

            data = {
                'id': university.id,
                'name': university.name,
                'location': university.location,
                'profile_picture': profile_picture
            }
            return JsonResponse({'university': data}, status=200)
        return JsonResponse({'error':'invalid request'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def create_department(request):
    try:
        if request.method == 'POST':
            name = request.POST.get('name')
            university_id = request.POST.get('university_id')
            profile_picture = request.FILES.get('profile_picture')

            if not name or not university_id or not profile_picture:
                return JsonResponse({'error':'invalid request'}, status=400)

            university = Universities.objects.get(id=university_id)
            uniGraph = University.nodes.get(name=university.name)

            depGraph = Department(name=name, profile_picture=profile_picture).save()
            depGraph.belongs_to.connect(uniGraph)

            department = Departments.objects.create(
                name=name,
                university=university,
                profile_picture=profile_picture
            )

            profile_picture_url = request.build_absolute_uri(department.profile_picture.url) if department.profile_picture else None

            return JsonResponse({
                'id': department.id,
                'name': department.name,
                'university': university.name,
                'profile_picture': profile_picture_url
            }, status=201)

        return JsonResponse({'error':'invalid request'}, status=400)
    except Exception as e:
        return JsonResponse({'error':str(e)}, status=500)