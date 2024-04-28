import asyncio
import os
import time

import chromedriver_autoinstaller
import jdatetime
from decouple import config
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from telegram import Bot

display = Display(visible=0, size=(1200, 1200))
display.start()

URL = config("WEB_URL")
LOGOUT_URL = URL + "logout"
USERNAME = config("WEB_USERNAME")
PASSWORD = config("WEB_PASSWORD")
TELEGRAM_BOT_TOKEN = config("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = config("TELEGRAM_CHAT_ID")

# Check if the current version of chromedriver exists
# and if it doesn't exist, download it automatically,
# then add chromedriver to path
chromedriver_autoinstaller.install()


def login_and_capture_screenshot(username, password, url, logout_url, screenshot_path):
    # Instantiate ChromeOptions
    chrome_options = webdriver.ChromeOptions()

    # Add necessary options
    options = [
        "--window-size=2000,1600",
        "--ignore-certificate-errors",
        # "--headless",
        # "--disable-gpu",
        # "--no-sandbox",
        # "--disable-dev-shm-usage",
        # "--remote-debugging-port=9222"
    ]

    # Add options to ChromeOptions
    for option in options:
        chrome_options.add_argument(option)

    # Define device emulation parameters
    device_emulation = {
        # "deviceName": "Surface Pro 7",
        "deviceMetrics": {"width": 912, "height": 1368, "pixelRatio": 3.0},
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    }

    # Add mobile emulation option
    chrome_options.add_experimental_option("mobileEmulation", device_emulation)

    # Instantiate WebDriver with ChromeOptions
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)
        # Find and fill in username and password fields
        username_field = driver.find_element(By.ID, "name")
        password_field = driver.find_element(By.ID, "password")
        username_field.send_keys(username)
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)

        # Wait for page to load after login
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, f'a[href="{logout_url}"]'))
        )  # An element ID that appears after login

        # Find all span with the attribute class="panel-title"
        day_of_month = driver.find_elements(By.CLASS_NAME, "panel-title")

        for element in day_of_month:
            try:
                # Parse the date from the element text
                shift_date = jdatetime.datetime.strptime(element.text.strip(), "%Y-%m-%d").date()
            except ValueError:
                continue  # Skip if the date parsing fails

            # Calculate the date for tomorrow
            tomorrow_date = jdatetime.datetime.today().date() + jdatetime.timedelta(days=1)

            # Check if the parsed date is tomorrow's date
            if shift_date == tomorrow_date:
                # Navigate to the sibling element (the <a> tag) within the parent
                table_data = element.find_element(By.XPATH, ".//ancestor::td")

                modal_links = table_data.find_elements(
                    By.CSS_SELECTOR, '[data-target="#user_view_general_modal"]'
                )

                break  # Stop after finding the correct link

        # Find the link and click on it
        if modal_links:
            modal_links[0].click()

        def wait_for_ajax(driver):
            return (
                driver.find_element(By.ID, "user_view_general_modal_body")
                .get_attribute("class")
                .find("text-center")
            ) == -1

        # Wait for modal to appear
        WebDriverWait(driver, 30).until(wait_for_ajax)  # An element ID that appears in the modal

        # Add a short sleep duration to ensure UI updates have finished rendering
        time.sleep(2)

        # Take screenshot of the modal
        driver.save_screenshot(screenshot_path)

    finally:
        # Close the browser session
        driver.quit()


async def send_screenshot(screenshot_path):
    if not os.path.exists(screenshot_path): return 
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    try:
        # Send the screenshot via Telegram bot
        await bot.send_photo(TELEGRAM_CHAT_ID, open(screenshot_path, "rb"))
    except:
        pass
    finally:
        # Remove the screenshot file after sending
        os.remove(screenshot_path)


screenshot_path = "./screenshot.png"
if __name__ == "__main__":
    login_and_capture_screenshot(USERNAME, PASSWORD, URL, LOGOUT_URL, screenshot_path)
    asyncio.run(send_screenshot(screenshot_path))
    display.stop()
