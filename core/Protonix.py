import configparser
import psutil
from pyrogram import Client
from pyrogram.raw.functions.messages import RequestWebView, RequestAppWebView
from pyrogram.raw.types import InputBotAppShortName
from .worker.WorkerManager import WorkerManager
from .telegram.Telegram import Telegram
from rich.console import Console
from .utils.System import get_hwid
from urllib.parse import unquote


class Protonix:

    def __init__(self) -> None:
        console = Console()
        self.hwid = get_hwid()
        mem = psutil.virtual_memory()
        config = configparser.ConfigParser()
        config.read('PROTONIX.ini')
        max_threads = int(config['system']['MAX_THREADING'])
        max_memory = int(config['system']['MAX_MEMORY'])
        max_cpu = int(config['system']['MAX_CPU'])
        self.single_threading = config['system']['SINGLE_THREADING']
        self.worker_name = config['machine']['WORKER_NAME']
        self.worker_manager = WorkerManager(max_threads, max_memory, max_cpu)

        console.print("[green]*[/green] TELEGRAM       [green]@harrycayairdrop[/green]")
        console.print("[green]*[/green] ABOUT          [blue]Protonix/Core 1.0-alpha[/blue]")
        console.print(f"[green]*[/green] MEMORY         [blue]{mem}%[/blue]")
        console.print(f"[green]*[/green] DASHBOARD      [blue]dash.aurateam.org[/blue] {self.hwid} {self.worker_name}")

    def get_worker_name(self):
        return self.worker_name
    
    def is_single_threading(self):
        return int(self.single_threading) == 1

    def get_hwid(self):
        return self.hwid

    def start_worker(self):
        try:
            self.worker_manager.start_threads()
            self.worker_manager.wait_for_completion()
        except KeyboardInterrupt:
            print("KeyboardInterrupt received. Stopping...")
            self.worker_manager.stop_event.set()
            for thread in self.worker_manager.threads:
                thread.join()
            print("Threads have been stopped.")

    async def get_tg_app_data(self, name: str, app_id: str, api_hash: str, workdir: str, airdrop_bot: object):
        client = Client(
            name=name,
            api_id=app_id,
            api_hash=api_hash,
            workdir=workdir
        )
        telegram = Telegram(app_id=app_id, api_hash=api_hash, workdir=workdir)
        is_session = await telegram.check_valid_session(session=name)
        if not is_session:
            async with client:
                await client.get_me()

        try:
            await client.connect()
            if airdrop_bot['app_web_view']:
                bot = await client.resolve_peer(airdrop_bot['username'])
                app = InputBotAppShortName(bot_id=bot, short_name=airdrop_bot['short_name'])
                web_view = await client.invoke(RequestAppWebView(
                    peer=bot,
                    app=app,
                    write_allowed=True,
                    platform='android'
                ))
            else:
                web_view = await client.invoke(RequestWebView(
                    peer=await client.resolve_peer(airdrop_bot['username']),
                    bot=await client.resolve_peer(airdrop_bot['username']),
                    from_bot_menu=False,
                    platform='android',
                    url=airdrop_bot['site']
                ))

            if web_view is None:
                return None

            auth_url = web_view.url
            await client.disconnect()

            return unquote(auth_url.split('tgWebAppData=', maxsplit=1)[1].split('&tgWebAppVersion', maxsplit=1)[0])
        except:
            pass
