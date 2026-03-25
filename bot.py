import logging
from aiogram import Bot, Dispatcher, types, executor
from config import *
from db import *

# ===== UPTIME =====
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot ishlayapti!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run).start()

# ===== BOT =====
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

state = {}

prices_sell = {"60":7000,"120":14000,"240":28000,"325":38000,"660":77000}
prices_buy = {"60":10000,"120":20000,"240":40000,"325":52000,"660":110000}

# ===== MENU =====
def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📤 Sotish","📥 Sotib olish")
    kb.add("💰 Hisob","📊 Statistika")
    kb.add("💎 UC Narxlari","🆘 Yordam")
    return kb

# ===== START =====
@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    create_user(msg.from_user.id)
    bot_id, bal,_ = get_user(msg.from_user.id)
    await msg.answer(f"Sizning ID: {bot_id}", reply_markup=main_menu())

# ===== ORQAGA =====
@dp.message_handler(lambda m: m.text=="🔙 Orqaga")
async def back(msg: types.Message):
    state[msg.from_user.id] = None
    await msg.answer("Menu", reply_markup=main_menu())

# ===== UC NARXLARI =====
@dp.message_handler(lambda m: m.text=="💎 UC Narxlari")
async def narx(msg: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("👤 Sotuvchi narxlari","🛒 Xaridor narxlari")
    kb.add("🔙 Orqaga")
    await msg.answer("Tanlang:", reply_markup=kb)

@dp.message_handler(lambda m: m.text=="👤 Sotuvchi narxlari")
async def sell_price(msg: types.Message):
    await msg.answer("60=7000\n120=14000\n240=28000\n325=38000\n660=77000")

@dp.message_handler(lambda m: m.text=="🛒 Xaridor narxlari")
async def buy_price(msg: types.Message):
    await msg.answer("60=10000\n120=20000\n240=40000\n325=52000\n660=110000")

# ===== SOTISH =====
@dp.message_handler(lambda m: m.text=="📤 Sotish")
async def sell(msg: types.Message):
    state[msg.from_user.id]="sell"
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for k in prices_sell: kb.add(f"{k} UC")
    kb.add("🔙 Orqaga")
    await msg.answer("Tanlang\n⚠️ Promokod ishlatilgan bo‘lsa pul berilmaydi", reply_markup=kb)

@dp.message_handler(lambda m: m.text.endswith("UC") and state.get(m.from_user.id)=="sell")
async def sell_uc(msg: types.Message):
    uc=msg.text.split()[0]
    state[msg.from_user.id]=f"promo_{uc}"
    await msg.answer("18 belgili promokod yubor:")

@dp.message_handler(lambda m: state.get(m.from_user.id,"").startswith("promo_"))
async def promo(msg: types.Message):
    if len(msg.text)!=18:
        await msg.answer("❌ 18 belgili bo‘lsin")
        return
    uc=state[msg.from_user.id].split("_")[1]
    bot_id,_,_=get_user(msg.from_user.id)

    await bot.send_message(CHANNEL_ID,f"📤 SOTISH\nID:{bot_id}\nUC:{uc}\nKod:{msg.text}")
    await msg.answer(f"✅ Yuborildi\n{prices_sell[uc]} so‘m olasiz")
    state[msg.from_user.id]=None

# ===== SOTIB OLISH =====
@dp.message_handler(lambda m: m.text=="📥 Sotib olish")
async def buy(msg: types.Message):
    state[msg.from_user.id]="buy"
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for k in prices_buy: kb.add(f"{k} UC")
    kb.add("🔙 Orqaga")
    await msg.answer("Tanlang (24 soat ichida beriladi)", reply_markup=kb)

@dp.message_handler(lambda m: m.text.endswith("UC") and state.get(m.from_user.id)=="buy")
async def buy_uc(msg: types.Message):
    uc=msg.text.split()[0]
    price=prices_buy[uc]
    bot_id,bal,_=get_user(msg.from_user.id)

    if bal<price:
        await msg.answer("❌ Yetarli emas")
        return

    state[msg.from_user.id]=f"buy_{uc}"
    await msg.answer("ID+Nick yubor:")

@dp.message_handler(lambda m: state.get(m.from_user.id,"").startswith("buy_"))
async def buy_finish(msg: types.Message):
    uc=state[msg.from_user.id].split("_")[1]
    price=prices_buy[uc]
    bot_id,_,_=get_user(msg.from_user.id)

    minus_balance(msg.from_user.id,price)

    await bot.send_message(CHANNEL_ID,f"📥 SOTIB OLISH\nID:{bot_id}\nUC:{uc}\nNick:{msg.text}")
    await bot.send_message(ADMIN_ID,f"Buy\nID:{bot_id}\nUC:{uc}\nNick:{msg.text}")

    await msg.answer("✅ 24 soatda beriladi")
    state[msg.from_user.id]=None

# ===== HISOB =====
@dp.message_handler(lambda m: m.text=="💰 Hisob")
async def acc(msg: types.Message):
    bot_id,bal,_=get_user(msg.from_user.id)
    kb=types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("➕ To‘ldirish","➖ Yechish")
    kb.add("🔙 Orqaga")
    await msg.answer(f"ID:{bot_id}\nBalans:{bal}",reply_markup=kb)

@dp.message_handler(lambda m: m.text=="➕ To‘ldirish")
async def dep(msg: types.Message):
    await msg.answer(f"{CARD_NUMBER}\nMin 5000\nChek yubor")

@dp.message_handler(content_types=types.ContentType.PHOTO)
async def check(msg: types.Message):
    bot_id,_,_=get_user(msg.from_user.id)
    await bot.send_photo(ADMIN_ID,msg.photo[-1].file_id,caption=f"TO‘LDIRISH ID:{bot_id}")

@dp.message_handler(lambda m: m.text=="➖ Yechish")
async def out(msg: types.Message):
    bot_id,bal,_=get_user(msg.from_user.id)
    if bal<14000:
        await msg.answer("❌ Min 14000")
        return
    state[msg.from_user.id]="withdraw"
    await msg.answer("Karta yubor:")

@dp.message_handler(lambda m: state.get(m.from_user.id)=="withdraw")
async def out2(msg: types.Message):
    bot_id,_,_=get_user(msg.from_user.id)
    minus_balance(msg.from_user.id,14000)
    await bot.send_message(ADMIN_ID,f"YECHISH ID:{bot_id}\n{msg.text}")
    await msg.answer("Yuborildi")
    state[msg.from_user.id]=None

# ===== STAT =====
@dp.message_handler(lambda m: m.text=="📊 Statistika")
async def stat(msg: types.Message):
    top=top_users()
    text="TOP:\n"
    for i,u in enumerate(top,1):
        text+=f"{i}. ID:{u[0]} - {u[1]}\n"
    await msg.answer(text)

# ===== YORDAM =====
@dp.message_handler(lambda m: m.text=="🆘 Yordam")
async def help(msg: types.Message):
    state[msg.from_user.id]="help"
    await msg.answer("Yoz:")

@dp.message_handler(lambda m: state.get(m.from_user.id)=="help")
async def help2(msg: types.Message):
    bot_id,_,_=get_user(msg.from_user.id)
    await bot.send_message(ADMIN_ID,f"YORDAM ID:{bot_id}\n{msg.text}")
    await msg.answer("Yuborildi")
    state[msg.from_user.id]=None

# ===== RUN =====
if __name__=="__main__":
    keep_alive()
    executor.start_polling(dp, skip_updates=True)
