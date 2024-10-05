import random
from telethon.sync import TelegramClient, functions
import requests
import os
import time
import config
import threading
import urllib3
from urllib.parse import unquote
import asyncio  # Added asyncio import

class Colors:
    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    BROWN = "\033[0;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    LIGHT_GRAY = "\033[0;37m"
    DARK_GRAY = "\033[1;30m"
    LIGHT_RED = "\033[1;31m"
    LIGHT_GREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    LIGHT_BLUE = "\033[1;34m"
    LIGHT_PURPLE = "\033[1;35m"
    LIGHT_CYAN = "\033[1;36m"
    LIGHT_WHITE = "\033[1;37m"
    END = "\033[0m"

def get_rgb_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return f"\033[38;2;{r};{g};{b}m"

def print_colored_log(message):
    color = get_rgb_color()
    print(f"{color}{message}{Colors.END}")

async def GetWebAppData(client):
    notcoin = await client.get_entity("notpixel")
    msg = await client(functions.messages.RequestWebViewRequest(notcoin, notcoin, platform="android", url="https://notpx.app/"))
    webappdata_global = msg.url.split('https://notpx.app/#tgWebAppData=')[1].replace("%3D", "=").split('&tgWebAppVersion=')[0].replace("%26", "&")
    user_data = webappdata_global.split("&user=")[1].split("&auth")[0]
    webappdata_global = webappdata_global.replace(user_data, unquote(user_data))
    return webappdata_global

class NotPx:
    UpgradePaintReward = {
        2: {"Price": 5},
        3: {"Price": 100},
        4: {"Price": 200},
        5: {"Price": 300},
        6: {"Price": 500},
        7: {"Price": 600, "Max": 1}
    }

    UpgradeReChargeSpeed = {
        2: {"Price": 5},
        3: {"Price": 100},
        4: {"Price": 200},
        5: {"Price": 300},
        6: {"Price": 400},
        7: {"Price": 500},
        8: {"Price": 600},
        9: {"Price": 700},
        10: {"Price": 800},
        11: {"Price": 900, "Max": 1}
    }
    
    UpgradeEnergyLimit = {
        2: {"Price": 5},
        3: {"Price": 100},
        4: {"Price": 200},
        5: {"Price": 300},
        6: {"Price": 400, "Max": 1}
    }

    def __init__(self, session_name: str) -> None:
        self.session = requests.Session()
        self.session_name = session_name
        self.__update_headers()

    def __update_headers(self):
        client = TelegramClient(self.session_name, config.API_ID, config.API_HASH).start()
        WebAppQuery = client.loop.run_until_complete(GetWebAppData(client))
        client.disconnect()
        self.session.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Authorization': f'initData {WebAppQuery}',
            'Priority': 'u=1, i',
            'Referer': 'https://notpx.app/',
            'Sec-Ch-Ua': 'Chromium;v=119, Not?A_Brand;v=24',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': 'Linux',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.105 Safari/537.36',
        }

    def request(self, method, end_point, key_check, data=None):
        try:
            if method == "get":
                response = self.session.get(f"https://notpx.app/api/v1{end_point}", timeout=5)
            else:
                response = self.session.post(f"https://notpx.app/api/v1{end_point}", timeout=5, json=data)
            
            if "failed to parse" in response.text:
                print_colored_log(f"NotPixel internal error. Wait 5 minutes...")
                time.sleep(5 * 60)
            elif response.status_code == 200:
                if key_check in response.text:
                    return response.json()
                else:
                    raise Exception(report_bug_text.format(response.text))
            elif response.status_code >= 500:
                time.sleep(5)
            else:
                nloop = asyncio.new_event_loop()
                asyncio.set_event_loop(nloop)
                client = TelegramClient(self.session_name, config.API_ID, config.API_HASH, loop=nloop).start()
                WebAppQuery = nloop.run_until_complete(GetWebAppData(client))
                client.disconnect()
                self.session.headers.update({
                    "Authorization": "initData " + WebAppQuery
                })
                print_colored_log("soft bot !! Reconek ulang !!")
                time.sleep(2)
        
        except requests.exceptions.ConnectionError:
            print_colored_log(f"ConnectionError {end_point}. tunggu  5 detik")
            time.sleep(5)
        except urllib3.exceptions.NewConnectionError:
            print_colored_log(f"NewConnectionError {end_point}. tunggu  5 detik")
            time.sleep(5)
        except requests.exceptions.Timeout:
            print_colored_log(f"Timeout Error {end_point}. tunggu  5 detik")
            time.sleep(5)
        
        return self.request(method, end_point, key_check, data)

    def claim_mining(self):
        return self.request("get","/mining/claim","claimed")['claimed']

    def accountStatus(self):
        return self.request("get","/mining/status","speedPerSecond")

    def autoPaintPixel(self):
        colors = [ "#FFFFFF" , "#000000" , "#00CC78" , "#BE0039" ]
        random_pixel = (random.randint(100,990) * 1000) + random.randint(100,990)
        data = {"pixelId":random_pixel,"newColor":random.choice(colors)}
        return self.request("post","/repaint/start","balance",data)['balance']
    
    def paintPixel(self, x, y, hex_color):
        pixelformated = (y * 1000) + x + 1
        data = {"pixelId":pixelformated,"newColor":hex_color}
        return self.request("post","/repaint/start","balance",data)['balance']

    def upgrade_paintreward(self):
        return self.request("get","/mining/boost/check/paintReward","paintReward")['paintReward']
    
    def upgrade_energyLimit(self):
        return self.request("get","/mining/boost/check/energyLimit","energyLimit")['energyLimit']
    
    def upgrade_reChargeSpeed(self):
        return self.request("get","/mining/boost/check/reChargeSpeed","reChargeSpeed")['reChargeSpeed']

# Function to display a banner only once
def show_success_banner():
    print(f"{Colors.YELLOW}")
    print("===============================================")
    print(f"""

 ██████╗██████╗ ██╗   ██╗██████╗ ████████╗ ██████╗ 
██╔════╝██╔══██╗╚██╗ ██╔╝██╔══██╗╚══██╔══╝██╔═══██╗
██║     ██████╔╝ ╚████╔╝ ██████╔╝   ██║   ██║   ██║
██║     ██╔══██╗  ╚██╔╝  ██╔═══╝    ██║   ██║   ██║
╚██████╗██║  ██║   ██║   ██║        ██║   ╚██████╔╝
 ╚═════╝╚═╝  ╚═╝   ╚═╝   ╚═╝        ╚═╝    ╚═════╝ 
    ██████╗  ██████╗ ██████╗ ██╗ █████╗            
    ██╔══██╗██╔═══██╗██╔══██╗██║██╔══██╗           
    ██████╔╝██║   ██║██████╔╝██║███████║           
    ██╔═══╝ ██║   ██║██╔══██╗██║██╔══██║           
    ██║     ╚██████╔╝██║  ██║██║██║  ██║           
    ╚═╝      ╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝           
    """)
    print(f"{Colors.END}")
    print("===============================================")
    print(f"{Colors.GREEN}")
    print("    NOT PIXEL BOT")
    print("    MENGGUNAKAN BOT BERESIKO AKUN BANNED !!!")
    print("==> Link telegram: https://t.me/cryptoporia")
    print(f"{Colors.END}")
    print("===============================================")

# Existing function to detect account and print information
def detect_account_and_print(NotPxClient):
    user_status = NotPxClient.accountStatus()

    if user_status:
        account_name = user_status.get('firstname', os.path.basename(NotPxClient.session_name))
        balance = user_status.get('userBalance', 'N/A')
        league = user_status.get('league', 'N/A')
        energy_limit = user_status['boosts'].get('energyLimit', 'N/A') + 1
        paint_reward = user_status['boosts'].get('paintReward', 'N/A') + 1
        recharge_speed = user_status['boosts'].get('reChargeSpeed', 'N/A') + 1

        # Print account details for every login
        print_colored_log(f"Account: [ {account_name} ]")
        print_colored_log(f"Balance: [ {balance} ]")
        print_colored_log(f"Pangkat: [ {league} ]")
        print_colored_log(f"Level Energy: [ {energy_limit} ]")
        print_colored_log(f"Level Reward: [ {paint_reward} ]")
        print_colored_log(f"Level Speed: [ {recharge_speed} ]")
    else:
        print_colored_log("Failed to retrieve account data.")

def painter(NotPxClient: NotPx, account_name: str):
    print_colored_log("<==> Mulai mewarnai <==>.")
    while True:
        try:
            user_status = NotPxClient.accountStatus()
            if not user_status:
                time.sleep(5)
                continue
            else:
                charges = user_status['charges']
                levels_recharge = user_status['boosts']['reChargeSpeed'] + 1
                levels_paintreward = user_status['boosts']['paintReward'] + 1
                levels_energylimit = user_status['boosts']['energyLimit'] + 1
                user_balance = user_status['userBalance']

            if levels_recharge - 1 < config.RE_CHARGE_SPEED_MAX and NotPx.UpgradeReChargeSpeed[levels_recharge]['Price'] <= user_balance:
                status = NotPxClient.upgrade_reChargeSpeed()
                print_colored_log(f"ReChargeSpeed Upgrade to level {levels_recharge} result: {status}")
                user_balance -= NotPx.UpgradeReChargeSpeed[levels_recharge]['Price']

            if levels_paintreward - 1 < config.PAINT_REWARD_MAX and NotPx.UpgradePaintReward[levels_paintreward]['Price'] <= user_balance:
                status = NotPxClient.upgrade_paintreward()
                print_colored_log(f"PaintReward Upgrade to level {levels_paintreward} result: {status}")
                user_balance -= NotPx.UpgradePaintReward[levels_paintreward]['Price']

            if levels_energylimit - 1 < config.ENERGY_LIMIT_MAX and NotPx.UpgradeEnergyLimit[levels_energylimit]['Price'] <= user_balance:
                status = NotPxClient.upgrade_energyLimit()
                print_colored_log(f"EnergyLimit Upgrade to level {levels_energylimit} result: {status}")
                user_balance -= NotPx.UpgradeEnergyLimit[levels_energylimit]['Price']
                
            if charges > 0:
                for _ in range(charges):
                    balance = NotPxClient.autoPaintPixel()
                    print_colored_log(f"{account_name}: 1 pixel Sukses, Saldo baru: [ {balance:.10f} ]")
                    t = random.randint(1,6)
                    print_colored_log(f" {account_name} soft bot: jeda {t}")
                    time.sleep(t)
            else:
                print_colored_log(f"{account_name}: Tiket habis. tunggu 10 menit")
                time.sleep(600)
        except requests.exceptions.ConnectionError:
            print_colored_log(f"{account_name}: ConnectionError. jeda 5s...")
            time.sleep(5)
        except urllib3.exceptions.NewConnectionError:
            print_colored_log(f"{account_name}: NewConnectionError. jeda for 5s...")
            time.sleep(5)
        except requests.exceptions.Timeout:
            print_colored_log(f"{account_name}: Timeout Error. Sleeping for 5s...")
            time.sleep(5)

def mine_claimer(NotPxClient: NotPx, account_name: str):
    time.sleep(5)

    print_colored_log("Bot di mulai !!!")
    while True:
        acc_data = NotPxClient.accountStatus()
        
        if acc_data is None:
            print_colored_log(f"{account_name}: Failed to retrieve account status. Retrying...")
            time.sleep(5)
            continue
        
        if 'fromStart' in acc_data and 'speedPerSecond' in acc_data:
            fromStart = acc_data['fromStart']
            speedPerSecond = acc_data['speedPerSecond']
            if fromStart * speedPerSecond > 0.3:
                claimed_count = round(NotPxClient.claim_mining(), 2)
                print_colored_log(f"{account_name}: NotPx Token claimed.")
        else:
            print_colored_log(f"{account_name}: Unexpected account data format. Retrying...")
        
        for remaining in range(3600, 0, -1):
            mins, secs = divmod(remaining, 60)
            timer = f"{mins:02}:{secs:02}"
            print(f"{account_name}: Ngopi Dulu ☕☕ {timer}", end="\r")
            time.sleep(1)
        print(f"{account_name}: Waktu ngopi selesai !!!")

# Modified function to show banner once before login
def multithread_starter():
    dirs = os.listdir("sessions/")
    sessions = list(filter(lambda x: x.endswith(".session"), dirs))
    sessions = list(map(lambda x: x.split(".session")[0], sessions))

    for session_name in sessions:
        try:
            cli = NotPx("sessions/" + session_name)
            account_name = cli.accountStatus().get('firstname', os.path.basename(session_name))

            # Always display the account information for each account
            detect_account_and_print(cli)

            threading.Thread(target=painter, args=[cli, account_name]).start()
            threading.Thread(target=mine_claimer, args=[cli, account_name]).start()
        except Exception as e:
            print_colored_log(f"Error on load session \"{session_name}\", error: {e}")

if __name__ == "__main__":
    if not os.path.exists("sessions"):
        os.mkdir("sessions")

    # Display banner before options
    show_success_banner()

    while True:
        option = input("Pilih 1 untuk add akun dan 2 untuk mulai Bot: ")
        if option == "1":
            name = input("\nEnter Session name: ")
            if not any(name in i for i in os.listdir("sessions/")):
                client = TelegramClient("sessions/" + name, config.API_ID, config.API_HASH).start()
                client.disconnect()
                print_colored_log(f"akun {name} sukses di simpan.")
            else:
                print_colored_log(f"akun {name} sudah ada.")
        elif option == "2":
            multithread_starter()
            break

