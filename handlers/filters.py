"""
فیلتر کلمات: ادمین می‌تواند تعریف کند وقتی کلمه‌ی خاصی در گروه گفته شد،
بات به‌طور خودکار یک پاسخ بدهد. مثال:
  /filter سلام درود بر تو دوست من!
حالا هر وقت کسی "سلام" بنویسد بات پاسخ می‌دهد.
"""

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

import database as db
from .utils import require_admin, render_template, user_mention


async def filter_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_admin(update, context):
        return
    text = update.effective_message.text or ""
    parts = text.split(maxsplit=2)
    if len(parts) < 3:
        await update.effective_message.reply_text(
            "استفاده: /filter <کلمه> <متن پاسخ>\nمثال: /filter تبلیغ تبلیغات ممنوع است!"
        )
        return
    keyword, response = parts[1], parts[2]
    db.add_filter(update.effective_chat.id, keyword, response)
    await update.effective_message.reply_text(f"✅ فیلتر برای «{keyword}» ثبت شد.")


async def stopfilter_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_admin(update, context):
        return
    if not context.args:
        await update.effective_message.reply_text("استفاده: /stopfilter <کلمه>")
        return
    keyword = context.args[0]
    if db.remove_filter(update.effective_chat.id, keyword):
        await update.effective_message.reply_text(f"✅ فیلتر «{keyword}» حذف شد.")
    else:
        await update.effective_message.reply_text("همچین فیلتری پیدا نشد.")


async def list_filters_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rows = db.get_filters(update.effective_chat.id)
    if not rows:
        await update.effective_message.reply_text("هیچ فیلتری تعریف نشده.")
        return
    text = "🔍 فیلترهای فعال:\n" + "\n".join(f"• {r['keyword']}" for r in rows)
    await update.effective_message.reply_text(text)


async def apply_filters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """روی هر پیام متنی چک می‌کند آیا کلمه‌ای از فیلترها داخلش هست یا نه."""
    message = update.effective_message
    if not message or not message.text:
        return
    chat_id = update.effective_chat.id
    rows = db.get_filters(chat_id)
    if not rows:
        return
    lowered = message.text.lower()
    for row in rows:
        if row["keyword"] in lowered:
            text = render_template(
                row["response"],
                user=user_mention(update.effective_user),
                group=update.effective_chat.title or "",
            )
            await message.reply_text(text, parse_mode=ParseMode.HTML)
            return
