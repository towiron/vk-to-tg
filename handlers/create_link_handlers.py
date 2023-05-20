from aiogram import Router
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.filters import StateFilter, Text
from aiogram.types import Message, CallbackQuery

from lexicon.lexicon_ru import LEXICON_RU
from keyboards.keyboards import start_kb, cancel_kb, forward_kb
from services.services import get_vk_id

from database.database import collection_users
from services.vk_services import start_checking_group

router: Router = Router()

user_dict: dict[int, dict[str, str | bool]] = {}


class CreateLink(StatesGroup):
    fill_vk_id = State()
    fill_tg_id = State()


@router.message(Text(text=['Отмена'], ignore_case=True), StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(text=LEXICON_RU['cancel_error'],
                         parse_mode='HTML',
                         reply_markup=start_kb())


@router.message(Text(text=['Отмена'], ignore_case=True), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(text=LEXICON_RU['cancel'],
                         reply_markup=start_kb())
    await state.clear()


@router.message(Text(text=['Создать свзяь'], ignore_case=True), StateFilter(default_state))
async def process_fill_link_command(message: Message, state: FSMContext):
    user_data = {'user_id': message.from_user.id}
    if not collection_users.find_one(user_data):
        collection_users.insert_one(user_data)
    await message.answer(text=LEXICON_RU['create_vk'],
                         parse_mode='HTML',
                         reply_markup=cancel_kb())
    await state.set_state(CreateLink.fill_vk_id)


@router.message(StateFilter(CreateLink.fill_vk_id))
async def process_fill_vk(message: Message, state: FSMContext):
    vk_group_id = await get_vk_id(message)
    if vk_group_id:
        collection_users.update_one({'user_id': message.from_user.id},
                                    {'$set': {'vk_group_id': vk_group_id}})
        await state.update_data(vk_group_id=vk_group_id)
        await message.answer(text=LEXICON_RU['create_tg'],
                             parse_mode='HTML',
                             reply_markup=cancel_kb())
        await state.set_state(CreateLink.fill_tg_id)
    else:
        await message.answer(text=LEXICON_RU['error_vk_link'])


@router.message(StateFilter(CreateLink.fill_tg_id))
async def process_fill_tg(message: Message, state: FSMContext):
    if message.forward_from_chat is not None:
        tg_channel_id = message.forward_from_chat.id
        await state.update_data(tg_channel_id=tg_channel_id)
        user_dict[message.from_user.id] = await state.get_data()
        user_data = collection_users.find_one({"user_id": message.from_user.id})
        if user_data:
            collection_users.update_one(
                {"user_id": message.from_user.id},
                {"$set": {'tg_channel_id': tg_channel_id,
                          'forwarding': False}}
            )
        await state.clear()
        await message.answer(text=LEXICON_RU['congratulations'],
                             parse_mode='HTML',
                             )
        await message.answer(text=LEXICON_RU['start_forward'],
                             reply_markup=forward_kb())
    else:
        await message.answer(text=LEXICON_RU['error_tg_forward'])


@router.callback_query(Text(text=['yes_forwarding', 'no_forwarding']))
async def process_forwarding(callback: CallbackQuery):
    if callback.data == 'yes_forwarding':
        collection_users.update_one(
            {"user_id": callback.from_user.id},
            {"$set": {'forwarding': True}}
        )
        await callback.message.edit_text(text='Репост запущен!')
        user_data = collection_users.find_one({"user_id": callback.from_user.id})
        await start_checking_group(user_id=user_data['user_id'],
                                   vk_group_id=user_data['vk_group_id'],
                                   tg_channel_id=user_data['tg_channel_id'])
        await callback.message.answer(text=LEXICON_RU['my_relations'],
                                      reply_markup=start_kb(),
                                      parse_mode='HTML')
    else:
        await callback.message.edit_text(text='Репост отключен!')
        await callback.message.answer(text=LEXICON_RU['my_relations'],
                                      reply_markup=start_kb(),
                                      parse_mode='HTML')


@router.callback_query(Text(text=['yes_forwarding', 'no_forwarding']))
async def process_forwarding(callback: CallbackQuery):
    if callback.data == 'yes_forwarding':
        collection_users.update_one(
            {"user_id": callback.from_user.id},
            {"$set": {'forwarding': True}}
        )
        await callback.message.edit_text(text='Репост запущен!')
        user_data = collection_users.find_one({"user_id": callback.from_user.id})
        await start_checking_group(user_id=user_data['user_id'],
                                   vk_group_id=user_data['vk_group_id'],
                                   tg_channel_id=user_data['tg_channel_id'])
        await callback.message.answer(text=LEXICON_RU['my_relations'],
                                      reply_markup=start_kb(),
                                      parse_mode='HTML')
    else:
        await callback.message.edit_text(text='Репост отключен!')
        await callback.message.answer(text=LEXICON_RU['my_relations'],
                                      reply_markup=start_kb(),
                                      parse_mode='HTML')