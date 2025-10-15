from aiogram import Bot
from aiogram.types import BotCommand, InlineKeyboardMarkup, InlineKeyboardButton

# Buttons and commands
COMMANDS: dict[str, str] = {
    '/start': 'Запустить бота',
}

async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(
            command=command,
            description=description
        ) for command, description in COMMANDS.items()
    ]
    await bot.set_my_commands(main_menu_commands)

inline_buttons_pay_type = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Безналичные", callback_data="non_cash")],
        [InlineKeyboardButton(text="Наличные", callback_data="cash")],
    ])

inlune_buttons_agreement = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Корректно", callback_data="correct")],
        [InlineKeyboardButton(text="Не корректно", callback_data="not_correct")],
    ]) 