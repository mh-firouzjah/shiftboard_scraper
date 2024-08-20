# Python Selenium Screenshotter with GitHub Actions

## Overview

This project is a simple automation script that logins to a website and reads some data from it then paste the important parts to my telegram chat.

## Features

- Automated login: The script automatically logs into the specified account before capturing the screenshot.
- Customizable: You can easily customize the script to capture screenshots from different web pages and send them to different Telegram chats.
- GitHub Actions integration: The script can be configured to run as a GitHub Action, allowing you to schedule screenshot captures at regular intervals.

## Prerequisites

Before running the script, make sure you have the following:

- Python installed on your system
- Necessary Python packages installed (python-telegram-bot, beautifulsoup4, python-decouple, jdatetime, flask)
- Telegram Bot API token and chat ID for sending screenshots to Telegram
- Properly configured GitHub Actions workflow if you plan to use it as an automated task

## Installation

1. Clone the repository to your local machine:

    ```bash
    git clone https://github.com/mh-firouzjah/shiftboard_scraper.git>
    ```

2. Install the required Python packages:

    ``` bash
    pip install -r requirements.txt
    ```

3. Configure the script by setting the necessary environment variables or updating the `.env` file with your credentials.

## Usage

- To capture a screenshot manually, run the following command:

    ```bash
    python scraper.py
    ```

- To set up the script as a scheduled task using GitHub Actions, create a workflow file in the `.github/workflows` directory of your repository. Here's an example workflow file:

```yaml
name: scraper

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
        run: python scraper.py
        env:
          SHIFTBOARD_USERNAME: ${{ secrets.SHIFTBOARD_USERNAME }}
          SHIFTBOARD_PASSWORD: ${{ secrets.SHIFTBOARD_PASSWORD }}
          MY_TELEGRAM_CHAT_ID: ${{ secrets.MY_TELEGRAM_CHAT_ID }}
          TELEGRAMBOT_TOKEN: ${{ secrets.TELEGRAMBOT_TOKEN }}
          SHIFTBOARD_LOGIN_URL: ${{ secrets.SHIFTBOARD_LOGIN_URL }}
```

Replace the `${{ secrets.SECRET_NAME }}` placeholders with your actual secrets stored in GitHub Secrets.

## Contributing

Contributions are welcome! If you encounter any issues or have suggestions for improvements, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgements

Special thanks to the developers of the GitHub, python-telegram-bot and Selenium libraries for making this project possible.
