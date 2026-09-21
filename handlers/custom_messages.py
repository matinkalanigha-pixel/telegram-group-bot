"""
اینجا قلب قابلیت درخواستی کاربر است: ادمین می‌تواند متن هر اکشن را
(کیک، بن، سایلنت، اخطار، خوش‌آمدگویی و ...) با پلیس‌هولدرهای دلخواه تغییر دهد.

پلیس‌هولدرهای قابل استفاده در هر متن (بسته به نوع پیام):
  {user}    -> منشن کاربر هدف
  {admin}   -> منشن ادمینی که دستور را زده
  {reason}  -> دلیل اقدام (در صورت وجود)
  {group}   -> نام گروه
  {duration}-> مدت‌زمان (فقط برای mute)
  {warn_count} / {max_warns} -> فقط برای warn

مثال استفاده:
  /setkickmsg {user} با لگد پرت شد بیرون توسط {admin} 😂 دلیل: {reason}
"""

from telegram import Update
from telegram.ext import ContextTypes

import database as db
from .utils import require_admin

# نگاشت دستور به کلید دیتابیس و توضیح
SETTABLE_MESSAGES = {
    "setkickmsg": ("kick_msg", "پیام اخراج (کیک)"),
    "setbanmsg": ("ban_msg", "پیام بن"),
    "setunbanmsg": ("unban_msg", "پیام آنبن"),
    "setmutemsg": ("mute_msg", "پیام سایلنت"),
    "setunmutemsg": ("unmute_msg", "پیام آنمیوت"),
    "setwarnmsg": ("warn_msg", "پیام اخطار"),
    "setunwarnmsg": ("unwarn_msg", "پیام حذف اخطار"),
    "setmaxwarnactionmsg": ("maxwarn_action_msg", "پیام رسیدن به سقف اخطار"),
    "setwelcomemsg": ("welcome_msg", "پیام خوش‌آمدگویی"),
    "setgoodbyemsg": ("goodbye_msg", "پیام خداحافظی"),
    "setrules": ("rules", "قوانین گروه"),
}


def make_setter(db_key: str, label: str):
    async def _setter(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await require_admin(update, context):
            return
        text = update.effective_message.text or ""
        # حذف خودِ دستور از ابتدای متن
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            await update.effective_message.reply_text(
                f"استفاده: /{context.matched_command if hasattr(context, 'matched_command') else ''} <متن جدید>\n\n"
                f"در حال تنظیم: {label}\n"
                "می‌توانی از {user}, {admin}, {reason}, {group} در متن استفاده کنی."
            )
            return
        new_text = parts[1]
        db.set_setting(update.effective_chat.id, db_key, new_text)
        await update.effective_message.reply_text(f"✅ {label} با موفقیت به‌روزرسانی شد.")

    return _setter


async def show_messages_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش همه متن‌های فعلی تنظیم‌شده برای این گروه."""
    chat_id = update.effective_chat.id
    lines = ["📋 متن‌های فعلی این گروه:\n"]
    for cmd_name, (db_key, label) in SETTABLE_MESSAGES.items():
        current = db.get_setting(chat_id, db_key)
        lines.append(f"• {label} (/{cmd_name}):\n{current}\n")
    await update.effective_message.reply_text("\n".join(lines))


async def resetmsg_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بازگرداندن یک متن به حالت پیش‌فرض: /resetmsg kick_msg"""
    if not await require_admin(update, context):
        return
    if not context.args:
        keys = ", ".join(db.DEFAULT_MESSAGES.keys())
        await update.effective_message.reply_text(
            f"استفاده: /resetmsg <کلید>\nکلیدهای معتبر:\n{keys}"
        )
        return
    key = context.args[0]
    if key not in db.DEFAULT_MESSAGES:
        await update.effective_message.reply_text("کلید نامعتبر است.")
        return
    db.set_setting(update.effective_chat.id, key, db.DEFAULT_MESSAGES[key])
    await update.effective_message.reply_text("✅ متن به حالت پیش‌فرض بازگشت.")
