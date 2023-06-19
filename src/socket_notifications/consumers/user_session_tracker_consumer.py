from datetime import datetime, timedelta
import json 
from channels.generic.websocket import AsyncWebsocketConsumer 
import asyncio
from asgiref.sync import async_to_sync
import time
from threading import Timer
import pytz

from api.utils.constants import WHEN_USER_AUTHENTICATED_SESSION_EXPIRES

USER_SESSION_HAS_EXPIRED = "user_session_expired"
CONNECTION_ESTABLISHED = "connection_established"
WAIT_TIME = 600 # 10 Minutes

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

        # --- FOR TESTING, UNCOMMENT THIS PART FOR A SHORTER WAIT
        # expiration_as_date = datetime.now(tz=pytz.UTC) + timedelta(seconds=15)

        self.expiry_task = asyncio.create_task(self.check_expiry(expiration_as_date))

    async def check_expiry(self, expiration_as_date):
        while True:
            current_date_and_time = datetime.now(tz=pytz.UTC)
            if current_date_and_time > expiration_as_date:
                await self.send_auth_notification()
                break
            await asyncio.sleep(WAIT_TIME) 

    async def disconnect(self, close_code):
        if hasattr(self, 'expiry_task'):
            self.expiry_task.cancel()
        await super().disconnect(close_code)
