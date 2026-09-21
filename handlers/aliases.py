"""
میانبرهای متنی برای اقدامات مدیریتی.

با این ماژول، ادمین می‌تواند به‌جای حفظ کردن دستورات انگلیسی مثل /kick، یک یا
چند کلمه‌ی دلخواه (فارسی یا هر زبان دیگری) تعریف کند که با ریپلای‌کردن روی
پیام یک کاربر و نوشتن همان کلمه، دقیقاً همان کاری که دستور اصلی انجام می‌داد
اجرا شود.

مثال: اگر ادمین کلمه‌ی «اخراج» را به اکشن kick وصل کند، از این پس با ریپلای
روی پیام کسی و نوشتن «اخراج» (به‌جای /kick) همان فرد اخراج می‌شود، همراه با
همان متنی که برای kick_msg تنظیم شده.

پشتیبانی‌شده: kick, ban, unban, mute, unmute, warn, unwarn, pin, unpin
"""

from telegram import Update
from telegram.ext import ContextTypes, ApplicationHandlerStop

import database as db
from . import moderation

ACTION_FUNCS = {
    "kick": moderation.kick_cmd,
    "ban": moderation.ban_cmd,
    "unban": moderation.unban_cmd,
    "mute": moderation.mute_cmd,
    "unmute": moderation.unmute_cmd,
    "warn": moderation.warn_cmd,
    "unwarn": moderation.unwarn_cmd,
    "pin": moderation.pin_cmd,
    "unpin": moderation.unpin_cmd,
}

# ترتیب نمایش در منو
ACTION_ORDER = list(ACTION_FUNCS.keys())


async def dispatch_alias(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    روی پیام‌های متنیِ معمولیِ گروه (نه دستور، نه پیوی) اجرا می‌شود. اگر اولین
    کلمه‌ی پیام با یکی از میانبرهای تعریف‌شده در همین گروه مطابقت داشته باشد،
    همان اکشن (با همان منطق و همان چک‌های ادمین‌بودن که دستور اصلی دارد) صدا
    زده می‌شود.
    """
    message = update.effective_message
    if not message or not message.text or update.effective_chat.type == "private":
        return

    words = message.text.strip().split()
    if not words:
        return

    first_word = words[0].lower()
    chat_id = update.effective_chat.id
    action = db.find_action_for_alias(chat_id, first_word)
    if not action or action not in ACTION_FUNCS:
        return

    # بقیه‌ی کلمات پیام را همان‌طور که برای /kick <آرگومان‌ها> رفتار می‌شد،
    # به‌عنوان آرگومان دستور شبیه‌سازی می‌کنیم (مثلاً مدت‌زمان یا دلیل).
    context.args = words[1:]
    await ACTION_FUNCS[action](update, context)
    raise ApplicationHandlerStop
