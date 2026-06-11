from django.shortcuts import render
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def home(request):

    user_message = ""
    bot_response = ""

    if request.method == "POST":

        user_message = request.POST.get("message")

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )

        bot_response = response.choices[0].message.content

    return render(
        request,
        "chat/home.html",
        {
            "user_message": user_message,
            "bot_response": bot_response
        }
    )