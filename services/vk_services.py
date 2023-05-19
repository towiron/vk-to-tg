import asyncio
import os

import aiohttp
import requests
from aiogram import Bot, types
from aiogram.types import FSInputFile
from vk_api import VkApi

from pymongo.collection import Collection
from config_data.config import Config, load_config
from services.send_post import send_text, send_location, send_poll, send_link, send_photos, send_file

config: Config = load_config()
VK_ACCESS_TOKEN = config.vk_access.token
TG_TOKEN = config.tg_bot.token
bot = Bot(TG_TOKEN)

data = []


async def start_checking_group(user_id, vk_group_id, tg_channel_id):
    new_dict = {'user_id': user_id, 'vk_group_id': vk_group_id, 'tg_channel_id': tg_channel_id}
    data.append(new_dict)
    print(f'Запуск: {data}')
    asyncio.create_task(check_group_for_new_post(new_dict))


def load_collection(collection: Collection):
    count = collection.count_documents({})
    if count > 0:
        for user in collection.find({'forwarding': True}):
            user_id = user['user_id']
            vk_group_id = user['vk_group_id']
            tg_channel_id = user['tg_channel_id']
            asyncio.create_task(start_checking_group(user_id, vk_group_id, tg_channel_id))
    else:
        print('База пуста')


async def stop_checking_group(user_id):
    print(f'остановить {data}')
    for d in data:
        if d['user_id'] == user_id:
            d['stop'] = True
            data.remove(d)
            break


async def check_group_for_new_post(d):
    vk_session = VkApi(token=VK_ACCESS_TOKEN)
    vk = vk_session.get_api()
    try:
        while True:
            if d.get('stop', False):
                break
            if d not in data:
                break
            long_poll = vk.groups.getLongPollServer(group_id=d['vk_group_id'])
            server, key, ts = long_poll['server'], long_poll['key'], long_poll['ts']
            connector = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(f'{server}?act=a_check&key={key}&ts={ts}&wait=25') as response:
                    response_json = await response.json()
                    updates = response_json.get('updates', [])
                    await check_updates(updates=updates, chat_id=d['tg_channel_id'])
    except Exception as e:
        print(e)



async def check_updates(updates, chat_id):
    for update in updates:
        if update['type'] == 'wall_post_new':
            post_link = f"https://vk.com/wall{update['object']['owner_id']}_{update['object']['id']}"
            text = ''
            if update['object']['text']:
                text += update['object']['text'] + '\n'
            attachments = update['object'].get('attachments', [])
            if attachments:
                media_photo = []
                media_file = []
                downloaded_photo = []
                downloaded_file = []
                for attachment in attachments:
                    if attachment['type'] == 'photo':
                        max_size = None
                        max_height = -1
                        for size in attachment['photo']['sizes']:
                            if size['height'] > max_height:
                                max_size = size
                                max_height = size['height']
                        photo_url = max_size['url']
                        photo_response = requests.get(photo_url)
                        if photo_response.status_code == 200:
                            file_extension = os.path.splitext(photo_url)[-1]
                            file_name = f"{update['object']['date']}_{update['object']['id']}_{attachment['photo']['id']}{file_extension}"
                            file_name = file_name.split('?')[0]
                            downloaded_photo.append(file_name)
                            file_path = os.path.join('download_temp', file_name)
                            with open(file_path, 'wb') as f:
                                f.write(photo_response.content)
                            media_photo.append(types.InputMediaPhoto(media=FSInputFile(file_path)))
                    elif attachment['type'] == 'doc':
                        doc_url = attachment['doc']['url']
                        doc_response = requests.get(doc_url)
                        if doc_response.status_code == 200:
                            file_extension = os.path.splitext(doc_url)[-1]
                            file_name = f"{update['object']['date']}_{update['object']['id']}_{attachment['doc']['id']}{file_extension}"
                            file_name = file_name.split('?')[0]
                            downloaded_file.append(file_name)
                            doc_name = attachment['doc']['title']
                            file_path = os.path.join('download_temp', file_name)
                            with open(file_path, 'wb') as f:
                                f.write(doc_response.content)
                            media_file.append(types.InputMediaDocument(media=FSInputFile(file_path, filename=doc_name)))
                    elif attachment['type'] == 'geo':
                        coordinates = str(attachment['geo']['coordinates']).split()
                        if text:
                            text += f"📌<a href='{post_link}'>ВК пост</a>"
                            await send_text(text=text, chat_id=chat_id)
                            await send_location(coordinates=coordinates, chat_id=chat_id)
                            text = ''
                        else:
                            await send_location(coordinates=coordinates, chat_id=chat_id)
                    elif attachment['type'] == 'poll':
                        question = str(attachment['poll']['question'])
                        options = []
                        for option in attachment['poll']['answers']:
                            options.append(str(option['text']))
                        multiple = str(attachment['poll']['multiple'])
                        if text:
                            text += f"📌<a href='{post_link}'>ВК пост</a>"
                            await send_text(text=text, chat_id=chat_id)
                            await send_poll(question=question, options=options, chat_id=chat_id, multiple=multiple)
                            text = ''
                        else:
                            await send_poll(question=question, options=options, chat_id=chat_id, multiple=multiple)

                    elif attachment['type'] == 'link':
                        photo_link = []
                        downloaded_link = []
                        url = attachment['link']['url']
                        title = attachment['link']['title']
                        description = attachment['link']['description']
                        if 'photo' in attachment['link']:
                            photo_url = attachment['link']['photo']['sizes'][-1]['url']
                            photo_response = requests.get(photo_url)
                            if photo_response.status_code == 200:
                                file_extension = os.path.splitext(photo_url)[-1]
                                # print(attachment)
                                file_name = f"{update['object']['date']}_{update['object']['id']}_{attachment['link']['photo']['id']}{file_extension}"
                                file_name = file_name.split('?')[0]
                                downloaded_link.append(file_name)
                                file_path = os.path.join('download_temp', file_name)
                                with open(file_path, 'wb') as f:
                                    f.write(photo_response.content)
                                print(file_path)
                                photo_link.append(types.InputMediaPhoto(type='photo', media=FSInputFile(file_path)))
                        await send_link(title=title,
                                        description=description,
                                        url=url,
                                        post_link=post_link,
                                        photo_link=photo_link,
                                        downloaded_link=downloaded_link,
                                        chat_id=chat_id)

                if len(media_photo) > 0 and len(media_file) > 0:
                    text += f"📌<a href='{post_link}'>ВК пост</a>"
                    await send_photos(chat_id=chat_id, text=text, media_photo=media_photo,
                                      downloaded_files=downloaded_photo)
                    await send_file(chat_id=chat_id, text='', media_file=media_file, downloaded_files=downloaded_file)
                else:
                    text += f"📌<a href='{post_link}'>ВК пост</a>"
                    if len(media_photo) > 0:
                        await send_photos(chat_id=chat_id, text=text, media_photo=media_photo,
                                          downloaded_files=downloaded_photo)
                    if len(media_file) > 0:
                        await send_file(chat_id=chat_id, text=text, media_file=media_file,
                                        downloaded_files=downloaded_file)
            else:
                text += f"📌<a href='{post_link}'>ВК пост</a>"
                await send_text(chat_id=chat_id, text=text)
