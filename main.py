import os
import asyncio
import random
import logging
import sys
from faker import Faker
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder

# --- CONFIGURATION ---
IMAGE_URL = "https://files.catbox.moe/qjmq6l.jpg"
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
BOT_USERNAME = os.environ.get("BOT_USERNAME")  # Add your bot username here, like 'MyBot'

if not BOT_TOKEN or not CHANNEL_ID or not BOT_USERNAME:
    print("Error: BOT_TOKEN, CHANNEL_ID or BOT_USERNAME not set!", file=sys.stderr)
    sys.exit(1)

fake = Faker()
logging.basicConfig(level=logging.INFO, stream=sys.stderr)

# --- UTILITY FUNCTIONS ---
def generate_cc_number():
    def luhn_residue(digits):
        sum_ = 0
        parity = len(digits) % 2
        for i, digit in enumerate(digits):
            if i % 2 == parity:
                digit *= 2
                if digit > 9:
                    digit -= 9
            sum_ += digit
        return sum_ % 10

    prefix = random.choice(["4", "5", "6"])
    cc = [int(d) for d in prefix]
    while len(cc) < 15:
        cc.append(random.randint(0, 9))
    cc.append((10 - luhn_residue(cc)) % 10)
    return ''.join(map(str, cc))

def generate_expiry():
    return str(random.randint(1, 12)).zfill(2), str(random.randint(2026, 2033))

def generate_cvv():
    return str(random.randint(100, 999))

def generate_card_profile():
    return {
        "number": generate_cc_number(),
        "month": generate_expiry()[0],
        "year": generate_expiry()[1],
        "cvv": generate_cvv(),
        "full_name": fake.name(),
        "street_address": fake.street_address(),
        "zip_code": fake.zipcode(),
        "bank_name": fake.company(),
        "card_brand": random.choice(["Visa", "Mastercard", "Discover", "Maestro"]),
        "country": fake.country()
    }

def format_card_caption(profile):
    cc_string = f"{profile['number']}|{profile['month']}|{profile['year']}|{profile['cvv']}"
    caption = (
        f"┏━━━━━━━━━━━━━━━━━━━━\n"
        f"┃ 💎 𝘿𝙤𝙢𝙞𝙣𝙖𝙩𝙤𝙧 𝘿𝙧𝙤𝙥 💳\n"
        f"┣━━━━━━━━━━━━━━━━━━━━\n"
        f"┃ 💎 𝑪𝑪: `{cc_string}`\n"
        f"┃ 👤 Owner: {profile['full_name']}\n"
        f"┃ 📍 Address: {profile['street_address']}\n"
        f"┃ 📮 Pin Code: {profile['zip_code']}\n"
        f"┃ 🏦 Bank: {profile['bank_name']}\n"
        f"┃ 🪄 Type: {profile['card_brand']} - Debit - Standard\n"
        f"┃ 🌐 Country: {profile['country']}\n"
        f"┗━━━━━━━━━━━━━━━━━━━━\n"
        f"✦ 𝑫𝑬𝑽 - [𝘿𝙤𝙢𝙞𝙣𝙖𝙩𝙤𝙧](https://t.me/DOMINATOR_XYZ) ✦"
    )
    return caption, cc_string

def format_bin_metrics():
    return [str(random.randint(400000, 699999)) for _ in range(5)]

# --- ASYNC BOT LOOP ---
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    async with app:
        while True:
            try:
                profile = generate_card_profile()
                caption, cc_string = format_card_caption(profile)
                
                # Check chat type safe button
                if CHANNEL_ID.startswith("@"):  # Channel
                    keyboard = InlineKeyboardMarkup([[
                        InlineKeyboardButton("📋 Copy CC", url=f"https://t.me/{BOT_USERNAME}?start=inlinequery_{cc_string}")
                    ]])
                else:
                    keyboard = InlineKeyboardMarkup([[
                        InlineKeyboardButton("📋 Copy CC", switch_inline_query_current_chat=cc_string)
                    ]])

                await app.bot.send_photo(CHANNEL_ID, IMAGE_URL, caption=caption, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)

                # BIN metrics
                bins = format_bin_metrics()
                for b in bins:
                    if CHANNEL_ID.startswith("@"):
                        bin_keyboard = InlineKeyboardMarkup([[
                            InlineKeyboardButton(f"📋 Copy BIN {b}", url=f"https://t.me/{BOT_USERNAME}?start=inlinequery_{b}")
                        ]])
                    else:
                        bin_keyboard = InlineKeyboardMarkup([[
                            InlineKeyboardButton(f"📋 Copy BIN {b}", switch_inline_query_current_chat=b)
                        ]])
                    await app.bot.send_message(CHANNEL_ID, f"💎 BIN DROP: `{b}`", parse_mode=ParseMode.MARKDOWN, reply_markup=bin_keyboard)

                await asyncio.sleep(random.randint(10, 15))

            except Exception as e:
                logging.error(f"Error: {e}", exc_info=True)
                await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
