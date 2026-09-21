# Telegram Group Management Bot

A complete Telegram group management bot where **all action messages can be fully customized by admins**.

For example, when a user is kicked, admins can define exactly what message the bot should send.

## Features

- 🖲 **Full interactive menu** (`/menu`) — configure everything using buttons without having to remember commands.
  Works both in groups and in the bot's private chat (using the **Continue in Private Chat** button or by sending `/menu` directly in private chat).

- ❓ **Built-in help system** — a help button explains how each section works. When editing messages, the exact meaning of every placeholder is also displayed.

- ⚡ **Command shortcuts** — instead of using commands such as `/kick`, `/ban`, etc., admins can define custom words for each action (kick, ban, mute, warn, etc.).
  By replying to a user's message and sending the configured word, the corresponding action is executed.

- 🌐 **Multilingual support** — Persian and English are supported, and adding new languages is easy.
  Each group can have its own independent language.

- Kick, ban, unban, mute (with duration), unmute — using replies, numeric user IDs, or public usernames (`@user`)

- Warning system with a configurable limit and automatic removal

- **Fully customizable action messages** using placeholders such as `{user}`, `{admin}`, `{reason}`, and `{group}`

- Create **completely custom commands** as an admin
  (for example, create `/rules`, `/telegram`, or any command you want)

- Word filters — automatically respond when a configured word is sent

- Content locks — links, images, videos, stickers, GIFs, forwarded messages, voice messages, and files

- Notes — save frequently used text and recall them using `#name`

- Customizable welcome and farewell messages

- Pin / unpin messages

- Group rules (`/rules`)

## Installation

```bash
cd telegram_group_bot
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
