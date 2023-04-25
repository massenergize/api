import json 
from channels.generic.websocket import AsyncWebsocketConsumer 
import asyncio
from asgiref.sync import async_to_sync
import time
class UserSessionTrackerConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept() 
       
        await self.send(text_data=json.dumps({
            "type":"CONNECTION_ESTABLISHED", 
            "message":"Its safe, send gift!"
           
        }))
        

    async def receive(self, text_data=None, bytes_data=None):
        # return await super().receive(text_data, bytes_data)
       
        gift = json.loads(text_data)
        token = gift.get("token", None)
        print("TOKEN HERE",token )
       

 

    # async def disconnect(self, close_code):
    #     print("this shit disconncted meerhn!!!!!")
       