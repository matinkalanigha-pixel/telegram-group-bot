# 🤖 Telegram Group Management Bot

A modular Telegram group management bot built with **Python**, **python-telegram-bot**, and **SQLite**.

The bot provides group moderation, warnings, mutes, bans, content locks, keyword filters, custom commands, notes, welcome/goodbye messages, customizable action messages, command aliases, and an interactive inline admin menu.

---

## ✨ Features

* 🛡️ Member moderation
* 🚫 Kick, ban, unban, mute, and unmute
* ⚠️ Warning system with configurable limits
* 🔒 Automatic content locks
* 🔍 Keyword-based filters
* 🧩 Custom commands
* 🗒️ Group notes
* 👋 Welcome and goodbye messages
* 📌 Pin and unpin messages
* ✏️ Customizable moderation messages
* 🏷️ Dynamic message placeholders
* ⚡ Custom moderation aliases
* 🎛️ Inline admin control panel
* 🔐 Private administration panel
* 🌐 Persian and English group interface
* 💾 SQLite persistent storage
* 📦 No external database server required

---

## 🛠️ Tech Stack

| Component        | Technology               |
| ---------------- | ------------------------ |
| Language         | Python                   |
| Telegram Library | python-telegram-bot 21.4 |
| Configuration    | python-dotenv 1.0.1      |
| Database         | SQLite                   |
| Architecture     | Modular handlers         |
| Runtime          | Telegram Bot API         |

Dependencies are defined in `requirements.txt`.

---

## 📂 Project Structure

```text
telegram-group-bot/
│
├── bot.py
├── config.py
├── database.py
├── locales.py
├── requirements.txt
│
└── handlers/
    ├── __init__.py
    ├── aliases.py
    ├── custom_commands.py
    ├── custom_messages.py
    ├── filters.py
    ├── locks.py
    ├── menu.py
    ├── moderation.py
    ├── utils.py
    └── welcome.py
```

### Main Components

**`bot.py`**

Application entry point. Registers command handlers, message handlers, callback handlers, group membership tracking, lock enforcement, aliases, filters, notes, and the admin menu.

**`database.py`**

SQLite storage layer for group settings, warnings, filters, custom commands, notes, locks, known chats, and aliases.

**`config.py`**

Loads environment variables including `BOT_TOKEN` and the optional database path.

**`locales.py`**

Contains the group interface translations and supported languages.

---

# 🚀 Installation

## 1. Clone the repository

```bash
git clone https://github.com/matinkalanigha-pixel/telegram-group-bot.git
cd telegram-group-bot
```

## 2. Create a virtual environment

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows

```powershell
python -m venv venv
venv\Scripts\activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

The current project requires:

```text
python-telegram-bot==21.4
python-dotenv==1.0.1
```

---

# 🔑 Configuration

Create a `.env` file in the project root:

```env
BOT_TOKEN=YOUR_BOT_TOKEN
```

The application reads `BOT_TOKEN` from the environment.

You can also optionally configure the SQLite database location:

```env
BOT_TOKEN=YOUR_BOT_TOKEN
DB_PATH=bot_data.db
```

`DB_PATH` defaults to:

```text
bot_data.db
```

when it is not provided.

---

# 🤖 Create Your Bot

Open **@BotFather** in Telegram and create a bot.

Copy the token provided by BotFather and place it in `.env`:

```env
BOT_TOKEN=123456789:YOUR_TOKEN
```

Keep the token private and never commit it to Git.

---

# ▶️ Run the Bot

Start the application with:

```bash
python bot.py
```

On startup, the bot initializes the SQLite database and starts Telegram polling.

---

# 👮 Telegram Permissions

Add the bot to your group and promote it to administrator.

For the moderation and automatic deletion features, the bot needs the Telegram permissions required for the actions you want to use.

Recommended permissions:

```text
Delete Messages
Restrict Members
Ban Users
Pin Messages
```

The bot also checks that the person executing protected actions is a group administrator.

### Important

The required permissions depend on which features you use. You do not need to grant unrelated administrator permissions.

---

# 🎛️ Admin Menu

Open the interactive admin menu with:

```text
/menu
```

The menu is available both:

* Inside a group
* In the bot's private chat

From a group, the menu can provide a **Continue in Private Chat** flow.

In private chat, `/menu` can display groups where:

* The bot is known to be present
* The current user is an administrator

The selected group is stored in the user's session data so the administrator can continue managing the same group from private chat.

The menu includes sections for:

```text
Messages
Locks
Welcome / Goodbye
Warning Limit
Language
Notes
Filters
Custom Commands
Aliases
Help
```

---

# 🛡️ Moderation Commands

## Kick

```text
/kick
```

Target the user by replying to their message:

```text
/kick reason
```

Or provide an ID / username:

```text
/kick 123456789 reason
/kick @username reason
```

---

## Ban

```text
/ban
```

Examples:

```text
/ban spam
/ban 123456789 spam
/ban @username spam
```

---

## Unban

```text
/unban
```

Example:

```text
/unban 123456789
```

---

# 🔇 Mute

```text
/mute
```

Mute supports these duration units:

```text
m = minutes
h = hours
d = days
w = weeks
```

Examples:

```text
/mute 30m
/mute 2h
/mute 1d
/mute 1w
```

With a reason:

```text
/mute 2h spam
```

When replying to a user's message:

```text
/mute 2h spam
```

Without a valid duration, the mute remains unlimited.

---

# 🔊 Unmute

```text
/unmute
```

Example:

```text
/unmute 123456789
```

Or reply to the user's message and use:

```text
/unmute
```

---

# ⚠️ Warning System

Give a warning:

```text
/warn
```

Examples:

```text
/warn spam
/warn 123456789 spam
/warn @username spam
```

Check warnings:

```text
/warnings
```

Set the warning limit:

```text
/setmaxwarns 3
```

The default maximum warning count is `3`.

When a user reaches the configured limit, the bot resets the warning counter and attempts the configured automatic action.

Remove one warning:

```text
/unwarn
```

Example:

```text
/unwarn 123456789
```

---

# 📌 Pin Management

Pin a replied-to message:

```text
/pin
```

Silent pin:

```text
/pin silent
```

Unpin:

```text
/unpin
```

---

# ✏️ Custom Action Messages

Administrators can replace the text used after moderation actions.

Available message settings:

```text
/setkickmsg
/setbanmsg
/setunbanmsg
/setmutemsg
/setunmutemsg
/setwarnmsg
/setunwarnmsg
/setmaxwarnactionmsg
/setwelcomemsg
/setgoodbyemsg
/setrules
```

Example:

```text
/setkickmsg 🚪 {user} was removed by {admin}. Reason: {reason}
```

Show current messages:

```text
/showmessages
```

Reset a message:

```text
/resetmsg <key>
```

Supported message keys include:

```text
welcome_msg
goodbye_msg
kick_msg
ban_msg
unban_msg
mute_msg
unmute_msg
warn_msg
unwarn_msg
max_warn_action_msg
rules
```

---

# 🧩 Message Placeholders

Custom messages can use dynamic placeholders.

| Placeholder    | Description                            |
| -------------- | -------------------------------------- |
| `{user}`       | Target user                            |
| `{admin}`      | Administrator who performed the action |
| `{reason}`     | Moderation reason                      |
| `{group}`      | Group name                             |
| `{duration}`   | Mute duration                          |
| `{warn_count}` | Current warning count                  |
| `{max_warns}`  | Warning limit                          |

Example:

```text
/setkickmsg 🚪 {user} was removed by {admin}. Reason: {reason}
```

```text
/setmutemsg 🔇 {user} was muted by {admin} for {duration}. Reason: {reason}
```

```text
/setwarnmsg ⚠️ {user} received a warning from {admin}. {warn_count}/{max_warns}
```

---

# 🛠️ Custom Commands

Create a custom command:

```text
/setcmd <name> <response>
```

Example:

```text
/setcmd rules Please read the group rules before posting.
```

Use it:

```text
/rules
```

List custom commands:

```text
/commands
```

Delete a custom command:

```text
/delcmd <name>
```

Example:

```text
/delcmd rules
```

Custom commands can use:

```text
{user}
{admin}
{group}
```

Built-in command names are protected from being overwritten.

---

# 🔍 Keyword Filters

Create a filter:

```text
/filter <keyword> <response>
```

Example:

```text
/filter hello Welcome to the group!
```

Remove a filter:

```text
/stopfilter <keyword>
```

List filters:

```text
/filters
```

The filter system checks normal text messages and sends the configured response when a matching keyword is detected.

---

# 🔒 Content Locks

Supported lock types:

```text
link
photo
video
sticker
gif
forward
voice
document
```

Enable a lock:

```text
/lock link
```

Disable a lock:

```text
/unlock link
```

Show active locks:

```text
/locks
```

Example:

```text
/lock link
```

Matching content from non-admin users can then be automatically deleted.

---

# 🗒️ Notes

Create a note:

```text
/note <name> <content>
```

Example:

```text
/note faq Frequently asked questions are listed here.
```

List notes:

```text
/notes
```

Delete a note:

```text
/delnote <name>
```

Example:

```text
/delnote faq
```

Use a saved note:

```text
#faq
```

---

# 👋 Welcome and Goodbye Messages

Toggle welcome messages:

```text
/togglewelcome
```

Toggle goodbye messages:

```text
/togglegoodbye
```

Customize the messages:

```text
/setwelcomemsg
/setgoodbyemsg
```

Example:

```text
/setwelcomemsg Welcome {user} to {group}!
```

---

# 📜 Group Rules

Set the rules:

```text
/setrules Group rules go here.
```

Display the rules:

```text
/rules
```

---

# ⚡ Command Aliases

The bot supports custom aliases for moderation actions.

Supported actions:

```text
kick
ban
unban
mute
unmute
warn
unwarn
pin
unpin
```

Aliases can be configured through:

```text
/menu
```

Example:

```text
kick → remove
ban → block
mute → silence
warn → warning
```

An alias can then trigger the corresponding moderation action without using the original command name.

---

# 🌐 Languages

The project currently includes:

```text
fa
en
```

Language selection is available from:

```text
/menu
```

The selected language is stored per group.

---

# 💾 Database

The project uses SQLite, so no external database server is required.

The database stores:

```text
Group settings
Warnings
Filters
Custom commands
Notes
Content locks
Known chats
Command aliases
```

The database is initialized automatically when the bot starts.

Default database file:

```text
bot_data.db
```

Optional custom path:

```env
DB_PATH=/path/to/database.db
```

---

# 🔐 Security

Never upload your `.env` file or bot token to GitHub.

Example:

```env
BOT_TOKEN=YOUR_PRIVATE_TOKEN
```

Keep credentials outside the repository and make sure sensitive files are ignored by Git.

Recommended `.gitignore` entries:

```gitignore
.env
*.db
__pycache__/
*.pyc
venv/
.venv/
```

---

# 🧪 Quick Start

```bash
git clone https://github.com/matinkalanigha-pixel/telegram-group-bot.git
cd telegram-group-bot

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

Create `.env`:

```env
BOT_TOKEN=YOUR_BOT_TOKEN
```

Run:

```bash
python bot.py
```

Add the bot to your Telegram group, promote it to administrator, and run:

```text
/menu
```

---

# 🐛 Troubleshooting

## Bot does not start

Check that `.env` contains:

```env
BOT_TOKEN=YOUR_BOT_TOKEN
```

Also make sure the virtual environment is activated and dependencies are installed.

---

## Moderation does not work

Check:

```text
1. The user running the command is a group administrator.
2. The bot is a group administrator.
3. The bot has the required Telegram permission.
```

---

## Locks do not delete messages

Check that the bot has:

```text
Delete Messages
```

enabled and verify the active locks with:

```text
/locks
```

---

# 🤝 Contributing

This project is open to improvements and new ideas.

If you enjoy working with **Python, Telegram bots, automation, moderation systems, or SQLite**, feel free to improve the project.

You can contribute by:

* Adding new features
* Improving existing handlers
* Fixing bugs
* Improving the admin panel
* Adding new languages
* Improving performance
* Creating better moderation tools
* Improving the documentation

A simple contribution workflow:

```bash
git checkout -b feature/your-feature
```

Make your changes, test them, commit your work, and open a pull request.

### 💡 Have an idea?

Suggestions, improvements, and feature requests are welcome.

Even a small improvement can make the project more useful for everyone.

---

# 📄 License

This repository currently does not declare a software license.

Until a license is added, the project should not be assumed to be licensed for unrestricted redistribution or modification.

---

# 👨‍💻 Author

**Matin Kalanigha**

GitHub:

https://github.com/matinkalanigha-pixel

Repository:

https://github.com/matinkalanigha-pixel/telegram-group-bot

---

# ⭐ Support the Project

If you find the project useful:

```text
⭐ Star the repository
🐛 Report bugs
💡 Suggest features
🔧 Contribute improvements
📢 Share the project
```

---

## 📌 Current Command Reference

```text
/start
/help
/menu

/kick
/ban
/unban
/mute
/unmute
/warn
/unwarn
/warnings
/setmaxwarns
/pin
/unpin

/setkickmsg
/setbanmsg
/setunbanmsg
/setmutemsg
/setunmutemsg
/setwarnmsg
/setunwarnmsg
/setmaxwarnactionmsg
/setwelcomemsg
/setgoodbyemsg
/setrules
/showmessages
/resetmsg

/setcmd
/delcmd
/commands

/filter
/stopfilter
/filters

/lock
/unlock
/locks

/note
/delnote
/notes

/togglewelcome
/togglegoodbye

/rules
```
