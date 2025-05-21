from django.db import models
from django.utils.translation import gettext_lazy as _
from messenger.mixins import IDMixin, TimestampMixin


class User(IDMixin, TimestampMixin):
    username = models.CharField(max_length=150, unique=True)
    password_hash = models.CharField(max_length=255)
    public_key = models.TextField()

    class Meta:
        db_table = '"messenger_encrypted"."user"'
        verbose_name = _("user")

    def __str__(self):
        return self.username


class Chat(IDMixin, TimestampMixin):
    CHAT_TYPES = (
        ("private", "Private"),
        ("group", "Group"),
    )
    name = models.CharField(max_length=255)
    chat_type = models.CharField(max_length=10, choices=CHAT_TYPES)

    class Meta:
        db_table = '"messenger_encrypted"."chat"'
        verbose_name = _("chat")

    def __str__(self):
        return self.name


class ChatParticipant(IDMixin, TimestampMixin):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    left_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = '"messenger_encrypted"."chat_participant"'
        verbose_name = _("chat_participant")


class Message(IDMixin, TimestampMixin):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    encrypted_payload = models.BinaryField()

    class Meta:
        db_table = '"messenger_encrypted"."message"'
        verbose_name = _("message")

    def __str__(self):
        return f"Message {self.id} in chat {self.chat.id}"


class MessageRead(IDMixin, TimestampMixin):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="reads")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = '"messenger_encrypted"."message_read"'
        verbose_name = _("message_read")
        unique_together = ("message", "user")
