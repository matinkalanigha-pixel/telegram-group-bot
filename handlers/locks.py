"""
قفل انواع محتوا در گروه. اگر قفل فعال باشد و کاربر عادی (غیر ادمین) آن نوع
پیام را بفرستد، پیام حذف می‌شود.
انواع پشتیبانی‌شده: link, photo, video, sticker, gif, forward, voice, document
"""

from telegram import Update
from telegram.ext import ContextTypes

import database as db
from .utils import require_admin, require_bot_admin, is_user_admin

LOCK_TYPES = ["link", "photo", "video", "sticker", "gif", "forward", "voice", "document"]


async def lock_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_admin(update, context):
        return
    if not context.args or context.args[0] not in LOCK_TYPES:
        await update.effective_message.reply_text(
            "استفاده: /lock <نوع>\nانواع مجاز: " + ", ".join(LOCK_TYPES)
        )
        return
    lock_type = context.args[0]
    db.set_lock(update.effective_chat.id, lock_type, True)
    await update.effective_message.reply_text(f"🔒 قفل «{lock_type}» فعال شد.")


async def unlock_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_admin(update, context):
        return
    if not context.args or context.args[0] not in LOCK_TYPES:
        await update.effective_message.reply_text(
            "استفاده: /unlock <نوع>\nانواع مجاز: " + ", ".join(LOCK_TYPES)
        )
        return
    lock_type = context.args[0]
    db.set_lock(update.effective_chat.id, lock_type, False)
    await update.effective_message.reply_text(f"🔓 قفل «{lock_type}» غیرفعال شد.")


async def list_locks_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    locks = db.get_locks(update.effective_chat.id)
    if not locks:
        await update.effective_message.reply_text("هیچ قفلی فعال نیست.")
        return
    await update.effective_message.reply_text("🔒 قفل‌های فعال:\n" + "\n".join(f"• {l}" for l in locks))


def _message_matches_lock(message, lock_type: str) -> bool:
    if lock_type == "link":
        if message.entities:
            for ent in message.entities:
                if ent.type in ("url", "text_link"):
                    return True
        if message.caption_entities:
            for ent in message.caption_entities:
                if ent.type in ("url", "text_link"):
                    return True
        return False
    if lock_type == "photo":
        return bool(message.photo)
    if lock_type == "video":
        return bool(message.video)
    if lock_type == "sticker":
        return bool(message.sticker)
    if lock_type == "gif":
        return bool(message.animation)
    if lock_type == "voice":
        return bool(message.voice)
    if lock_type == "document":
        return bool(message.document)
    if lock_type == "forward":
        return bool(message.forward_date or message.forward_origin)
    return False


async def enforce_locks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if not message or not update.effective_chat or update.effective_chat.type == "private":
        return
    chat_id = update.effective_chat.id
    locks = db.get_locks(chat_id)
    if not locks:
        return

    # ادمین‌ها از قفل‌ها مستثنی هستند
    if await is_user_admin(update, context, update.effective_user.id):
        return

    for lock_type in locks:
        if _message_matches_lock(message, lock_type):
            try:
                await message.delete()
            except Exception:
                pass
            return


# ---------- نوت‌ها ----------

async def savenote_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_admin(update, context):
        return
    text = update.effective_message.text or ""
    parts = text.split(maxsplit=2)
    if len(parts) < 3:
        await update.effective_message.reply_text(
            "استفاده: /note <نام> <محتوا>\nمثال: /note faq سوالات متداول اینجاست..."
        )
        return
    name, content = parts[1], parts[2]
    db.add_note(update.effective_chat.id, name, content)
    await update.effective_message.reply_text(f"✅ نوت «{name}» ذخیره شد. با #{name} قابل مشاهده است.")


async def delnote_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_admin(update, context):
        return
    if not context.args:
        await update.effective_message.reply_text("استفاده: /delnote <نام>")
        return
    name = context.args[0]
    if db.remove_note(update.effective_chat.id, name):
        await update.effective_message.reply_text(f"✅ نوت «{name}» حذف شد.")
    else:
        await update.effective_message.reply_text("همچین نوتی پیدا نشد.")


async def list_notes_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    names = db.list_notes(update.effective_chat.id)
    if not names:
        await update.effective_message.reply_text("هیچ نوتی ذخیره نشده.")
        return
    text = "🗒 نوت‌های ذخیره‌شده:\n" + "\n".join(f"• #{n}" for n in names)
    await update.effective_message.reply_text(text)


async def hashtag_note_dispatcher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """اگر پیام با #نام_نوت شروع شود، محتوای نوت نمایش داده می‌شود."""
    message = update.effective_message
    if not message or not message.text or not message.text.startswith("#"):
        return
    name = message.text[1:].split()[0].lower()
    content = db.get_note(update.effective_chat.id, name)
    if content:
        await message.reply_text(content)
