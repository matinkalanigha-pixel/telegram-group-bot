# telegram-group-bot
🤖 A powerful Telegram group management bot built with Python. Features include moderation, warnings, bans, mutes, content filters, custom commands, welcome messages, group rules, multilingual support, and an interactive admin menu. Built with python-telegram-bot and SQLite.
# 🤖 Telegram Group Management Bot

A powerful and customizable Telegram group management bot built with Python and `python-telegram-bot`.

This bot is designed to make Telegram group administration easier by providing moderation tools, customizable messages, multilingual support, content filters, warnings, locks, and an interactive admin menu.

## ✨ Features

* 🛡️ Advanced group moderation
* 👢 Kick, ban, unban, mute and unmute members
* ⚠️ Warning system with configurable limits
* 🔒 Content locks for links, photos, videos, stickers, GIFs, forwards, voice messages and documents
* 📝 Custom commands and responses
* 🎯 Keyword-based filters
* 👋 Custom welcome and goodbye messages
* 📌 Pin and unpin messages
* 📖 Group rules management
* 🌍 Persian and English language support
* 🎛️ Interactive inline admin menu
* 💾 SQLite database for storing group settings
* ⚙️ Environment-based configuration using `.env`
* 🧩 Modular and easy-to-extend code structure

## 🛠️ Technologies

* Python
* python-telegram-bot
* SQLite
* python-dotenv

## 🚀 Installation

Clone the repository and install the required dependencies:

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
pip install -r requirements.txt
```

Create a `.env` file and add your Telegram bot token:

```env
BOT_TOKEN=YOUR_BOT_TOKEN
DB_PATH=bot_data.db
```

Then run the bot:

```bash
python3 bot.py
```

## 🔐 Security

Never publish your real bot token or other sensitive information on GitHub.

The `.env` file should remain private and should be excluded using `.gitignore`.

## 📌 Project Status

This project is actively developed and can be extended with additional moderation tools, admin features, custom commands and other Telegram group management capabilities.

---

Made with ❤️ and Python.
