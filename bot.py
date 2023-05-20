import asyncio
import logging

from aiogram import Bot, Dispatcher
from utils.mongo import MongoStorage

from config_data.config import Config, load_config
from handlers import other_handlers, user_handlers, create_link_handlers

from services.vk_services import load_collection
from database.database import collection_users

# Инициализируем логгер
logger = logging.getLogger(__name__)


# Функция конфигурирования и запуска бота
async def main():
    # Конфигурируем логирование
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')

    storage = MongoStorage(uri="mongodb://localhost:27017/",
                                 database='vktotg',
                                 collection_states='sessions'
                                 )

    # Загружаем конфиг в переменную config
    config: Config = load_config()

    # Инициализируем бот и диспетчер
    bot: Bot = Bot(token=config.tg_bot.token,
                   parse_mode='HTML')
    dp: Dispatcher = Dispatcher(storage=storage)

    # Регистриуем роутеры в диспетчере
    dp.include_router(create_link_handlers.router)
    dp.include_router(user_handlers.router)
    dp.include_router(other_handlers.router)

    load_collection(collection_users)
    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
