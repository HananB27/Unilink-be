import json
import traceback
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from .models import Message

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.other_user = self.scope["url_route"]["kwargs"]["username"]

        # Build a consistent room name using both usernames
        self.room_name = f"{min(self.user.username, self.other_user)}__{max(self.user.username, self.other_user)}"
        self.room_group_name = f"chat_{self.room_name}"

        print(f"🔌 [CONNECT] {self.user} connecting to room {self.room_group_name}")

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        print(f"❌ [DISCONNECT] {self.user} left {self.room_group_name}")
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        try:
            if not self.user.is_authenticated:
                print("⚠️  Unauthenticated user tried to send a message.")
                await self.send(text_data=json.dumps({"error": "Unauthenticated"}))
                await self.close()
                return

            if not text_data:
                await self.send(text_data=json.dumps({"error": "No text data received"}))
                return

            data = json.loads(text_data)
            message = data.get("message", "").strip()

            if not message:
                await self.send(text_data=json.dumps({"error": "Empty message"}))
                return

            sender = await sync_to_async(User.objects.get)(id=self.user.id)
            receiver = await sync_to_async(User.objects.get)(username=self.other_user)

            await sync_to_async(Message.objects.create)(
                sender=sender,
                receiver=receiver,
                content=message
            )

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "sender": sender.username,
                }
            )
        except ObjectDoesNotExist as e:
            await self.send(text_data=json.dumps({"error": "User not found."}))
            print(f"❌ [DB ERROR] User not found: {e}")
            await self.close()
        except Exception as e:
            await self.send(text_data=json.dumps({"error": "Internal server error"}))
            print("❌ [UNHANDLED ERROR] in receive():")
            traceback.print_exc()
            await self.close()

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"]
        }))
