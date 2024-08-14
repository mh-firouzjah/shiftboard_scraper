import asyncio
from pathlib import Path

import aiohttp
import jdatetime
import telegram
from bs4 import BeautifulSoup
from decouple import config

SHIFTBOARD_USERNAME = config("SHIFTBOARD_USERNAME")
SHIFTBOARD_PASSWORD = config("SHIFTBOARD_PASSWORD")
MY_TELEGRAM_CHAT_ID = config("MY_TELEGRAM_CHAT_ID")
TELEGRAMBOT_TOKEN = config("TELEGRAMBOT_TOKEN")
SHIFTBOARD_LOGIN_URL = config("SHIFTBOARD_LOGIN_URL")


# Get text content while keeping spaces and dashes
def get_readable_text(element):
    # Extract all text parts with spaces
    return [content.get_text(strip=True) for content in element.contents]


def latin_to_persian(text):
    # Mapping of Latin numerals to Persian numerals
    latin_to_persian_map = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
    # Translate the text using the map
    return text.translate(latin_to_persian_map)


async def get_new_shiftboard(session):
    # Fetch the login page
    async with session.get(SHIFTBOARD_LOGIN_URL) as response:
        login_page = await response.text()

    # Parse the login page HTML to extract the CSRF token
    soup = BeautifulSoup(login_page, "html.parser")
    csrf_token = soup.find("input", {"name": "_token"})["value"]

    # Login payload including CSRF token
    payload = {
        "name": SHIFTBOARD_USERNAME,
        "password": SHIFTBOARD_PASSWORD,
        "_token": csrf_token,  # Include the CSRF token in the payload
    }

    # Headers including CSRF token
    headers = {"X-XSRF-TOKEN": csrf_token}

    # Send a POST request to login with the CSRF token and session cookie
    async with session.post(SHIFTBOARD_LOGIN_URL, data=payload, headers=headers) as response:
        response_content = await response.text()

    soup = BeautifulSoup(response_content, "html.parser")

    today = jdatetime.datetime.today().date()
    remained_shifts = []

    if soup:
        for td_element in soup.find_all("td"):
            for date_span in td_element.find_all("span", class_="panel-title"):
                try:
                    # Parse the date from the element text
                    date = jdatetime.datetime.strptime(date_span.get_text(strip=True), "%Y-%m-%d").date()
                except ValueError:
                    continue  # Skip if the date parsing fails

                # Calculate the date for tomorrow
                if (
                    date > today
                    and any(
                        True for anchor in td_element.find_all("a")
                        if anchor.get_text(strip=True) in ("شیفت شب", "شیفت روز")
                    )
                ):
                    remained_shifts.append((date, td_element))

    nearest_shift = sorted(remained_shifts, key=lambda tp: tp[0])[0][1]

    # Extract all spans with class "panel-title"
    panel_titles = nearest_shift.find_all("span", class_="panel-title")
    panel_titles_text = [title.get_text(strip=True) for title in panel_titles]

    # Extract information within the specific div
    target_div = nearest_shift.find("div", class_="panel border-top-xlg border-top-green alpha-green")

    # Replace <i class="icon-dash"></i> with a dash (-)
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

    try:
        # Compare the new board with the existing one
        old_board = shiftboard_path.read_text()
        file_not_found = False
    except FileNotFoundError:
        file_not_found = True

    if file_not_found or new_board != old_board:
        # Update the shiftboard file with the new board data
        shiftboard_path.write_text(new_board)

        # Initialize telegram bot
        bot = telegram.Bot(token=TELEGRAMBOT_TOKEN)

        # Send the new board data to Telegram
        async with bot:
            await bot.send_message(chat_id=MY_TELEGRAM_CHAT_ID, text=new_board, parse_mode="HTML")


if __name__ == "__main__":
    asyncio.run(main())
