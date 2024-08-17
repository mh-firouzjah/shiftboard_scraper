import asyncio
import base64
from pathlib import Path

import aiohttp
import jdatetime
import telegram
from bs4 import BeautifulSoup
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from decouple import config

# Configuration
SHIFTBOARD_USERNAME = config("SHIFTBOARD_USERNAME")
SHIFTBOARD_PASSWORD = config("SHIFTBOARD_PASSWORD")
MY_TELEGRAM_CHAT_ID = config("MY_TELEGRAM_CHAT_ID")
TELEGRAMBOT_TOKEN = config("TELEGRAMBOT_TOKEN")
SHIFTBOARD_LOGIN_URL = config("SHIFTBOARD_LOGIN_URL")
AES_KEY = config("THE_AES_KEY").encode()  # Ensure your AES key is 16, 24, or 32 bytes long
AES_IV = config("THE_AES_IV").encode()  # Ensure your AES IV is 16 bytes long


# AES Encryption
def encrypt_text(text, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ct_bytes = cipher.encrypt(pad(text.encode(), AES.block_size))
    return base64.b64encode(iv + ct_bytes).decode("utf-8")


# AES Decryption
def decrypt_text(encrypted_text, key):
    encrypted_data = base64.b64decode(encrypted_text)
    iv = encrypted_data[:16]  # Extract the IV
    ct = encrypted_data[16:]  # Extract the ciphertext
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ct), AES.block_size).decode("utf-8")


# Get text content while keeping spaces and dashes
def get_readable_text(element):
    return [content.get_text(strip=True) for content in element.contents]


def latin_to_persian(text):
    latin_to_persian_map = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
    return text.translate(latin_to_persian_map)


async def get_new_shiftboard(session):
    async with session.get(SHIFTBOARD_LOGIN_URL) as response:
        login_page = await response.text()

    soup = BeautifulSoup(login_page, "html.parser")
    csrf_token = soup.find("input", {"name": "_token"})["value"]

    payload = {
        "name": SHIFTBOARD_USERNAME,
        "password": SHIFTBOARD_PASSWORD,
        "_token": csrf_token,
    }

    headers = {"X-XSRF-TOKEN": csrf_token}

    async with session.post(SHIFTBOARD_LOGIN_URL, data=payload, headers=headers) as response:
        response_content = await response.text()

    soup = BeautifulSoup(response_content, "html.parser")

    today = jdatetime.datetime.today().date()
    remained_shifts = []

    if soup:
        for td_element in soup.find_all("td"):
            for date_span in td_element.find_all("span", class_="panel-title"):
                try:
                    date = jdatetime.datetime.strptime(date_span.get_text(strip=True), "%Y-%m-%d").date()
                except ValueError:
                    continue

                if (
                    date > today
                    and not td_element.find(string="موقعیت ها در وضعیت پیش نویس هستند.")
                    and any(
                        True
                        for anchor in td_element.find_all("a")
                        if anchor.get_text(strip=True) in ("شیفت شب", "شیفت روز")
                    )
                ):
                    remained_shifts.append((date, td_element))

    if not remained_shifts:
        return None
    nearest_shift = sorted(remained_shifts, key=lambda tp: tp[0])[0][1]

    panel_titles = nearest_shift.find_all("span", class_="panel-title")
    panel_titles_text = [title.get_text(strip=True) for title in panel_titles]

    target_div = nearest_shift.find("div", class_="panel border-top-xlg border-top-green alpha-green")

    for icon in target_div.find_all("i", class_="icon-dash"):
        icon.replace_with(" - ")

    finial_text = [string for string in panel_titles_text + get_readable_text(target_div) if string]
    date = "-".join(f"{string.rjust(2,'۰')}" for string in latin_to_persian(finial_text[2]).split("-")[::-1])
    return (
        f"<b>{finial_text[0]} {finial_text[1]} {date}</b>"
        f"\n<blockquote><b>{' '.join(finial_text[5:8])}  {finial_text[4]}</b></blockquote>"
        f"\n<blockquote><b>{' '.join(finial_text[9:])}  {finial_text[8]}</b></blockquote>"
    )


async def main():
    shiftboard_path = Path("shiftboard.txt")

    async with aiohttp.ClientSession() as session:
        new_board = await get_new_shiftboard(session)
        if not new_board:
            return

    try:
        # Read and decrypt the existing board file if it exists
        encrypted_board = shiftboard_path.read_text()
        old_board = decrypt_text(encrypted_board, AES_KEY)
        file_not_found = False
    except (FileNotFoundError, ValueError):
        file_not_found = True

    if file_not_found or new_board != old_board:
        # Encrypt and update the shiftboard file with the new board data
        encrypted_board = encrypt_text(new_board, AES_KEY, AES_IV)
        shiftboard_path.write_text(encrypted_board)

        # Initialize telegram bot
        bot = telegram.Bot(token=TELEGRAMBOT_TOKEN)

        # Send the new board data to Telegram
        async with bot:
            await bot.send_message(chat_id=MY_TELEGRAM_CHAT_ID, text=new_board, parse_mode="HTML")


if __name__ == "__main__":
    asyncio.run(main())
