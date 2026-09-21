from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

import database as db
from .utils import require_admin, render_template, user_mention


async def greet_new_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not db.get_flag(chat_id, "welcome_enabled"):
        return
    template = db.get_setting(chat_id, "welcome_msg")
    for member in update.effective_message.new_chat_members:
        if member.is_bot and member.id == context.bot.id:
            continue
        text = render_template(
            template, user=user_mention(member), group=update.effective_chat.title or ""
        )
        await update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)


async def farewell_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not db.get_flag(chat_id, "goodbye_enabled"):
        return
    left = update.effective_message.left_chat_member
    if not left or left.id == context.bot.id:
        return
    template = db.get_setting(chat_id, "goodbye_msg")
    text = render_template(
        template, user=user_mention(left), group=update.effective_chat.title or ""
    )
    await update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)


async def togglewelcome_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_admin(update, context):
        return
    chat_id = update.effective_chat.id
    new_value = not db.get_flag(chat_id, "welcome_enabled")
    db.set_flag(chat_id, "welcome_enabled", new_value)
    status = "فعال" if new_value else "غیرفعال"
    await update.effective_message.reply_text(f"پیام خوش‌آمدگویی {status} شد.")


async def togglegoodbye_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_admin(update, context):
        return
    chat_id = update.effective_chat.id
    new_value = not db.get_flag(chat_id, "goodbye_enabled")
    db.set_flag(chat_id, "goodbye_enabled", new_value)
    status = "فعال" if new_value else "غیرفعال"
    await update.effective_message.reply_text(f"پیام خداحافظی {status} شد.")


async def rules_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rules = db.get_setting(update.effective_chat.id, "rules")
    await update.effective_message.reply_text(f"📜 قوانین گروه:\n\n{rules}")
