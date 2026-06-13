from django.db import models
from django.contrib.auth.models import User


class ChatSession(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="chats",
        null=True,
        blank=True
    )

    title = models.CharField(
        max_length=200
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.title


class Message(models.Model):

    chat = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    user_message = models.TextField()

    bot_response = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.user_message[:50]


class UploadedFile(models.Model):

    chat = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE
    )

    file = models.FileField(
        upload_to="uploads/"
    )

    extracted_text = models.TextField(
        blank=True,
        null=True
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    extracted_text = models.TextField(
    blank=True,
    default=""
    )

    def __str__(self):

        return self.file.name