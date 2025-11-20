import sqlite3
import logging
from datetime import datetime
from config import ADMIN_USERNAME

class Database:
    def __init__(self, db_path='fazil_bot.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Таблица пользователей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Таблица товаров
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    price INTEGER NOT NULL,
                    payment_details TEXT,
                    payment_photo TEXT,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')
            
            # Таблица заказов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    status TEXT DEFAULT 'ожидает',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (product_id) REFERENCES products (product_id)
                )
            ''')
            
            # Таблица настроек
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
            
            # Инициализация настроек по умолчанию
            cursor.execute('''
                INSERT OR IGNORE INTO settings (key, value) 
                VALUES ('admin_username_for_contact', ?)
            ''', (ADMIN_USERNAME,))
            
            cursor.execute('''
                INSERT OR IGNORE INTO settings (key, value) 
                VALUES ('main_admin_id', '0')
            ''')
            
            conn.commit()
    
    def add_user(self, user_id, username, first_name):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO users (user_id, username, first_name) 
                VALUES (?, ?, ?)
            ''', (user_id, username, first_name))
    
    def get_active_products(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM products WHERE is_active = TRUE')
            return cursor.fetchall()
    
    def get_product(self, product_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM products WHERE product_id = ?', (product_id,))
            return cursor.fetchone()
    
    def add_product(self, name, description, price, payment_details, payment_photo=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO products (name, description, price, payment_details, payment_photo)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, description, price, payment_details, payment_photo))
            return cursor.lastrowid
    
    def update_product(self, product_id, **kwargs):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])
            values = list(kwargs.values())
            values.append(product_id)
            cursor.execute(f'UPDATE products SET {set_clause} WHERE product_id = ?', values)
    
    def delete_product(self, product_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM products WHERE product_id = ?', (product_id,))
    
    def create_order(self, user_id, product_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO orders (user_id, product_id, status) 
                VALUES (?, ?, 'ожидает')
            ''', (user_id, product_id))
            return cursor.lastrowid
    
    def get_user_orders(self, user_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT o.*, p.name, p.price 
                FROM orders o 
                JOIN products p ON o.product_id = p.product_id 
                WHERE o.user_id = ?
            ''', (user_id,))
            return cursor.fetchall()
    
    def get_pending_orders_count(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM orders WHERE status = "ожидает"')
            return cursor.fetchone()[0]
    
    def get_total_users(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM users')
            return cursor.fetchone()[0]
    
    def get_total_products(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM products')
            return cursor.fetchone()[0]
    
    def get_completed_orders_count(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM orders WHERE status = "подтверждено"')
            return cursor.fetchone()[0]
    
    def get_setting(self, key):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def update_setting(self, key, value):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO settings (key, value) 
                VALUES (?, ?)
            ''', (key, value))

    # НОВЫЕ МЕТОДЫ ДЛЯ УПРАВЛЕНИЯ ЗАЯВКАМИ
    def get_all_orders(self, limit=50):
        """Получить все заказы с информацией о пользователях и товарах"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    o.order_id,
                    o.user_id,
                    u.username,
                    u.first_name,
                    o.product_id,
                    p.name as product_name,
                    p.price,
                    o.status,
                    o.created_at
                FROM orders o
                LEFT JOIN users u ON o.user_id = u.user_id
                LEFT JOIN products p ON o.product_id = p.product_id
                ORDER BY o.created_at DESC
                LIMIT ?
            ''', (limit,))
            return cursor.fetchall()

    def get_orders_by_status(self, status, limit=50):
        """Получить заказы по статусу"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    o.order_id,
                    o.user_id,
                    u.username,
                    u.first_name,
                    o.product_id,
                    p.name as product_name,
                    p.price,
                    o.status,
                    o.created_at
                FROM orders o
                LEFT JOIN users u ON o.user_id = u.user_id
                LEFT JOIN products p ON o.product_id = p.product_id
                WHERE o.status = ?
                ORDER BY o.created_at DESC
                LIMIT ?
            ''', (status, limit))
            return cursor.fetchall()

    def update_order_status(self, order_id, status):
        """Обновить статус заказа"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE orders 
                SET status = ? 
                WHERE order_id = ?
            ''', (status, order_id))
            return cursor.rowcount > 0

    def get_order(self, order_id):
        """Получить информацию о конкретном заказе"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    o.order_id,
                    o.user_id,
                    u.username,
                    u.first_name,
                    o.product_id,
                    p.name as product_name,
                    p.price,
                    o.status,
                    o.created_at
                FROM orders o
                LEFT JOIN users u ON o.user_id = u.user_id
                LEFT JOIN products p ON o.product_id = p.product_id
                WHERE o.order_id = ?
            ''', (order_id,))
            return cursor.fetchone()