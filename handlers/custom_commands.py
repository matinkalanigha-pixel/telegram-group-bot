"""
امکان ساخت دستورات کاملاً دلخواه توسط ادمین.
مثال:
  /setcmd rules قوانین گروه: 1) احترام 2) بدون تبلیغ 3) بدون توهین
بعد از این هر کسی /rules بزند همان متن نمایش داده می‌شود.

از آنجا که python-telegram-bot دستورات را از قبل ثبت می‌کند، دستورات سفارشی
از طریق یک MessageHandler عمومی که پیام‌های شروع‌شده با / را می‌گیرد پردازش می‌شوند
(بعد از اینکه دستورات ثابتِ بات چک شدند).
"""

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

import database as db
from .utils import require_admin, render_template, user_mention

RESERVED_NAMES = {
    "start", "help", "kick", "ban", "unban", "mute", "unmute", "warn", "unwarn",
    "warnings", "setmaxwarns", "pin", "unpin", "setkickmsg", "setbanmsg",
    "setunbanmsg", "setmutemsg", "setunmutemsg", "setwarnmsg", "setunwarnmsg",
    "setmaxwarnactionmsg", "setwelcomemsg", "setgoodbyemsg", "setrules",
    "showmessages", "resetmsg", "setcmd", "delcmd", "commands", "filter",
    "stopfilter", "filters", "lock", "unlock", "locks", "note", "delnote",
    "notes", "rules", "welcome", "togglewelcome", "togglegoodbye",
}


async def setcmd_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_admin(update, context):
        return
    text = update.effective_message.text or ""
    parts = text.split(maxsplit=2)
    if len(parts) < 3:
        await update.effective_message.reply_text(
            "استفاده: /setcmd <نام_دستور> <متن پاسخ>\n"
            "مثال: /setcmd rules قوانین گروه اینجاست...\n"
            "می‌توانی از {user}, {admin}, {group} هم استفاده کنی."
        )
        return
    name = parts[1].lstrip("/").lower()
    response = parts[2]
    if name in RESERVED_NAMES:
        await update.effective_message.reply_text(
            "⛔ این نام رزرو شده و قابل بازنویسی نیست. نام دیگری انتخاب کن."
        )
        return
    db.add_custom_command(update.effective_chat.id, name, response)
    await update.effective_message.reply_text(f"✅ دستور /{name} ساخته شد.")


async def delcmd_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_admin(update, context):
        return
    if not context.args:
        await update.effective_message.reply_text("استفاده: /delcmd <نام_دستور>")
        return
    name = context.args[0].lstrip("/").lower()
    if db.remove_custom_command(update.effective_chat.id, name):
        await update.effective_message.reply_text(f"✅ دستور /{name} حذف شد.")
    else:
        await update.effective_message.reply_text("همچین دستوری پیدا نشد.")


async def list_custom_commands_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    names = db.list_custom_commands(update.effective_chat.id)
    if not names:
        await update.effective_message.reply_text("هنوز هیچ دستور سفارشی‌ای ساخته نشده.")
        return
    text = "🛠 دستورات سفارشی این گروه:\n" + "\n".join(f"• /{n}" for n in names)
    await update.effective_message.reply_text(text)


async def dynamic_command_dispatcher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    این هندلر روی همه‌ی پیام‌های /something اجرا می‌شود که با هیچ‌کدام از
    دستورات ثابت مطابقت نداشته (چون آن‌ها اولویت بالاتر و هندلر مجزا دارند).
    اگر دستور سفارشی متناظر پیدا شود، پاسخش ارسال می‌شود؛ در غیر این صورت نادیده گرفته می‌شود.
    """
    message = update.effective_message
    if not message or not message.text:
        return
    cmd = message.text.split()[0][1:].split("@")[0].lower()
    response = db.get_custom_command(update.effective_chat.id, cmd)
    if response is None:
        return
    text = render_template(
        response,
        user=user_mention(update.effective_user),
        admin=user_mention(update.effective_user),
        group=update.effective_chat.title or "",
    )
    await message.reply_text(text, parse_mode=ParseMode.HTML)
