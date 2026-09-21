"""
دستورات اصلی مدیریت گروه: کیک، بن، آنبن، سایلنت (میوت)، آنمیوت، اخطار.
متن هر پیام از دیتابیس خوانده می‌شود تا ادمین بتواند با دستورات موجود در
custom_messages.py آن را به دلخواه خودش تغییر دهد.
"""

import time
from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

import database as db
from .utils import (
    require_admin,
    require_bot_admin,
    get_target_user,
    get_reason,
    render_template,
    user_mention,
)

DURATION_UNITS = {"m": 60, "h": 3600, "d": 86400, "w": 604800}


def parse_duration(text: str):
    """تبدیل رشته‌هایی مثل 10m, 2h, 1d به ثانیه. خروجی None یعنی نامعتبر."""
    if not text:
        return None
    unit = text[-1]
    if unit not in DURATION_UNITS:
        return None
    try:
        value = int(text[:-1])
    except ValueError:
        return None
    return value * DURATION_UNITS[unit]


async def kick_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_admin(update, context) or not await require_bot_admin(update, context):
        return
    target = await get_target_user(update, context)
    if not target:
        await update.effective_message.reply_text(
            "کاربر مشخص نشد. روی پیام فرد ریپلای کن یا آیدی عددی‌اش را بده."
        )
        return

    chat_id = update.effective_chat.id
    was_reply = bool(update.effective_message.reply_to_message)
    reason = get_reason(context, skip_first_arg=not was_reply)
    try:
        await context.bot.unban_chat_member(chat_id, target.id, only_if_banned=False)
    except Exception as e:
        await update.effective_message.reply_text(f"خطا در اخراج کاربر: {e}")
        return

    template = db.get_setting(chat_id, "kick_msg")
    text = render_template(
        template,
        user=user_mention(target),
        admin=user_mention(update.effective_user),
        reason=reason,
        group=update.effective_chat.title or "",
    )
    await update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)


async def ban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_admin(update, context) or not await require_bot_admin(update, context):
        return
    target = await get_target_user(update, context)
    if not target:
        await update.effective_message.reply_text(
            "کاربر مشخص نشد. روی پیام فرد ریپلای کن یا آیدی عددی‌اش را بده."
        )
        return

    chat_id = update.effective_chat.id
    was_reply = bool(update.effective_message.reply_to_message)
    reason = get_reason(context, skip_first_arg=not was_reply)
    try:
        await context.bot.ban_chat_member(chat_id, target.id)
    except Exception as e:
        await update.effective_message.reply_text(f"خطا در بن کردن کاربر: {e}")
        return

    template = db.get_setting(chat_id, "ban_msg")
    text = render_template(
        template,
        user=user_mention(target),
        admin=user_mention(update.effective_user),
        reason=reason,
        group=update.effective_chat.title or "",
    )
    await update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)


async def unban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_admin(update, context) or not await require_bot_admin(update, context):
        return
    target = await get_target_user(update, context)
    if not target:
        await update.effective_message.reply_text("کاربر مشخص نشد.")
        return

    chat_id = update.effective_chat.id
    try:
        await context.bot.unban_chat_member(chat_id, target.id)
    except Exception as e:
        await update.effective_message.reply_text(f"خطا: {e}")
        return

    template = db.get_setting(chat_id, "unban_msg")
    text = render_template(
        template, user=user_mention(target), admin=user_mention(update.effective_user)
    )
    await update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)


async def mute_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_admin(update, context) or not await require_bot_admin(update, context):
        return
    target = await get_target_user(update, context)
    if not target:
        await update.effective_message.reply_text(
            "کاربر مشخص نشد. روی پیام فرد ریپلای کن یا آیدی عددی‌اش را بده.\n"
            "مثال: /mute 1h اسپم می‌کرد"
        )
        return

    chat_id = update.effective_chat.id
    was_reply = bool(update.effective_message.reply_to_message)
    args = context.args or []
    if not was_reply and args:
        args = args[1:]  # اولین آرگومان آیدی/یوزرنیم هدف بود، نه بخشی از مدت/دلیل
    duration_seconds = None
    reason_args = args
    if args and parse_duration(args[0]) is not None:
        duration_seconds = parse_duration(args[0])
        reason_args = args[1:]
    reason = " ".join(reason_args) if reason_args else "ذکر نشده"

    until_date = None
    duration_display = "نامحدود"
    if duration_seconds:
        until_date = int(time.time()) + duration_seconds
        duration_display = args[0]

    try:
        await context.bot.restrict_chat_member(
            chat_id,
            target.id,
            permissions=ChatPermissions(can_send_messages=False),
            until_date=until_date,
        )
    except Exception as e:
        await update.effective_message.reply_text(f"خطا در سایلنت کردن کاربر: {e}")
        return

    template = db.get_setting(chat_id, "mute_msg")
    text = render_template(
        template,
        user=user_mention(target),
        admin=user_mention(update.effective_user),
        reason=reason,
        duration=duration_display,
        group=update.effective_chat.title or "",
    )
    await update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)


async def unmute_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_admin(update, context) or not await require_bot_admin(update, context):
        return
    target = await get_target_user(update, context)
    if not target:
        await update.effective_message.reply_text("کاربر مشخص نشد.")
        return

    chat_id = update.effective_chat.id
    try:
        await context.bot.restrict_chat_member(
            chat_id,
            target.id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_audios=True,
                can_send_documents=True,
                can_send_photos=True,
                can_send_videos=True,
                can_send_video_notes=True,
                can_send_voice_notes=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
            ),
        )
    except Exception as e:
        await update.effective_message.reply_text(f"خطا: {e}")
        return

    template = db.get_setting(chat_id, "unmute_msg")
    text = render_template(
        template, user=user_mention(target), admin=user_mention(update.effective_user)
    )
    await update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)


async def warn_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_admin(update, context):
        return
    target = await get_target_user(update, context)
    if not target:
        await update.effective_message.reply_text("کاربر مشخص نشد.")
        return

    chat_id = update.effective_chat.id
    was_reply = bool(update.effective_message.reply_to_message)
    reason = get_reason(context, skip_first_arg=not was_reply)
    count = db.add_warn(chat_id, target.id)
    max_warns = db.get_max_warns(chat_id)

    template = db.get_setting(chat_id, "warn_msg")
    text = render_template(
        template,
        user=user_mention(target),
        admin=user_mention(update.effective_user),
        reason=reason,
        warn_count=count,
        max_warns=max_warns,
    )
    await update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)

    if count >= max_warns:
        db.reset_warns(chat_id, target.id)
        if await require_bot_admin(update, context):
            try:
                await context.bot.ban_chat_member(chat_id, target.id)
                await context.bot.unban_chat_member(chat_id, target.id, only_if_banned=False)
                action_template = db.get_setting(chat_id, "maxwarn_action_msg")
                action_text = render_template(action_template, user=user_mention(target))
                await update.effective_message.reply_text(action_text, parse_mode=ParseMode.HTML)
            except Exception as e:
                await update.effective_message.reply_text(f"خطا در حذف خودکار کاربر: {e}")


async def unwarn_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_admin(update, context):
        return
    target = await get_target_user(update, context)
    if not target:
        await update.effective_message.reply_text("کاربر مشخص نشد.")
        return

    chat_id = update.effective_chat.id
    db.remove_warn(chat_id, target.id)
    template = db.get_setting(chat_id, "unwarn_msg")
    text = render_template(
        template, user=user_mention(target), admin=user_mention(update.effective_user)
    )
    await update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)


async def warnings_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = await get_target_user(update, context) or update.effective_user
    chat_id = update.effective_chat.id
    count = db.get_warns(chat_id, target.id)
    max_warns = db.get_max_warns(chat_id)
    await update.effective_message.reply_text(
        f"{user_mention(target)} در حال حاضر {count}/{max_warns} اخطار دارد.",
        parse_mode=ParseMode.HTML,
    )


async def setmaxwarns_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_admin(update, context):
        return
    if not context.args or not context.args[0].isdigit():
        await update.effective_message.reply_text("استفاده: /setmaxwarns <عدد>")
        return
    value = int(context.args[0])
    db.set_max_warns(update.effective_chat.id, value)
    await update.effective_message.reply_text(f"✅ سقف اخطار روی {value} تنظیم شد.")


async def pin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_admin(update, context) or not await require_bot_admin(update, context):
        return
    if not update.effective_message.reply_to_message:
        await update.effective_message.reply_text("روی پیامی که می‌خواهی پین شود ریپلای کن.")
        return
    silent = "silent" in (context.args or [])
    await context.bot.pin_chat_message(
        update.effective_chat.id,
        update.effective_message.reply_to_message.message_id,
        disable_notification=silent,
    )
    await update.effective_message.reply_text("📌 پیام پین شد.")


async def unpin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_admin(update, context) or not await require_bot_admin(update, context):
        return
    await context.bot.unpin_chat_message(update.effective_chat.id)
    await update.effective_message.reply_text("پین برداشته شد.")
