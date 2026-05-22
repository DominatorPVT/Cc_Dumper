# main.py
import os
import asyncio
import random
import logging
import sys
from faker import Faker
from telegram import ParseMode
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
    caption = "┏━━━━━━━━━━━━━━━━━━━━\n"
    caption += "┃ 💎 𝘿𝙤𝙢𝙞𝙣𝙖𝙩𝙤𝙧 𝘿𝙧𝙤𝙥 💳\n"
    caption += "┣━━━━━━━━━━━━━━━━━━━━\n"
    caption += f"┃ 💎 𝑪𝑪: `{p['number']}|{p['month']}|{p['year']}|{p['cvv']}`\n"
    caption += f"┃ 👤 Owner: {p['full_name']}\n"
    caption += f"┃ 📍 Address: {p['street_address']}\n"
    caption += f"┃ 📮 Pin Code: {p['zip_code']}\n"
    caption += f"┃ 🏦 Bank: {p['bank_name']}\n"
    caption += f"┃ 🪄 Type: {p['card_brand']} - Debit - Standard\n"
    caption += f"┃ 🌐 Country: {p['country']}\n"
    caption += "┗━━━━━━━━━━━━━━━━━━━━\n"
    caption += "✦ 𝑫𝑬𝑽 - [𝘿𝙤𝙢𝙞𝙣𝙖𝙩𝙤𝙧](https://t.me/DOMINATOR_XYZ) ✦"
    return caption

def format_bin_metrics():
    bins = [str(random.randint(400000, 699999)) for _ in range(5)]
    message = "💎💳💎 BIN DROP 💳💎💎\n"
    message += "┏━━━━━━ BIN DROP 💎 ━━━━━━┓\n"
    for b in bins:
        message += f"┃ 🃏 ⭐ {b} 💎\n"
    message += "┗━━━━━━━━━━━━━━━━━━━━┛"
    return message

# --- ASYNC BOT LOOP ---
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    async with app:
        while True:
            try:
                for _ in range(10):  # 10 separate card messages
                    profile = generate_card_profile()
                    caption = format_card_caption(profile)
                    await app.bot.send_photo(CHANNEL_ID, IMAGE_URL, caption=caption, parse_mode=ParseMode.MARKDOWN)
                    await asyncio.sleep(random.randint(8,10))
                
                # BIN metrics after 10 cards
                bin_msg = format_bin_metrics()
                await app.bot.send_message(CHANNEL_ID, bin_msg, parse_mode=ParseMode.MARKDOWN)
                await asyncio.sleep(random.randint(8,10))
            except Exception as e:
                logging.error(f"Error: {e}", exc_info=True)
                await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())