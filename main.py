import logging
import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiohttp import web

# Bot Token
API_TOKEN = '8788197839:AAH7T2QTrv2wPPSG848i3VDcckzqvNxIyRI'  # BotFather ဆီကရတဲ့ Token ကို ဒီမှာထည့်ပါ
ADMIN_ID = 8699560400  # Admin ID နံပါတ်ပဲ ထည့်ပါ

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# User ရဲ့ ရွေးချယ်မှုကို ခေတ္တမှတ်ထားရန်
user_data = {}

# --- Render အတွက် Web Server အသေးလေး ဆောက်ခြင်း ---
async def handle(request):
    return web.Response(text="Bot is running!")

# Web server startup (Render က Web port ကို မြင်အောင်လုပ်ပေးမယ်)
async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Render ရဲ့ PORT variable ကို ဖတ်မယ်၊ မရှိရင် 8080 သုံးမယ်
    port = int(os.environ.get('PORT', 8080))
    # '0.0.0.0' မှာ bind လုပ်ဖို့ အရေးကြီးပါတယ်
    site = web.TCPSite(runner, '0.0.0.0', port) 
    await site.start()
    logging.info(f"Web server started on port {port}")

# ----------------------------------------------

# Start Keyboard
start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[KeyboardButton(text='Start')]])

# Main Buttons (aiogram v3 ရဲ့ ရေးဟန်အသစ်)
main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Channel join ရန်", url="https://t.me/nyeinmlbbshop")],
    [InlineKeyboardButton(text="Diamond ဝယ်ရန်", callback_data="buy_diamond")],
    [InlineKeyboardButton(text="နောက်မှ...", callback_data="later")]
])

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer("Bot ကိုစတင်ရန် 'Start' ကိုနှိပ်ပါ", reply_markup=start_keyboard)

@dp.message(F.text == "Start") # aiogram v3 ရဲ့ F filter ကိုသုံး
async def show_menu(message: types.Message):
    await message.answer("မင်္ဂလာပါရှင့် Nyein's Mlbb Shop ရဲ့ Ai Bot ပဲဖြစ်ပါတယ်ရှင်။ ဘာများဝန်ဆောင်မှုပေးရမလဲရှင်", reply_markup=main_menu)

@dp.callback_query(F.data == 'buy_diamond') # aiogram v3 ရဲ့ F filter ကိုသုံး
async def process_buy_diamond(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    msg = "Nyein's Mlbb Shop မှာရနိုင်သော Diamond ဈေး‌များ\n41-3000MMK\n82-6000MMK\nWEEKLY PASS-7000MMK\n\nမှတ်ချက် - မိမိဝယ်ယူလိုသောအမျိုးစားကိုသာလျှင်ပို့ပေးပါရန် ဥပမာ 41၊ WeeklyPass 3ပတ်"
    await bot.send_message(callback_query.from_user.id, msg)
    user_data[callback_query.from_user.id] = {'step': 'waiting_item'}

# aiogram v3 မှာ content_type စစ်ပုံအသစ်
@dp.message(F.content_type == types.ContentType.TEXT)
async def handle_text(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_data and user_data[user_id].get('step') == 'waiting_item':
        user_data[user_id]['item'] = message.text
        user_data[user_id]['step'] = 'waiting_screenshot'
        await message.answer("ကျသင့်ငွေကို 09672663696 Kpay or Wave ဖြင့်လွှဲပြီး ပြေစာကို ss ပြပေးပါရှင်")
    elif message.text == "Start":
        await show_menu(message)

# aiogram v3 မှာ content_type စစ်ပုံအသစ်
@dp.message(F.content_type == types.ContentType.PHOTO)
async def handle_photo(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_data and user_data[user_id].get('step') == 'waiting_screenshot':
        selected_item = user_data[user_id]['item']
        try:
            await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=f"🛒 အော်ဒါအသစ်ရပါပြီ!\n\n💎 အမျိုးအစား: {selected_item}\n👤 ပို့သူ: @{message.from_user.username or 'No Username'}")
            await message.answer("အော်ဒါတင်ခြင်း အောင်မြင်ပါတယ်ရှင်။ ခေတ္တစောင့်ပေးပါဦး။")
        except Exception as e:
            await message.answer("အော်ဒါပို့မရပါ။ Admin ကို တိုက်ရိုက်ပြောပေးပါရှင်။")
            logging.error(f"Error sending photo to admin: {e}")
        del user_data[user_id]

# --- Main entry point ---
async def main():
    # Start web server
    await start_web_server()
    
    # Start Bot Polling
    logging.info("Bot is starting (Polling with web server active)")
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped")
