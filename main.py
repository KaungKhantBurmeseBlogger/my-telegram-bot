
import logging
import os
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiohttp import web
import asyncio

# Bot Token
API_TOKEN = 'YOUR_BOT_TOKEN_HERE'
ADMIN_ID = 8699560400 

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
user_data = {}

# --- Render အတွက် Web Server အသေးလေး ဆောက်ခြင်း ---
async def handle(request):
    return web.Response(text="Bot is running!")

async def on_startup(dp):
    # Web server ကို port 10000 မှာ run မယ် (Render ရဲ့ default)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get('PORT', 10000)))
    await site.start()

app = web.Application()
app.router.add_get("/", handle)
# ----------------------------------------------

# Start Keyboard
start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
start_keyboard.add(KeyboardButton('Start'))

main_menu = InlineKeyboardMarkup(row_width=1)
main_menu.add(
    InlineKeyboardButton("Channel join ရန်", url="https://t.me/nyeinmlbbshop"),
    InlineKeyboardButton("Diamond ဝယ်ရန်", callback_data="buy_diamond"),
    InlineKeyboardButton("နောက်မှ...", callback_data="later")
)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("Bot ကိုစတင်ရန် 'Start' ကိုနှိပ်ပါ", reply_markup=start_keyboard)

@dp.message_handler(lambda message: message.text == "Start")
async def show_menu(message: types.Message):
    await message.answer("မင်္ဂလာပါရှင့် Nyein's Mlbb Shop ရဲ့ Ai Bot ပဲဖြစ်ပါတယ်ရှင်။ ဘာများဝန်ဆောင်မှုပေးရမလဲရှင်", reply_markup=main_menu)

@dp.callback_query_handler(lambda c: c.data == 'buy_diamond')
async def process_buy_diamond(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    msg = "Nyein's Mlbb Shop မှာရနိုင်သော Diamond ဈေး‌များ\n41-3000MMK\n82-6000MMK\nWEEKLY PASS-7000MMK\n\nမှတ်ချက် - မိမိဝယ်ယူလိုသောအမျိုးစားကိုသာလျှင်ပို့ပေးပါရန် ဥပမာ 41၊ WeeklyPass 3ပတ်"
    await bot.send_message(callback_query.from_user.id, msg)
    user_data[callback_query.from_user.id] = {'step': 'waiting_item'}

@dp.message_handler(content_types=['text'])
async def handle_text(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_data and user_data[user_id].get('step') == 'waiting_item':
        user_data[user_id]['item'] = message.text
        user_data[user_id]['step'] = 'waiting_screenshot'
        await message.answer("ကျသင့်ငွေကို 09672663696 Kpay or Wave ဖြင့်လွှဲပြီး ပြေစာကို ss ပြပေးပါရှင်")
    elif message.text == "Start":
        await show_menu(message)

@dp.message_handler(content_types=['photo'])
async def handle_photo(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_data and user_data[user_id].get('step') == 'waiting_screenshot':
        selected_item = user_data[user_id]['item']
        try:
            await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=f"🛒 အော်ဒါအသစ်ရပါပြီ!\n\n💎 အမျိုးအစား: {selected_item}\n👤 ပို့သူ: @{message.from_user.username or 'No Username'}")
            await message.answer("အော်ဒါတင်ခြင်း အောင်မြင်ပါတယ်ရှင်။ ခေတ္တစောင့်ပေးပါဦး။")
        except:
            await message.answer("အော်ဒါပို့မရပါ။ Admin ကို တိုက်ရိုက်ပြောပေးပါရှင်။")
        del user_data[user_id]

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
