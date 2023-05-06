import re
import requests
from aiogram import Bot
from aiogram.types import Chat

from config_data.config import Config, load_config

config: Config = load_config()

# print(config.vk_access.token)

VK_ACCESS_TOKEN = config.vk_access.token
BOT_TOKEN = config.tg_bot.token


async def is_vk_group_url(url):
    pattern = r'^https?://(m\.)?vk\.com/([\w\d\.\-]+)$'
    if re.match(pattern, url):
        return True
    else:
        return False


async def get_vk_id(message):
    if await is_vk_group_url(url=message.text):
        url = "https://api.vk.com/method/utils.resolveScreenName"
        screen_name = message.text.split("/")[-1]
        params = {
            "screen_name": screen_name,
            "access_token": VK_ACCESS_TOKEN,
            "v": "5.131"
        }
        response = requests.get(url, params=params)
        response_json = response.json()
        if "response" in response_json:
            if response_json["response"]["type"] in ["group", "page"]:
                vk_group_id = str(response_json["response"]["object_id"])
                return vk_group_id

            else:
                return False
    else:
        return False


async def get_group_name(vk_group_id: str) -> str:
    url = f"https://api.vk.com/method/groups.getById?group_id={vk_group_id}&access_token={VK_ACCESS_TOKEN}&v=5.131"
    response = requests.get(url).json()
    group_name = response["response"][0]["name"]
    return group_name


async def get_telegram_channel_name(channel_id):
    response = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getChat', params={'chat_id': channel_id})
    data = response.json()
    if data['ok']:
        return data['result']['title']
    else:
        return None
