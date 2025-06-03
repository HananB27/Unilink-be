import os
from django.http import JsonResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import connection

import google.generativeai as genai
from utils.embeddings import embed_text
from apps.posts.models import Tags, Posts
from apps.users.models import Users
from apps.universities.models import Universities

genai.configure(api_key=os.environ["GENAI_API_KEY"])

def get_similar_posts(query_text, top_n=5):
    embedding = embed_text(query_text)
    if not embedding:
        return []
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, title, content
            FROM posts
            ORDER BY embedding <-> (%s::vector)
            LIMIT %s
        """, [embedding, top_n])
        rows = cursor.fetchall()
    return [{'id': r[0], 'title': r[1], 'content': r[2]} for r in rows]

def handle_factual_queries(user_input: str) -> str | None:
    query = user_input.lower()

    if "tag" in query and ("how many" in query or "list" in query or "what" in query or "show" in query):
        tags = list(Tags.objects.values_list("name", flat=True).distinct())
        if not tags:
            return "There are currently no tags in the system."
        tag_list = ", ".join(tags)
        return f"There are {len(tags)} unique tags:\n{tag_list}"

    if "user" in query and ("how many" in query or "number of" in query):
        count = Users.objects.count()
        return f"There are currently {count} registered users."

    if ("university" in query or "universities" in query) and ("list" in query or "what" in query or "show" in query):

        names = list(Universities.objects.values_list("name", flat=True))
        if not names:
            return "There are no universities registered."
        return "Here are all the universities:\n" + "\n".join(f"- {n}" for n in names)

    if "popular" in query or "trending post" in query:
        posts = Posts.objects.order_by("-created_at")[:5]
        if not posts:
            return "There are no posts yet."
        return "Here are some popular posts:\n" + "\n".join(f"- {p.title}" for p in posts)

    if "active user" in query or "most active" in query:
        users = Users.objects.order_by("-created_at")[:5]
        if not users:
            return "No users found."
        return "Here are some of the most active users:\n" + "\n".join(f"- {u.username}" for u in users)

    if "suggest tag" in query:
        return "To suggest tags, please provide your post content."

    return None

@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def chat_with_bot(request):
    if request.data.get("clear"):
        request.session["chat_history"] = []
        return JsonResponse({"response": "Conversation history cleared."})

    user_input = request.data.get("message", "").strip()
    if not user_input:
        return JsonResponse({"error": "Empty input"}, status=400)

    # Get history
    history = request.data.get("chat_history", [])
    request.session["chat_history"] = history  # store latest history

    # Handle factual queries
    factual_response = handle_factual_queries(user_input)
    if factual_response:
        return JsonResponse({"response": factual_response})

    # Handle rewriting
    if "rewrite this post" in user_input.lower():
        original = request.data.get("post_content", "")
        if not original:
            return JsonResponse({"response": "Please provide 'post_content' for rewriting."})
        prompt = f"""Rewrite the following student post to be more formal and professional:\n\n{original}"""
    else:
        related_posts = get_similar_posts(user_input)
        context_text = "\n".join([f"- {p['title']}: {p['content']}" for p in related_posts])
        history_prompt = "\n".join(
            f"{m['sender']}: {m['message']}" for m in history[-10:]
        )
        prompt = f"""You are a helpful assistant for a student social network called Unilink.

Conversation so far:
{history_prompt}

New question:
"{user_input}"

Relevant posts:
{context_text}

Please respond appropriately."""

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return JsonResponse({"response": response.text})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
