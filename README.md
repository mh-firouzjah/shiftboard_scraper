# Python Selenium Screenshotter with GitHub Actions

## Overview

This project is a simple automation script that utilizes Selenium to capture a screenshot of a specified website. It first logs into the specified account, navigates to the desired page, captures the screenshot, and then sends it to a designated Telegram chat using the Python-telegram-bot package.

## Features

- Automated login: The script automatically logs into the specified account before capturing the screenshot.
- Customizable: You can easily customize the script to capture screenshots from different web pages and send them to different Telegram chats.
- GitHub Actions integration: The script can be configured to run as a GitHub Action, allowing you to schedule screenshot captures at regular intervals.

## Prerequisites

Before running the script, make sure you have the following:

- Python installed on your system
- Necessary Python packages installed (Selenium, python-telegram-bot, chromedriver-autoinstaller, python-decouple)
- Telegram Bot API token and chat ID for sending screenshots to Telegram
- Properly configured GitHub Actions workflow if you plan to use it as an automated task

## Installation

1. Clone the repository to your local machine:

    ```bash
    git clone https://github.com/mh-firouzjah/shiftboard_scrapper.git>
    ```

2. Install the required Python packages:

    ``` bash
    pip install -r requirements.txt
    ```

3. Configure the script by setting the necessary environment variables or updating the `.env` file with your credentials.

## Usage

- To capture a screenshot manually, run the following command:

    ```bash
    python scrapper.py
    ```

- To set up the script as a scheduled task using GitHub Actions, create a workflow file in the `.github/workflows` directory of your repository. Here's an example workflow file:

```yaml
name: Screenshotter

on:
  schedule:
    - cron: '0 0 ** *'  # Run the job daily at midnight

jobs:
  screenshot_job:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.x'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run screenshot script
        run: python scrapper.py
        env:
          WEB_URL: ${{ secrets.WEB_URL }}
          WEB_USERNAME: ${{ secrets.WEB_USERNAME }}
          WEB_PASSWORD: ${{ secrets.WEB_PASSWORD }}
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
```

Replace the `${{ secrets.SECRET_NAME }}` placeholders with your actual secrets stored in GitHub Secrets.

## Contributing

Contributions are welcome! If you encounter any issues or have suggestions for improvements, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgements

Special thanks to the developers of the GitHub, python-telegram-bot and Selenium libraries for making this project possible.
