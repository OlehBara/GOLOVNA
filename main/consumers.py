import json

from django.contrib.auth import get_user_model

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import ChatMessage

User = get_user_model()


class SupportChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close()
            return

        self.user = user
        self.user_group_name = f"support_user_{self.user.id}"

        await self.channel_layer.group_add(self.user_group_name, self.channel_name)
        if self.user.is_staff:
            await self.channel_layer.group_add("admin_support", self.channel_name)

        await self.accept()

        # Надсилаємо історію останніх повідомлень при підключенні
        if self.user.is_staff:
            history = await self._get_admin_history(limit=50)
        else:
            history = await self._get_user_history(user_id=self.user.id, limit=30)

        for msg in history:
            payload = self._serialize_message(msg)
            await self.send(text_data=json.dumps(payload))

    async def disconnect(self, close_code):
        if getattr(self, "user", None) and self.user.is_authenticated:
            await self.channel_layer.group_discard(
                self.user_group_name, self.channel_name
            )
            if self.user.is_staff:
                await self.channel_layer.group_discard(
                    "admin_support", self.channel_name
                )

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return

        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        message = (data.get("message") or "").strip()
        if not message:
            return

        target_user_id = data.get("target_user_id")

        if self.user.is_staff:
            if not target_user_id:
                return
            chat_user = await self._get_user(target_user_id)
            if not chat_user:
                return
            is_admin_reply = True
        else:
            chat_user = self.user
            is_admin_reply = False

        chat_message = await self._create_message(
            sender=self.user,
            chat_user=chat_user,
            message=message,
            is_admin_reply=is_admin_reply,
        )

        payload = self._serialize_message(chat_message)

        if self.user.is_staff:
            await self.channel_layer.group_send(
                f"support_user_{chat_user.id}",
                {"type": "chat.message", "payload": payload},
            )
            await self.channel_layer.group_send(
                "admin_support",
                {"type": "chat.message", "payload": payload},
            )
        else:
            await self.channel_layer.group_send(
                self.user_group_name,
                {"type": "chat.message", "payload": payload},
            )
            await self.channel_layer.group_send(
                "admin_support",
                {"type": "chat.message", "payload": payload},
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event["payload"]))

    def _serialize_message(self, chat_message: ChatMessage):
        return {
            "id": chat_message.id,
            "message": chat_message.message,
            "sender_id": chat_message.sender_id,
            "sender_username": chat_message.sender.username,
            "is_admin_reply": chat_message.is_admin_reply,
            "chat_user_id": chat_message.chat_user_id,
            "chat_user_username": chat_message.chat_user.username,
            "timestamp": chat_message.timestamp.isoformat(),
        }

    @database_sync_to_async
    def _get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def _create_message(self, sender, chat_user, message, is_admin_reply):
        return ChatMessage.objects.create(
            sender=sender,
            chat_user=chat_user,
            message=message,
            is_admin_reply=is_admin_reply,
        )

    @database_sync_to_async
    def _get_user_history(self, user_id: int, limit: int = 30):
        qs = (
            ChatMessage.objects.filter(chat_user_id=user_id)
            .select_related("sender", "chat_user")
            .order_by("-timestamp")[:limit]
        )
        return list(reversed(list(qs)))

    @database_sync_to_async
    def _get_admin_history(self, limit: int = 50):
        qs = (
            ChatMessage.objects.all()
            .select_related("sender", "chat_user")
            .order_by("-timestamp")[:limit]
        )
        return list(reversed(list(qs)))
