import os
from pyrogram import Client

class Telegram:
    def __init__(self, app_id: str, api_hash: str, workdir: str):
        self.api_id = app_id
        self.api_hash = api_hash
        self.workdir = workdir

    async def check_valid_session(self, session):
        try:
            client = Client(name=session, api_id=self.api_id, api_hash=self.api_hash, workdir=self.workdir)

            if await client.connect():
                return True

            await client.disconnect()
        except:
            return False

        return False

    async def get_accounts(self):
        sessions = self.pars_sessions()
        accounts = await self.check_valid_sessions(sessions)

        if not accounts:
            raise ValueError("Have not valid sessions")
        else:
            return accounts
