from django.shortcuts import render, redirect
from groq import Groq
from dotenv import load_dotenv
from .models import (
    Message,
    ChatSession,
    UploadedFile
)
import os
import markdown
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import get_object_or_404
import fitz
from .forms import RegisterForm


def register(request):

    if request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("login")

    else:
        form = RegisterForm()

    return render(
        request,
        "registration/register.html",
        {"form":form}
    )

load_dotenv()

def get_groq_client():
    return Groq(
        api_key=os.getenv("GROQ_API_KEY")
    )
client = get_groq_client()
@login_required
def home(request, chat_id=None):

    # Open selected chat
    if chat_id:
        chat = ChatSession.objects.get(
    id=chat_id,
    user=request.user
)
    else:
        chat = ChatSession.objects.filter(
    user=request.user
).first()

        if not chat:
            chat = ChatSession.objects.create(
            user=request.user,
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
            "chats": ChatSession.objects.filter(
    user=request.user
).order_by("-created_at")
        }
    )


@login_required
def new_chat(request):

    chat = ChatSession.objects.create(
    user=request.user,
    title="New Chat"
)

    return redirect(
        "chat",
        chat_id=chat.id
    )


@login_required
def delete_chat(request, chat_id):


    

    chat = ChatSession.objects.get(
    id=chat_id,
    user=request.user
)

    chat.delete()

    return redirect("home")

@login_required
def rename_chat(request, chat_id):

    chat = ChatSession.objects.get(
        id=chat_id,
        user=request.user
    )

    if request.method == "POST":

        new_title = request.POST.get("title")

        if new_title:
            chat.title = new_title

            chat.save()

    return redirect(
        "chat",
        chat_id=chat.id
    )

@login_required
def send_message(request, chat_id):

    if request.method == "POST":

        chat = ChatSession.objects.get(
    id=chat_id,
    user=request.user
)

        user_message = request.POST.get("message")
        uploaded_file = request.FILES.get("file")
        print("FILE RECEIVED:", uploaded_file)

        pdf_text = ""
        latest_pdf = UploadedFile.objects.filter(
            chat=chat
        ).order_by("-uploaded_at").first()

        if latest_pdf and latest_pdf.extracted_text:

            pdf_text = latest_pdf.extracted_text







        if uploaded_file:

            saved_file = UploadedFile.objects.create(
                chat=chat,
                file=uploaded_file
            )

            if uploaded_file.name.endswith(".pdf"):

                pdf_path = saved_file.file.path

                pdf_document = fitz.open(pdf_path)

                for page in pdf_document:

                    pdf_text += page.get_text()

                pdf_document.close()

                saved_file.extracted_text = pdf_text[:50000]

                saved_file.save()

            if uploaded_file.name.endswith(".pdf"):

                pdf_path = saved_file.file.path

                pdf_document = fitz.open(pdf_path)

                for page in pdf_document:

                    pdf_text += page.get_text()

                pdf_document.close()

                saved_file.extracted_text = pdf_text[:50000]
                saved_file.save()

        if pdf_text and not user_message:

            user_message = (
                "Summarize this PDF "
                "and explain the key concepts."
            )

        if chat.title == "New Chat" and user_message:

            words = user_message.split()

            chat.title = " ".join(words[:5])

            chat.save()

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


    if pdf_text:

        conversation.append({
            "role": "user",
            "content":
            f"""
            PDF CONTENT:

            {pdf_text[:15000]}

            USER QUESTION:

            {user_message}
            """
        })

    else:

        conversation.append({
            "role": "user",
            "content": user_message
        })

        try:

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=conversation
            )

            bot_response = (
                response.choices[0]
                .message.content
            )

        except Exception as e:

            print("Groq Error:", e)

            error_text = str(e).lower()

            if "rate limit" in error_text:

                bot_response = (
                    "⚠️ ChatGPT Jr AI limit reached. "
                    "Please try again later."
                )

            else:

                bot_response = (
                    "⚠️ ChatGPT Jr encountered an error. "
                    "Please try again."
                )

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

