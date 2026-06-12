from django.shortcuts import render, redirect
from groq import Groq
from dotenv import load_dotenv
from .models import Message, ChatSession
import os
import markdown
from django.http import JsonResponse

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def home(request, chat_id=None):

    # Open selected chat
    if chat_id:
        chat = ChatSession.objects.get(id=chat_id)
    else:
        chat = ChatSession.objects.first()

        if not chat:
            chat = ChatSession.objects.create(
                title="New Chat"
            )

    if request.method == "POST":

        user_message = request.POST.get("message")

        # Auto title from first message
        if chat.title == "New Chat":
            chat.title = user_message[:30]
            chat.save()

        # Build conversation memory
        conversation = []

        previous_messages = Message.objects.filter(
            chat=chat
        ).order_by("-created_at")[:10]

        for msg in reversed(previous_messages):

            conversation.append({
                "role": "user",
                "content": msg.user_message
            })

            conversation.append({
                "role": "assistant",
                "content": msg.bot_response
            })

        conversation.append({
            "role": "user",
            "content": user_message
        })

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=conversation
        )

        raw_response = response.choices[0].message.content

        Message.objects.create(
            chat=chat,
            user_message=user_message,
            bot_response=raw_response
        )

        return redirect(
            "chat",
            chat_id=chat.id
        )

    messages = Message.objects.filter(
        chat=chat
    ).order_by("created_at")

    return render(
        request,
        "chat/home.html",
        {
            "messages": messages,
            "chat": chat,
            "chats": ChatSession.objects.all().order_by("-created_at")
        }
    )


def new_chat(request):

    chat = ChatSession.objects.create(
        title="New Chat"
    )

    return redirect(
        "chat",
        chat_id=chat.id
    )


def delete_chat(request, chat_id):

    chat = ChatSession.objects.get(
        id=chat_id
    )

    chat.delete()

    return redirect("home")

def send_message(request, chat_id):

    if request.method == "POST":

        chat = ChatSession.objects.get(id=chat_id)

        user_message = request.POST.get("message")

        conversation = []

        previous_messages = Message.objects.filter(
            chat=chat
        ).order_by("-created_at")[:10]

        for msg in reversed(previous_messages):

            conversation.append({
                "role": "user",
                "content": msg.user_message
            })

            conversation.append({
                "role": "assistant",
                "content": msg.bot_response
            })

        conversation.append({
            "role": "user",
            "content": user_message
        })

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=conversation
        )

        bot_response = response.choices[0].message.content

        Message.objects.create(
            chat=chat,
            user_message=user_message,
            bot_response=bot_response
        )

        return JsonResponse({
            "user_message": user_message,
            "bot_response": bot_response
        })

    return JsonResponse({
        "error": "Invalid request"
    })