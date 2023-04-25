import json 
from channels.generic.websocket import AsyncWebsocketConsumer 
import asyncio
from asgiref.sync import async_to_sync
import time
class UserSessionTrackerConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept() 
        # headers = self.scope["headers"]
       
        await self.send(text_data=json.dumps({
            "type":"le_connection_established", 
            "message":"The connection is established!"
           
        }))
        

    async def receive(self, text_data=None, bytes_data=None):
        return await super().receive(text_data, bytes_data)
       

 

    # async def disconnect(self, close_code):
    #     print("this shit disconncted meerhn!!!!!")
       