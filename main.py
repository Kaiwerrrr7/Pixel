# -*- coding: utf-8 -*-
import asyncio
import hashlib
import random
import time
import urllib.parse
import json

from time import sleep

from rich.console import Console
from datetime import datetime
from api.NotPixel import NotPixel
from core import Protonix, AirdropIds, update_pool
from user_agent import generate_user_agent
from utils.Utils import format_proxy

start_time = time.time()

protonix_core = Protonix()

with open("game_config.json", "r") as file:
    game_config = json.load(file)

def get_formatted_datetime():
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

console = Console()

start_time = time.time()

def format_user_data(user_data):
    user_param = user_data.split('user=')[1].split('&')[0]
    decoded_user_param = urllib.parse.unquote(user_param)
    user_json = json.loads(decoded_user_param)

    return json.dumps(user_json, ensure_ascii=False, indent=2)

def calculate_upgrade_price(level, base_price, increment):
    if level <= 1:
        return 50
    else:
        return base_price + (level - 2) * increment

async def worker_task(account, user_agent, proxies=None):
    hwid = protonix_core.get_hwid()
    worker_name = protonix_core.get_worker_name()
    while True:
        tg_web_data = None
        if "query_id" not in account:
            app_name = account['app_name']
            app_id = account['app_id']
            api_hash = account['api_hash']
            tg_web_data = await protonix_core.get_tg_app_data(
                name=app_name,
                app_id=app_id,
                api_hash=api_hash,
                workdir="sessions/",
                airdrop_bot=AirdropIds.NOT_PIXEL
            )
        else:
            tg_web_data = account['query_id']

        not_pixel = NotPixel(tg_web_data, user_agent, proxies)

        account_info = not_pixel.get_user_info()
        first_name = account_info['firstName']
        balance = account_info['balance']
        console.print(f"{get_formatted_datetime()} logged as {first_name}, {balance} pts!")

        update_pool(hwid, worker_name, "NotPixel", {
            "username": first_name,
            "balance": balance
        })
        account_status = not_pixel.get_status()
        if account_status:
            speedPerSecond = account_status['speedPerSecond']
            maxMiningTime = account_status['maxMiningTime']
            fromStart = account_status['fromStart']

            current_mining = speedPerSecond * fromStart
            max_mining = speedPerSecond * maxMiningTime
            console.print(f"{get_formatted_datetime()}<{first_name}> checking farm...")
            if current_mining >= max_mining:
                console.print(f"{get_formatted_datetime()}<{first_name}> claiming farm...")
                claim_farm = not_pixel.mining_claim()
                if claim_farm:
                    console.print(f"{get_formatted_datetime()}<{first_name}> claim farming success, receive {max_mining} pts!")
                else:
                    console.print(f"{get_formatted_datetime()}<{first_name}> [red]claim farming failed!![/red]")
            
            console.print(f"{get_formatted_datetime()}<{first_name}> checking paint...")
            paint_charges = account_status['charges']
            while paint_charges > 0:
                random_point = random.randint(1, 1000000)
                hex_color = "#{:06x}".format(random.randint(0, 0xFFFFFF)).upper()
                paint = not_pixel.random_paint(random_point, hex_color)
                if paint:
                    console.print(f"{get_formatted_datetime()}<{first_name}> painted color code {hex_color} at point {random_point}.")
                    paint_point = paint['balance']
                    console.print(f"{get_formatted_datetime()}<{first_name}> current points: {paint_point}")
                    paint_charges -= 1
                else:
                    console.print(f"{get_formatted_datetime()}<{first_name}> drawing pixel color failed.")
                    paint_charges = 0

            console.print(f"{get_formatted_datetime()}<{first_name}> checking upgrade...")
            status_boost = account_status['boosts']
            energyLimit = status_boost['energyLimit']
            paintReward = status_boost['paintReward']
            reChargeSpeed = status_boost['reChargeSpeed']
            userBalance = account_status['userBalance']
            if game_config['upgrade_boost']:
                if energyLimit < game_config['energy_limit']:
                    energyLimit_upgrade_price = calculate_upgrade_price(energyLimit, 100, 100)
                    if userBalance >= energyLimit_upgrade_price and not_pixel.upgrade("energyLimit"):
                        console.print(f"{get_formatted_datetime()}<{first_name}> upgraded energyLimit to lv {energyLimit + 1} with {energyLimit_upgrade_price} pts!")
                    
                if paintReward < game_config['paint_reward']:
                    paintReward_upgrade_price = calculate_upgrade_price(paintReward, 100, 100)
                    if userBalance >= paintReward_upgrade_price and not_pixel.upgrade("paintReward"):
                        console.print(f"{get_formatted_datetime()}<{first_name}> upgraded paintReward to lv {paintReward + 1} with {energyLimit_upgrade_price} pts!")
            
                if reChargeSpeed < game_config['recharge_speed']:
                    reChargeSpeed_upgrade_price = calculate_upgrade_price(reChargeSpeed, 100, 100)
                    if userBalance >= reChargeSpeed_upgrade_price and not_pixel.upgrade("reChargeSpeed"):
                        console.print(f"{get_formatted_datetime()}<{first_name}> upgraded reChargeSpeed to lv {reChargeSpeed + 1} with {reChargeSpeed_upgrade_price} pts!")
        
        for i in range(60*45, 0, -1):
            console.print(f"[gray][[/gray][white]{i}[/white][gray]][/gray] [red]waiting delay![/red]",
                            style="bold red", end="\r")
            sleep(1)

if __name__ == "__main__":
    async def main():
        with open("config.json", "r") as file:
            config = json.load(file)
            for account in config['accounts']:
                proxy = None
                if "proxy" in account and account['proxy'] != "":
                    proxy = format_proxy(account['proxy'])
                    proxies = {
                        "http": f"http://{proxy}",
                        "https": f"http://{proxy}"
                    }
                
                user_agent = None
                if "user_agent" in account and account['user_agent'] != "":
                    user_agent = account['user_agent']
                else:
                    user_agent = generate_user_agent(os=("android"))
                if proxy is not None:
                    protonix_core.worker_manager.add_task(worker_task, account, user_agent, proxies)
                else:
                    protonix_core.worker_manager.add_task(worker_task, account, user_agent)
        protonix_core.start_worker()
    asyncio.run(main())