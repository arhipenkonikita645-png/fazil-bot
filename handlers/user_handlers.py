from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import Database
from keyboards import *
from config import ADMIN_USERNAME

router = Router()
db = Database()

class PaymentStates(StatesGroup):
    waiting_confirmation = State()

@router.message(Command("start"))
async def cmd_start(message: Message):
    db.add_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    
    welcome_text = (
        "Добро пожаловать! Этот бот предоставляет доступ к закрытому каналу Фазиля. "
        "Для покупки доступа нажмите кнопку 'Купить доступ'."
    )
    
    await message.answer(welcome_text, reply_markup=get_main_keyboard())

@router.message(F.text == "🛒 Купить доступ")
async def show_products(message: Message):
    products = db.get_active_products()
    
    if not products:
        await message.answer("В настоящее время нет доступных товаров.")
        return
    
    await message.answer("Выберите товар:", reply_markup=get_products_keyboard(products))

@router.callback_query(F.data.startswith("product_"))
async def show_product_details(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    product = db.get_product(product_id)
    
    if not product:
        await callback.answer("Товар не найден")
        return
    
    product_text = (
        f"{product[1]}\n\n"
        f"{product[2] or 'Описание отсутствует'}\n\n"
        f"Цена: {product[3]} руб.\n\n"
        f"Реквизиты для оплаты:\n{product[4]}"
    )
    
    if product[5]:  # Если есть фото реквизитов
        await callback.message.answer_photo(
            product[5],
            caption=product_text,
            reply_markup=get_product_actions_keyboard()
        )
    else:
        await callback.message.answer(
            product_text,
            reply_markup=get_product_actions_keyboard()
        )
    
    await callback.answer()

@router.callback_query(F.data == "back_to_products")
async def back_to_products(callback: CallbackQuery):
    products = db.get_active_products()
    
    if not products:
        await callback.message.answer("В настоящее время нет доступных товаров.")
        return
    
    await callback.message.answer("Выберите товар:", reply_markup=get_products_keyboard(products))
    await callback.answer()

@router.callback_query(F.data == "confirm_payment")
async def confirm_payment(callback: CallbackQuery, state: FSMContext):
    # Получаем информацию о последнем просмотренном товаре
    # Для этого нужно хранить состояние последнего товара
    # Временно будем использовать первый активный товар
    
    products = db.get_active_products()
    if not products:
        await callback.answer("Нет доступных товаров")
        return
    
    # Берем первый товар (в реальном боте нужно хранить выбранный товар)
    product = products[0]
    product_id = product[0]
    product_name = product[1]
    price = product[3]
    
    # Создаем заявку
    order_id = db.create_order(callback.from_user.id, product_id)
    
    admin_username = db.get_setting('admin_username_for_contact') or ADMIN_USERNAME
    
    instruction_text = (
        f"✅ Ваша заявка #{order_id} принята!\n\n"
        f"Для подтверждения оплаты свяжитесь с администратором: {admin_username}\n\n"
        f"Не забудьте указать:\n"
        f"• Номер заявки: #{order_id}\n"
        f"• Ваш username: @{callback.from_user.username or 'не указан'}\n"
        f"• Товар: {product_name}\n"
        f"• Сумма: {price} руб."
    )
    
    await callback.message.answer(instruction_text)
    
    # Отправка уведомления администратору
    main_admin_id = db.get_setting('main_admin_id')
    if main_admin_id:
        try:
            from bot import bot
            notification_text = (
                f"🆕 Новая заявка на доступ!\n\n"
                f"Заявка: #{order_id}\n"
                f"Пользователь: @{callback.from_user.username} ({callback.from_user.id})\n"
                f"Товар: {product_name}\n"
                f"Сумма: {price} руб.\n"
                f"Время: {callback.message.date.strftime('%d.%m.%Y %H:%M')}\n\n"
                f"Статус: ⏳ Ожидает подтверждения"
            )
            await bot.send_message(int(main_admin_id), notification_text)
        except Exception as e:
            print(f"Не удалось отправить уведомление администратору: {e}")
    
    await callback.answer()