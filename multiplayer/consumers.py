from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("chat_message", "No message received")
        print("message:", message)
        
        # Send an HTML update that htmx will apply
        await self.send(text_data=json.dumps({
            "message": f'<div>{message}</div>'
        }))