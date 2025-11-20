from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ContentType
from datetime import datetime

from database import Database
from keyboards import *
from config import ADMIN_IDS

db = Database()

class AddProductStates(StatesGroup):
    waiting_name = State()
    waiting_description = State()
    waiting_price = State()
    waiting_payment = State()

class EditProductStates(StatesGroup):
    waiting_name = State()
    waiting_description = State()
    waiting_price = State()
    waiting_payment = State()

class SettingsStates(StatesGroup):
    waiting_admin_id = State()
    waiting_admin_username = State()

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

def register_handlers(dp: Dispatcher):
    @dp.message_handler(commands=["admin"])
    async def cmd_admin(message: types.Message):
        if not is_admin(message.from_user.id):
            await message.answer("У вас нет доступа к админ-панели.")
            return
        
        await message.answer("Админ-панель", reply_markup=get_admin_keyboard())

    @dp.message_handler(lambda message: message.text == "🚪 Выйти из админки")
    async def exit_admin(message: types.Message):
        await message.answer("Вы вышли из админ-панели.", reply_markup=get_main_keyboard())

    @dp.message_handler(lambda message: message.text == "➕ Добавить товар")
    async def add_product_start(message: types.Message):
        if not is_admin(message.from_user.id):
            return
        
        await message.answer("Введите название товара:")
        await AddProductStates.waiting_name.set()

    @dp.message_handler(state=AddProductStates.waiting_name)
    async def process_product_name(message: types.Message, state: FSMContext):
        await state.update_data(name=message.text)
        await message.answer("Введите описание товара (необязательно, отправьте '-' чтобы пропустить):")
        await AddProductStates.waiting_description.set()

    @dp.message_handler(state=AddProductStates.waiting_description)
    async def process_product_description(message: types.Message, state: FSMContext):
        description = message.text if message.text != '-' else None
        await state.update_data(description=description)
        await message.answer("Введите цену в рублях (только число):")
        await AddProductStates.waiting_price.set()

    @dp.message_handler(state=AddProductStates.waiting_price)
    async def process_product_price(message: types.Message, state: FSMContext):
        try:
            price = int(message.text)
            await state.update_data(price=price)
            await message.answer("Отправьте реквизиты для оплаты (текст или фото):")
            await AddProductStates.waiting_payment.set()
        except ValueError:
            await message.answer("Пожалуйста, введите корректное число:")

    @dp.message_handler(state=AddProductStates.waiting_payment, content_types=ContentType.ANY)
    async def process_product_payment(message: types.Message, state: FSMContext):
        data = await state.get_data()
        
        payment_details = None
        payment_photo = None
        
        if message.content_type == ContentType.TEXT:
            payment_details = message.text
        elif message.content_type == ContentType.PHOTO:
            payment_photo = message.photo[-1].file_id
            payment_details = "Реквизиты на изображении"
        else:
            await message.answer("Пожалуйста, отправьте текст или фото:")
            return
    
        product_id = db.add_product(
            data['name'],
            data['description'],
            data['price'],
            payment_details,
            payment_photo
        )
        
        await message.answer(f"Товар '{data['name']}' успешно добавлен!")
        await state.finish()

    @dp.message_handler(lambda message: message.text == "✏️ Редактировать товары")
    async def edit_products_list(message: types.Message):
        if not is_admin(message.from_user.id):
            return
        
        products = db.get_active_products()
        
        if not products:
            await message.answer("Нет товаров для редактирования.")
            return
        
        await message.answer("Выберите товар для редактирования:", reply_markup=get_products_edit_keyboard(products))

    @dp.callback_query_handler(lambda c: c.data.startswith("edit_product_"))
    async def edit_product_options(callback: types.CallbackQuery):
        product_id = int(callback.data.split("_")[2])
        product = db.get_product(product_id)
        
        if not product:
            await callback.answer("Товар не найден")
            return
        
        product_info = (
            f"Товар: {product[1]}\n"
            f"Описание: {product[2] or 'Отсутствует'}\n"
            f"Цена: {product[3]} руб.\n"
            f"Реквизиты: {product[4]}"
        )
        
        await callback.message.answer(product_info, reply_markup=get_product_edit_options_keyboard(product_id))
        await callback.answer()

    @dp.callback_query_handler(lambda c: c.data.startswith("edit_name_"))
    async def edit_product_name_start(callback: types.CallbackQuery, state: FSMContext):
        product_id = int(callback.data.split("_")[2])
        await state.update_data(product_id=product_id)
        await callback.message.answer("Введите новое название товара:")
        await EditProductStates.waiting_name.set()
        await callback.answer()

    @dp.message_handler(state=EditProductStates.waiting_name)
    async def process_edit_name(message: types.Message, state: FSMContext):
        data = await state.get_data()
        db.update_product(data['product_id'], name=message.text)
        await message.answer("Название товара обновлено!")
        await state.finish()

    @dp.callback_query_handler(lambda c: c.data.startswith("edit_desc_"))
    async def edit_product_desc_start(callback: types.CallbackQuery, state: FSMContext):
        product_id = int(callback.data.split("_")[2])
        await state.update_data(product_id=product_id)
        await callback.message.answer("Введите новое описание товара (отправьте '-' чтобы удалить):")
        await EditProductStates.waiting_description.set()
        await callback.answer()

    @dp.message_handler(state=EditProductStates.waiting_description)
    async def process_edit_description(message: types.Message, state: FSMContext):
        data = await state.get_data()
        description = message.text if message.text != '-' else None
        db.update_product(data['product_id'], description=description)
        await message.answer("Описание товара обновлено!")
        await state.finish()

    @dp.callback_query_handler(lambda c: c.data.startswith("edit_price_"))
    async def edit_product_price_start(callback: types.CallbackQuery, state: FSMContext):
        product_id = int(callback.data.split("_")[2])
        await state.update_data(product_id=product_id)
        await callback.message.answer("Введите новую цену товара:")
        await EditProductStates.waiting_price.set()
        await callback.answer()

    @dp.message_handler(state=EditProductStates.waiting_price)
    async def process_edit_price(message: types.Message, state: FSMContext):
        try:
            data = await state.get_data()
            price = int(message.text)
            db.update_product(data['product_id'], price=price)
            await message.answer("Цена товара обновлена!")
            await state.finish()
        except ValueError:
            await message.answer("Пожалуйста, введите корректное число:")

    @dp.callback_query_handler(lambda c: c.data.startswith("delete_product_"))
    async def delete_product_confirmation(callback: types.CallbackQuery):
        product_id = int(callback.data.split("_")[2])
        product = db.get_product(product_id)
        
        if not product:
            await callback.answer("Товар не найден")
            return
        
        await callback.message.answer(
            f"Вы уверены, что хотите удалить товар '{product[1]}'?",
            reply_markup=get_confirmation_keyboard("delete", product_id)
        )
        await callback.answer()

    @dp.callback_query_handler(lambda c: c.data.startswith("confirm_delete_"))
    async def confirm_delete_product(callback: types.CallbackQuery):
        product_id = int(callback.data.split("_")[2])
        db.delete_product(product_id)
        await callback.message.answer("Товар удален!")
        await callback.answer()

    @dp.callback_query_handler(lambda c: c.data.startswith("cancel_delete_"))
    async def cancel_delete_product(callback: types.CallbackQuery):
        await callback.message.answer("Удаление отменено.")
        await callback.answer()

    # УПРАВЛЕНИЕ ЗАЯВКАМИ
    @dp.message_handler(lambda message: message.text == "📋 Управление заявками")
    async def manage_orders(message: types.Message):
        if not is_admin(message.from_user.id):
            return
        
        pending_count = db.get_pending_orders_count()
        total_orders = len(db.get_all_orders(limit=1000))
        
        orders_text = (
            "📋 Управление заявками\n\n"
            f"Всего заявок: {total_orders}\n"
            f"⏳ Ожидают подтверждения: {pending_count}\n\n"
            "Выберите тип заявок для просмотра:"
        )
        
        await message.answer(orders_text, reply_markup=get_admin_orders_keyboard())

    @dp.callback_query_handler(lambda c: c.data.startswith("orders_"))
    async def handle_orders_selection(callback: types.CallbackQuery, state: FSMContext):
        action = callback.data
        
        if action == "orders_all":
            orders = db.get_all_orders()
            title = "📋 Все заявки"
        elif action == "orders_pending":
            orders = db.get_orders_by_status("ожидает")
            title = "⏳ Заявки ожидающие подтверждения"
        elif action == "orders_confirmed":
            orders = db.get_orders_by_status("подтверждено")
            title = "✅ Подтвержденные заявки"
        elif action == "orders_rejected":
            orders = db.get_orders_by_status("отклонено")
            title = "❌ Отклоненные заявки"
        elif action == "orders_back":
            await manage_orders(callback.message)
            await callback.answer()
            return
        else:
            await callback.answer("Неизвестное действие")
            return
        
        if not orders:
            await callback.message.answer(f"{title}\n\nЗаявки не найдены.")
            await callback.answer()
            return
        
        await state.update_data(
            current_orders=orders,
            current_page=0,
            orders_title=title
        )
        
        await show_orders_page(callback.message, state)
        await callback.answer()

    async def show_orders_page(message: types.Message, state: FSMContext):
        data = await state.get_data()
        orders = data['current_orders']
        current_page = data['current_page']
        title = data['orders_title']
        
        orders_text = f"{title}\n\n"
        orders_text += f"Страница {current_page + 1}\n"
        orders_text += f"Всего заявок: {len(orders)}\n\n"
        
        await message.answer(
            orders_text,
            reply_markup=get_orders_list_keyboard(orders, current_page)
        )

    @dp.callback_query_handler(lambda c: c.data.startswith("orders_page_"))
    async def handle_orders_pagination(callback: types.CallbackQuery, state: FSMContext):
        page = int(callback.data.split("_")[2])
        await state.update_data(current_page=page)
        await show_orders_page(callback.message, state)
        await callback.answer()

    @dp.callback_query_handler(lambda c: c.data.startswith("order_detail_"))
    async def show_order_detail(callback: types.CallbackQuery):
        order_id = int(callback.data.split("_")[2])
        order = db.get_order(order_id)
        
        if not order:
            await callback.answer("Заявка не найден")
            return
        
        (order_id, user_id, username, first_name, 
         product_id, product_name, price, status, created_at) = order
        
        # Форматируем дату
        if isinstance(created_at, str):
            created_date = created_at
        else:
            created_date = created_at.strftime("%d.%m.%Y %H:%M")
        
        status_emoji = {
            'ожидает': '⏳',
            'подтверждено': '✅',
            'отклонено': '❌'
        }.get(status, '📄')
        
        order_text = (
            f"📄 Детали заявки #{order_id}\n\n"
            f"Пользователь:\n"
            f"👤 ID: {user_id}\n"
            f"📛 Имя: {first_name}\n"
            f"🔗 Username: @{username if username else 'не указан'}\n\n"
            f"Товар:\n"
            f"🛍️ {product_name}\n"
            f"💰 Цена: {price} руб.\n\n"
            f"Статус: {status_emoji} {status}\n"
            f"Дата: {created_date}"
        )
        
        await callback.message.answer(
            order_text,
            reply_markup=get_order_actions_keyboard(order_id)
        )
        await callback.answer()

    @dp.callback_query_handler(lambda c: c.data.startswith("order_confirm_"))
    async def confirm_order(callback: types.CallbackQuery):
        order_id = int(callback.data.split("_")[2])
        
        if db.update_order_status(order_id, "подтверждено"):
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text="◀️ Назад к списку", callback_data="orders_list_back"))
            
            await callback.message.edit_text(
                f"✅ Заявка #{order_id} подтверждена!",
                reply_markup=keyboard
            )
        else:
            await callback.answer("Ошибка при подтверждении заявки")
        
        await callback.answer()

    @dp.callback_query_handler(lambda c: c.data.startswith("order_reject_"))
    async def reject_order(callback: types.CallbackQuery):
        order_id = int(callback.data.split("_")[2])
        
        if db.update_order_status(order_id, "отклонено"):
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text="◀️ Назад к списку", callback_data="orders_list_back"))
            
            await callback.message.edit_text(
                f"❌ Заявка #{order_id} отклонена!",
                reply_markup=keyboard
            )
        else:
            await callback.answer("Ошибка при отклонении заявки")
        
        await callback.answer()

    @dp.callback_query_handler(lambda c: c.data.startswith("order_contact_"))
    async def contact_user(callback: types.CallbackQuery):
        order_id = int(callback.data.split("_")[2])
        order = db.get_order(order_id)
        
        if order:
            user_id = order[1]
            username = order[2]
            
            contact_text = (
                f"👤 Контактная информация\n\n"
                f"Заявка: #{order_id}\n"
                f"User ID: {user_id}\n"
                f"Username: @{username if username else 'не указан'}\n\n"
                f"Чтобы связаться, используйте:\n"
                f"• Перешлите это сообщение\n"
                f"• Напишите напрямую: @{username}\n"
                f"• Используйте ID: {user_id}"
            )
            
            await callback.message.answer(contact_text)
        else:
            await callback.answer("Заявка не найдена")
        
        await callback.answer()

    @dp.callback_query_handler(lambda c: c.data == "orders_list_back")
    async def back_to_orders_list(callback: types.CallbackQuery, state: FSMContext):
        await show_orders_page(callback.message, state)
        await callback.answer()

    @dp.callback_query_handler(lambda c: c.data == "admin_back")
    async def back_to_admin_orders(callback: types.CallbackQuery):
        await manage_orders(callback.message)
        await callback.answer()

    @dp.message_handler(lambda message: message.text == "📊 Статистика")
    async def show_statistics(message: types.Message):
        if not is_admin(message.from_user.id):
            return
        
        total_users = db.get_total_users()
        total_products = db.get_total_products()
        completed_orders = db.get_completed_orders_count()
        pending_orders = db.get_pending_orders_count()
        rejected_orders = len(db.get_orders_by_status("отклонено", limit=1000))
        all_orders = len(db.get_all_orders(limit=1000))
        
        stats_text = (
            "📊 Статистика бота\n\n"
            f"👥 Пользователи: {total_users}\n"
            f"🛍️ Товары: {total_products}\n\n"
            f"📄 Всего заявок: {all_orders}\n"
            f"✅ Подтвержденные: {completed_orders}\n"
            f"⏳ Ожидают: {pending_orders}\n"
            f"❌ Отклоненные: {rejected_orders}"
        )
        
        await message.answer(stats_text)

    @dp.message_handler(lambda message: message.text == "⚙️ Настройки реквизитов")
    async def show_settings(message: types.Message):
        if not is_admin(message.from_user.id):
            return
        
        main_admin_id = db.get_setting('main_admin_id') or 'Не установлен'
        admin_username = db.get_setting('admin_username_for_contact') or ADMIN_USERNAME
        
        settings_text = (
            "⚙️ Настройки\n\n"
            f"User_ID администратора для уведомлений: {main_admin_id}\n"
            f"Username администратора для связи: {admin_username}"
        )
        
        await message.answer(settings_text, reply_markup=get_settings_keyboard())

    @dp.callback_query_handler(lambda c: c.data == "edit_admin_id")
    async def edit_admin_id_start(callback: types.CallbackQuery):
        await callback.message.answer("Введите новый User_ID администратора для уведомлений:")
        await SettingsStates.waiting_admin_id.set()
        await callback.answer()

    @dp.message_handler(state=SettingsStates.waiting_admin_id)
    async def process_admin_id(message: types.Message, state: FSMContext):
        try:
            admin_id = int(message.text)
            db.update_setting('main_admin_id', str(admin_id))
            await message.answer("User_ID администратора обновлен!")
            await state.finish()
        except ValueError:
            await message.answer("Пожалуйста, введите корректный ID (число):")

    @dp.callback_query_handler(lambda c: c.data == "edit_admin_username")
    async def edit_admin_username_start(callback: types.CallbackQuery):
        await callback.message.answer("Введите новый username администратора для связи (с @):")
        await SettingsStates.waiting_admin_username.set()
        await callback.answer()

    @dp.message_handler(state=SettingsStates.waiting_admin_username)
    async def process_admin_username(message: types.Message, state: FSMContext):
        new_username = message.text
        if not new_username.startswith('@'):
            new_username = '@' + new_username
        
        db.update_setting('admin_username_for_contact', new_username)
        await message.answer(f"✅ Username администратора обновлен на: {new_username}")
        await state.finish()