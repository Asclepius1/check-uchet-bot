import os
from datetime import datetime

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery


from app.users import UserData
from app.states import Form, NonCashForm, UserForm
from app.services import upload_to_google_sheet, extract_texts_from_photo
from app.keyboards import inline_buttons_pay_type, inlune_buttons_agreement


os.makedirs('temp', exist_ok=True)
router = Router()
users = UserData()
@router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    """
    This handler receives messages with `/start` command
    """
    user_id = message.from_user.id 
    users.get_user(user_id)
    if not users.get_user(user_id):
        await state.set_state(UserForm.FIO)
        await message.answer(f"Отправьте ваше ФИО полностью!")
    else:
        await message.answer(f"Выберите тип оплаты!", reply_markup=inline_buttons_pay_type)


@router.message(UserForm.FIO)
async def process_user_fio(message: Message, state: FSMContext):
    fio = message.text
    user_id = message.from_user.id 
    users.add_user(user_id, fio)
    await message.answer(f"Спасибо, {fio}!\nВыберите тип оплаты!", reply_markup=inline_buttons_pay_type)


@router.callback_query(F.data == "cash")
async def process_cash_type(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Form.FIO)
    await callback.answer("Вы выбрали оплату наличными!")
    await callback.message.answer("Отправьте ФИО полностью!")


@router.message(Form.FIO)
async def process_fio(message: Message, state: FSMContext):
    await state.update_data(fio=message.text)
    await state.set_state(Form.sum_)
    await message.answer("Отправьте сумму чека (только цифры)")

@router.message(Form.sum_)
async def process_cash_sum(message: Message, state: FSMContext):
    await state.update_data(sum_=message.text, date=datetime.now().strftime("%d.%m.%Y"), payment_type='Наличные')
    data = await state.get_data()
    is_correct_message = await message.answer("Проверьте правильность введенных данных:\n"
                         f"ФИО: {data['fio']}\n"
                         f"Сумма: {data['sum_']}\n"
                        #  f"Дата: {datetime.now().strftime('%d.%m.%Y')}\n"
                         f"Тип оплаты: Наличные", reply_markup=inlune_buttons_agreement)
    await state.update_data(is_correct_message_id=is_correct_message.message_id)

@router.callback_query(F.data == "non_cash")
async def process_non_cash_type(callback: CallbackQuery, state: FSMContext):
    await state.set_state(NonCashForm.check_photo)
    await callback.answer("Вы выбрали оплату без наличными")
    await callback.message.answer("Отправьте Фото чека!")

@router.message(F.photo, NonCashForm.check_photo)
async def process_check_photo(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id        
    unic_file_name = f"temp/{photo_id}.jpg"
    await message.bot.download(photo_id, destination=unic_file_name)
    await state.update_data(check_photo_path=unic_file_name)
    await state.set_state(NonCashForm.FIO)
    await message.answer(f"Отправьте ФИО полностью!")

@router.message(NonCashForm.FIO)
async def process_fio_non_cash(message: Message, state: FSMContext):
    await state.update_data(fio=message.text)
    data = await state.get_data()
    await message.answer(f"Обрабатываю...")
    result_data = await extract_texts_from_photo(data['check_photo_path'])
    result_data['fio'] = data['fio']
    result_data['user'] = users.get_user(message.from_user.id)['FIO']
    await upload_to_google_sheet(result_data)
    await message.answer(f"Данные получены!")

@router.callback_query(F.data == "correct", Form.sum_)
async def process_agreement_correct(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await callback.bot.delete_message(callback.from_user.id, data['is_correct_message_id'])
    await callback.answer(f"Обрабатываю...")
    data['user'] = users.get_user(callback.from_user.id)['FIO']
    await upload_to_google_sheet(data)
    await callback.message.answer(f"Данные получены!")

@router.callback_query(F.data == "not_correct", Form.sum_)
async def process_agreement_correct(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await callback.bot.delete_message(callback.from_user.id, data['is_correct_message_id'])
    await callback.answer(f"Давайте начнем заново!")
    await state.clear()
    await callback.message.answer(f"Выберите тип оплаты!", reply_markup=inline_buttons_pay_type)