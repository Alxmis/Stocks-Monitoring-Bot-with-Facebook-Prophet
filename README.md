# Stock Monitoring and Notification Bot
[![File count](https://img.shields.io/github/directory-file-count/alxmis/Stocks-Monitoring-Bot-with-Facebook-Prophet?style=for-the-badge&logo=github)](https://img.shields.io/github/directory-file-count/alxmis/Stocks-Monitoring-Bot-with-Facebook-Prophet?style=for-the-badge&logo=github) [![Repo size](https://img.shields.io/github/repo-size/alxmis/Stocks-Monitoring-Bot-with-Facebook-Prophet?style=for-the-badge&logo=github)](https://img.shields.io/github/repo-size/alxmis/Stocks-Monitoring-Bot-with-Facebook-Prophet?style=for-the-badge&logo=github) [![Language count](https://img.shields.io/github/languages/count/alxmis/Stocks-Monitoring-Bot-with-Facebook-Prophet?style=for-the-badge&logo=github)](https://img.shields.io/github/languages/count/alxmis/Stocks-Monitoring-Bot-with-Facebook-Prophet?style=for-the-badge&logo=github) [![Top language used](https://img.shields.io/github/languages/top/alxmis/Stocks-Monitoring-Bot-with-Facebook-Prophet?style=for-the-badge&logo=python&logoColor=white)](https://img.shields.io/github/languages/top/alxmis/Stocks-Monitoring-Bot-with-Facebook-Prophet?style=for-the-badge&logo=python&logoColor=white)


## Overview

Bot designed to monitor and analyze financial data related to stock prices, exchange rates, and similar metrics. The bot parses daily data, detects spikes or drops, and sends notifications with detailed analysis and charts to a Telegram chat. Additionally, it incorporates technical analysis and forecasting using Facebook's Prophet model.


## Features

- **Daily Data Parsing**: Automatically fetches financial data every day.
- **Monitoring**: Monitors data for significant fluctuations.
- **Notifications**: Sends notifications to a specified Telegram chat with detailed charts and descriptions.
- **Technical Analysis**: Includes technical analysis to provide deeper insights.
- **Predictive Models**: Uses predictive models, such as Prophet, to forecast future trends.

## Getting Started

### Prerequisites

- Required Python packages (listed in requirements.txt)
- Telegram bot API token and chat ID for notifications

### Installation

1. **Clone the repository:**

    ```sh
    git clone https://github.com/yourusername/financial-monitoring-system.git
    cd financial-monitoring-system
    ```

2. **Install dependencies:**

    ```sh
    pip install -r requirements.txt
    ```

3. **Set up environment variables:**

    Create a `.env` file in the project root directory and add your Telegram bot token and chat ID:

    ```env
    TELEGRAM_BOT_TOKEN=your_telegram_bot_token
    TELEGRAM_CHAT_ID=your_telegram_chat_id

## Acknowledgements

- [Facebook Prophet](https://facebook.github.io/prophet/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
