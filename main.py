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

if not BOT_TOKEN or not CHANNEL_ID:
    print("Error: BOT_TOKEN or CHANNEL_ID not set!", file=sys.stderr)
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

def format_card_caption(p):
    cc_string = f"{p['number']}|{p['month']}|{p['year']}|{p['cvv']}"
    caption = (
        "┏━━━━━━━━━━━━━━━━━━━━\n"
        "┃ 💎 𝘿𝙤𝙢𝙞𝙣𝙖𝙩𝙤𝙧 𝘿𝙧𝙤𝙥 💳\n"
        "┣━━━━━━━━━━━━━━━━━━━━\n"
        f"┃ 💎 𝑪𝑪: `{cc_string}`\n"
        f"┃ 👤 Owner: {p['full_name']}\n"
        f"┃ 📍 Address: {p['street_address']}\n"
        f"┃ 📮 Pin Code: {p['zip_code']}\n"
        f"┃ 🏦 Bank: {p['bank_name']}\n"
        f"┃ 🪄 Type: {p['card_brand']} - Debit - Standard\n"
        f"┃ 🌐 Country: {p['country']}\n"
        "┗━━━━━━━━━━━━━━━━━━━━\n"
        "✦ 𝑫𝑬𝑽 - [𝘿𝙤𝙢𝙞𝙣𝙖𝙩𝙤𝙧](https://t.me/DOMINATOR_XYZ) ✦"
    )
    return caption, cc_string

def format_bin_metrics():
    bins = [str(random.randint(400000, 699999)) for _ in range(5)]
    return bins

# --- ASYNC BOT LOOP ---
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    async with app:
        while True:
            try:
                # --- Generate single CC with one-click copy button ---
                profile = generate_card_profile()
                caption, cc_string = format_card_caption(profile)

                keyboard = InlineKeyboardMarkup([[
                    InlineKeyboardButton("📋 Copy CC", switch_inline_query_current_chat=cc_string)
                ]])

                await app.bot.send_photo(CHANNEL_ID, IMAGE_URL, caption=caption, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)

                # --- Generate BIN metrics with copy buttons ---
                bins = format_bin_metrics()
                for b in bins:
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
