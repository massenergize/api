from datetime import datetime, timedelta
import json 
from channels.generic.websocket import AsyncWebsocketConsumer 
import asyncio
from asgiref.sync import async_to_sync
import time
from threading import Timer
import pytz

from api.utils.constants import WHEN_USER_AUTHENTICATED_SESSION_EXPIRES

USER_SESSION_ALMOST_EXPIRED = "user_session_almost_expired"
USER_SESSION_HAS_EXPIRED = "user_session_expired"
CONNECTION_ESTABLISHED = "connection_established"
WAIT_TIME = 660 # 11 Minutes

class UserSessionTrackerConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({
            "type": CONNECTION_ESTABLISHED,
            "message": "It's safe, send a gift!"
        }))

        await self.track()

    async def send_auth_notification(self):
        response = {"type": USER_SESSION_HAS_EXPIRED, "message": "User needs to sign in again..."}
        await self.send(json.dumps(response))

    async def almost_expired(self):
        response = {"type": USER_SESSION_ALMOST_EXPIRED, "message": "User session expires in 10 minutes..."}
        await self.send(json.dumps(response))
        await self.count_down_to_expiration()

    
    async def count_down_to_expiration(self): 
        ten_minutes_expiration = datetime.now(tz=pytz.UTC) + timedelta(minutes=10)
        # --- FOR TESTING, UNCOMMENT THIS ----
        # ten_minutes_expiration = datetime.now(tz=pytz.UTC) + timedelta(minutes=1) # COMMENT OUT BEFORE PR (BPR)
        self.expiry_task = asyncio.create_task(self.check_expiry(ten_minutes_expiration, self.send_auth_notification,60))


    async def track(self):
        session = self.scope.get("session")
        expiration_in_session = session.get(WHEN_USER_AUTHENTICATED_SESSION_EXPIRES)

        # If there is ever a situation where the expiration time is not sent through by the frontend 
        # Send a message back to send (There on frontend, admins can be forced to sign in again, if the value is really somehow not available)
        if not expiration_in_session:
            response = {"type": USER_SESSION_HAS_EXPIRED, "message": "Did not receive session expiration time..."}
            await self.send(json.dumps(response))
            return

        in_seconds = expiration_in_session / 1000
        expiration_as_date = datetime.fromtimestamp(in_seconds, tz=pytz.UTC)
        expiration_as_date = expiration_as_date - timedelta(minutes=10)
        self.expiry_task = asyncio.create_task(self.check_expiry(expiration_as_date, self.almost_expired))


        # --- FOR TESTING, UNCOMMENT THIS PART FOR A SHORTER WAIT
        # expiration_as_date = datetime.now(tz=pytz.UTC) + timedelta(seconds=25)
        # self.expiry_task = asyncio.create_task(self.check_expiry(expiration_as_date, self.almost_expired,5)) # COMMENT OUT BEFORE PR (BPR)

       
    async def check_expiry(self, expiration_as_date, func, wait_time = WAIT_TIME):
        while True:
            current_date_and_time = datetime.now(tz=pytz.UTC)
            if current_date_and_time > expiration_as_date:
                await func()
                break
            await asyncio.sleep(wait_time) 

    async def disconnect(self, close_code):
        if hasattr(self, 'expiry_task'):
            self.expiry_task.cancel()
        await super().disconnect(close_code)
