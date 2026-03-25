import sqlite3
import random

db = sqlite3.connect("database.db")
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    bot_id INTEGER,
    balance INTEGER DEFAULT 0,
    total_deposit INTEGER DEFAULT 0
)
""")
db.commit()

def create_user(user_id):
    bot_id = random.randint(100000, 999999)
    cursor.execute("INSERT OR IGNORE INTO users (user_id, bot_id) VALUES (?,?)", (user_id, bot_id))
    db.commit()

def get_user(user_id):
    cursor.execute("SELECT bot_id, balance, total_deposit FROM users WHERE user_id=?", (user_id,))
    return cursor.fetchone()

def add_balance(user_id, amount):
    cursor.execute("UPDATE users SET balance=balance+?, total_deposit=total_deposit+? WHERE user_id=?", (amount, amount, user_id))
    db.commit()

def minus_balance(user_id, amount):
    cursor.execute("UPDATE users SET balance=balance-? WHERE user_id=?", (amount, user_id))
    db.commit()

def top_users():
    cursor.execute("SELECT bot_id,total_deposit FROM users ORDER BY total_deposit DESC LIMIT 10")
    return cursor.fetchall()
