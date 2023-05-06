from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import default_state
from aiogram.filters import Command, CommandStart, StateFilter, Text

from lexicon.lexicon_ru import LEXICON_RU
from keyboards.keyboards import start_kb, forward_start_kb, forward_stop_kb
from database.database import collection_users
from services.services import get_group_name, get_telegram_channel_name
from .create_link_handlers import process_fill_link_command

router: Router = Router()


@router.message(CommandStart(), StateFilter(default_state))
async def proccess_start_command(message: Message):
    await message.answer(text=LEXICON_RU['/start'],
                         reply_markup=start_kb())


@router.message(Command(commands=['help']), StateFilter(default_state))
async def proccess_help_command(message: Message):
    await message.answer(text=LEXICON_RU['/help'],
                         reply_markup=start_kb())


@router.message(Text(text=['Моя свзяь'], ignore_case=True), StateFilter(default_state))
async def process_showdata_command(message: Message):
    user_data = collection_users.find_one({"user_id": message.from_user.id})
    if user_data:
        status = '🟢Запущен' if user_data['forwarding'] else '🔴Остановлен'
        await message.answer(
            text=f'📢Ваша связь:\n'
                 f'Название группы ВК: {await get_group_name(user_data["vk_group_id"])}\n'
                 f'Название ТГ канала: {await get_telegram_channel_name(user_data["tg_channel_id"])}\n'
                 f'Состояние: {status}',
            reply_markup=forward_stop_kb() if user_data['forwarding'] else forward_start_kb())
    else:
        await message.answer(text=LEXICON_RU['no_data'],
                             parse_mode='HTML')


@router.callback_query(Text(text=['update_link', 'delete_link']))
async def process_forwarding(callback: CallbackQuery, state: FSMContext):
    if callback.data == 'update_link':
        await callback.message.edit_text('Заполните новую форму')
        message = callback.message
        await process_fill_link_command(message, state)
    elif callback.data == 'delete_link':
        collection_users.delete_one({'user_id': callback.from_user.id})
        await callback.message.edit_text(text='Ваша связь успешно удалена!')
        await callback.message.answer('Если хотите создат новую свзяь, нажмите на кнопку <b>Создать связь</b>',
                                      parse_mode='HTML',
                                      reply_markup=start_kb())


@router.callback_query(Text(text=['forward_start', 'forward_stop']))
async def process_forwarding(callback: CallbackQuery):
    user_data = collection_users.find_one({"user_id": callback.from_user.id})
    if callback.data == 'forward_start':
        start_thread(user_id=user_data['user_id'],
                     vk_group_id=user_data['vk_group_id'],
                     tg_channel_id=user_data['tg_channel_id'])
        collection_users.update_one(
            {"user_id": callback.from_user.id},
            {"$set": {'forwarding': True}}
        )
        if user_data:
            await callback.message.edit_text(
                text=
                f'📢Ваша связь:\n'
                f'Название группы ВК: {await get_group_name(user_data["vk_group_id"])}\n'
                f'Название ТГ канала: {await get_telegram_channel_name(user_data["tg_channel_id"])}\n'
                f'Состояние(Изменилось): 🟢Запущен')
            await callback.answer()
    elif callback.data == 'forward_stop':
        # stop_thread(user_data['user_id'])
        collection_users.update_one(
            {"user_id": callback.from_user.id},
            {"$set": {'forwarding': False}}
        )
        if user_data:
            await callback.message.edit_text(
                text=
                f'📢Ваша связь:\n'
                f'Название группы ВК: {await get_group_name(user_data["vk_group_id"])}\n'
                f'Название ТГ канала: {await get_telegram_channel_name(user_data["tg_channel_id"])}\n'
                f'Состояние(Изменилось): 🔴Остановлен')
