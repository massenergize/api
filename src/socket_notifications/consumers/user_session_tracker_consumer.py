from datetime import datetime, timedelta
import json 
from channels.generic.websocket import AsyncWebsocketConsumer 
import asyncio
from asgiref.sync import async_to_sync
import time
from threading import Timer

from _main_.utils.common import custom_timezone_info
from api.constants import WHEN_USER_AUTHENTICATED_SESSION_EXPIRES

USER_SESSION_RENEWED = "user_session_renewed"
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

    async def get_expiration_as_date(self): 
        session = self.scope.get("session")
        if not session: return None
        expiration_in_session = session.get(WHEN_USER_AUTHENTICATED_SESSION_EXPIRES)
        in_seconds = expiration_in_session / 1000
        expiration_as_date = datetime.fromtimestamp(in_seconds, tz=custom_timezone_info())
        return expiration_as_date
    
    async def send_auth_notification(self):
        response = {"type": USER_SESSION_HAS_EXPIRED, "message": "User needs to sign in again..."}
        await self.send(json.dumps(response))

    async def track(self):
        expiration_as_date = await self.get_expiration_as_date()
        # If there is ever a situation where the expiration time is not sent through by the frontend 
        # Send a message back to send (There on frontend, admins can be forced to sign in again, if the value is really somehow not available)
        if not expiration_as_date:
            response = {"type": USER_SESSION_HAS_EXPIRED, "message": "Did not receive session expiration time..."}
            await self.send(json.dumps(response))
            return

        # --- UNCOMMENT THIS IF YOU ARE LOCALLY TESTING 
        # --- So that you send a disconnect message to the frontend in 25 seconds
        # expiration_as_date = datetime.now(tz=pytz.UTC) + timedelta(seconds=25)
        # self.expiry_task = asyncio.create_task(self.check_expiry(expiration_as_date, self.send_auth_notification,5))

        # --- COMMENT THIS PART OUT IF YOU ARE LOCALLY TESTING
        self.expiry_task = asyncio.create_task(self.check_expiry(expiration_as_date, self.send_auth_notification))
       
       
    async def check_expiry(self, expiration_as_date, func, wait_time = WAIT_TIME):
        while True:
            current_date_and_time = datetime.now(tz=custom_timezone_info())
            if current_date_and_time > expiration_as_date:
                await func()
                break
            await asyncio.sleep(wait_time) 

    async def receive(self, text_data=None, bytes_data=None):
        message = json.loads(text_data)
        _type = message.get('type', None)
        if _type == USER_SESSION_RENEWED: 
            await self.track()

    async def disconnect(self, close_code):
        if hasattr(self, 'expiry_task'):
            self.expiry_task.cancel()
        await super().disconnect(close_code)
