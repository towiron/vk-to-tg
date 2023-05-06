import os

from aiogram import Bot
from config_data.config import Config, load_config

config: Config = load_config()

TG_TOKEN = config.tg_bot.token
bot = Bot(TG_TOKEN, parse_mode='HTML')


async def send_text(text: str, chat_id: str):
    max_message_length = 4096
    if len(text) <= max_message_length:
        await bot.send_message(chat_id, text, disable_web_page_preview=True)
    else:
        while text:
            if len(text) <= max_message_length:
                await bot.send_message(chat_id, text)
                break
            else:
                chunk = text[:max_message_length]
                last_space = chunk.rfind(" ")
                if last_space == -1:
                    last_space = max_message_length
                await bot.send_message(chat_id, text[:last_space], disable_web_page_preview=True)
                text = text[last_space + 1:]


async def send_photos(chat_id, text, media_photo, downloaded_files):
    if text and len(text) < 1024:
        media_photo[0].caption = text
        await bot.send_media_group(chat_id, media=media_photo)
        await delete_temp(downloaded_files=downloaded_files)

    elif text and len(text) > 1024:
        max_caption_length = 1024
        caption = text[:max_caption_length]
        last_space_index = caption.rfind(' ')
        caption = caption[:last_space_index]
        media_photo[0].caption = caption
        await bot.send_media_group(chat_id, media=media_photo)
        await delete_temp(downloaded_files=downloaded_files)
        await send_text(text=text[last_space_index + 1:], chat_id=chat_id)

    else:
        await bot.send_media_group(chat_id, media=media_photo)
        await delete_temp(downloaded_files=downloaded_files)


async def delete_temp(downloaded_files):
    for file_name in downloaded_files:
        file_path = os.path.join('download_temp', file_name)
        if os.path.exists(file_path):
            os.remove(file_path)


async def send_file(chat_id, media_file, text, downloaded_files):
    if text and len(text) < 1024:
        media_file[0].caption = text
        await bot.send_media_group(chat_id, media=media_file)
        await delete_temp(downloaded_files=downloaded_files)

    elif text and len(text) > 1024:
        max_caption_length = 1024
        caption = text[:max_caption_length]
        last_space_index = caption.rfind(' ')
        caption = caption[:last_space_index]
        media_file[0].caption = caption
        await bot.send_media_group(chat_id, media=media_file)
        await delete_temp(downloaded_files=downloaded_files)
        await send_text(text=text[last_space_index + 1:], chat_id=chat_id)

    else:
        await bot.send_media_group(chat_id, media=media_file)
        await delete_temp(downloaded_files=downloaded_files)


async def send_location(coordinates, chat_id):
    latitude = coordinates[0]
    longitude = coordinates[1]
    await bot.send_location(chat_id=chat_id, latitude=latitude, longitude=longitude)


async def send_poll(question, options, multiple, chat_id):
    await bot.send_poll(chat_id=chat_id,
                        question=question,
                        options=options,
                        allows_multiple_answers=multiple)


async def send_link(title, description, url, post_link, photo_link, chat_id, downloaded_link):
    message = f'<b>{title}</b>\n\n{description}\n\n<a href="{url}">Читать</a>'
    message += f"\n\n📌<a href='{post_link}'>ВК пост</a>"
    photo_link[0].caption = message
    if photo_link:
        await bot.send_media_group(chat_id=chat_id,
                                   media=photo_link)
    else:
        message = f'<b>{title}</b>\n\n{description}\n\n<a href="{url}">Читать</a>'
        await bot.send_message(chat_id=chat_id,
                               text=message,
                               parse_mode='HTML')
    await delete_temp(downloaded_files=downloaded_link)
