from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage

class UserForm(StatesGroup):
    FIO = State()

class Form(StatesGroup):
    FIO = State()
    sum_ = State()
    date = State()
    payment_type = State()
    is_correct_message_id = State()
    
class NonCashForm(Form):
    check_photo = State()
    FIO = State()
    sum_ = State()
    date = State()
    payment_type = State()