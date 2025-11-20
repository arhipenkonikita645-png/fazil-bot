from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

def get_main_keyboard():
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text="🛒 Купить доступ"))
    return keyboard.as_markup(resize_keyboard=True)

def get_products_keyboard(products):
    keyboard = InlineKeyboardBuilder()
    for product in products:
        keyboard.add(InlineKeyboardButton(
            text=f"{product[1]} - {product[3]} руб.",
            callback_data=f"product_{product[0]}"
        ))
    keyboard.adjust(1)
    return keyboard.as_markup()

def get_product_actions_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="✅ Я оплатил(а)", callback_data="confirm_payment"))
    keyboard.add(InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_products"))
    keyboard.adjust(1)
    return keyboard.as_markup()

def get_admin_keyboard():
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text="➕ Добавить товар"))
    keyboard.add(KeyboardButton(text="✏️ Редактировать товары"))
    keyboard.add(KeyboardButton(text="📋 Управление заявками"))
    keyboard.add(KeyboardButton(text="⚙️ Настройки реквизитов"))
    keyboard.add(KeyboardButton(text="📊 Статистика"))
    keyboard.add(KeyboardButton(text="🚪 Выйти из админки"))
    keyboard.adjust(2)
    return keyboard.as_markup(resize_keyboard=True)

def get_products_edit_keyboard(products):
    keyboard = InlineKeyboardBuilder()
    for product in products:
        keyboard.add(InlineKeyboardButton(
            text=f"{product[0]} | {product[1]}",
            callback_data=f"edit_product_{product[0]}"
        ))
    keyboard.adjust(1)
    return keyboard.as_markup()

def get_product_edit_options_keyboard(product_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="✏️ Изменить название", callback_data=f"edit_name_{product_id}"))
    keyboard.add(InlineKeyboardButton(text="📝 Изменить описание", callback_data=f"edit_desc_{product_id}"))
    keyboard.add(InlineKeyboardButton(text="💰 Изменить цену", callback_data=f"edit_price_{product_id}"))
    keyboard.add(InlineKeyboardButton(text="🖼️ Изменить реквизиты", callback_data=f"edit_payment_{product_id}"))
    keyboard.add(InlineKeyboardButton(text="❌ Удалить товар", callback_data=f"delete_product_{product_id}"))
    keyboard.add(InlineKeyboardButton(text="◀️ Назад к списку", callback_data="back_to_products_list"))
    keyboard.adjust(1)
    return keyboard.as_markup()

def get_confirmation_keyboard(action, id):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="✅ Да", callback_data=f"confirm_{action}_{id}"))
    keyboard.add(InlineKeyboardButton(text="❌ Нет", callback_data=f"cancel_{action}_{id}"))
    keyboard.adjust(2)
    return keyboard.as_markup()

def get_settings_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="👤 Изменить User_ID для уведомлений", callback_data="edit_admin_id"))
    keyboard.add(InlineKeyboardButton(text="🔗 Изменить Username для связи", callback_data="edit_admin_username"))
    keyboard.adjust(1)
    return keyboard.as_markup()

# НОВЫЕ КЛАВИАТУРЫ ДЛЯ УПРАВЛЕНИЯ ЗАЯВКАМИ
def get_admin_orders_keyboard():
    """Клавиатура для управления заявками"""
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="📋 Все заявки", callback_data="orders_all"))
    keyboard.add(InlineKeyboardButton(text="⏳ Ожидают", callback_data="orders_pending"))
    keyboard.add(InlineKeyboardButton(text="✅ Подтвержденные", callback_data="orders_confirmed"))
    keyboard.add(InlineKeyboardButton(text="❌ Отклоненные", callback_data="orders_rejected"))
    keyboard.add(InlineKeyboardButton(text="◀️ Назад", callback_data="admin_back"))
    keyboard.adjust(2)
    return keyboard.as_markup()

def get_orders_list_keyboard(orders, current_page=0, orders_per_page=5):
    """Клавиатура со списком заявок"""
    keyboard = InlineKeyboardBuilder()
    
    start_idx = current_page * orders_per_page
    end_idx = start_idx + orders_per_page
    current_orders = orders[start_idx:end_idx]
    
    for order in current_orders:
        order_id, user_id, username, first_name, product_id, product_name, price, status, created_at = order
        
        status_emoji = {
            'ожидает': '⏳',
            'подтверждено': '✅',
            'отклонено': '❌'
        }.get(status, '📄')
        
        keyboard.add(InlineKeyboardButton(
            text=f"{status_emoji} {order_id} | {first_name} | {price} руб.",
            callback_data=f"order_detail_{order_id}"
        ))
    
    # Навигация
    if current_page > 0:
        keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"orders_page_{current_page-1}"))
    
    if end_idx < len(orders):
        keyboard.add(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"orders_page_{current_page+1}"))
    
    keyboard.add(InlineKeyboardButton(text="◀️ Назад к заявкам", callback_data="orders_back"))
    keyboard.adjust(1)
    return keyboard.as_markup()

def get_order_actions_keyboard(order_id):
    """Клавиатура действий для конкретной заявки"""
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"order_confirm_{order_id}"))
    keyboard.add(InlineKeyboardButton(text="❌ Отклонить", callback_data=f"order_reject_{order_id}"))
    keyboard.add(InlineKeyboardButton(text="📞 Связаться", callback_data=f"order_contact_{order_id}"))
    keyboard.add(InlineKeyboardButton(text="◀️ Назад к списку", callback_data="orders_list_back"))
    keyboard.adjust(2)
    return keyboard.as_markup()