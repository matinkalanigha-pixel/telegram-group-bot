"""
منوی شیشه‌ای (Inline Keyboard) برای مدیریت گروه بدون نیاز به حفظ دستورات.

این نسخه از دو جا قابل استفاده است:
  1) داخل خود گروه، با زدن /menu (مثل قبل).
  2) در پیوی خود بات:
       - یا با زدن دکمه‌ی «🔐 ادامه در پیوی» زیر منوی گروه (که کاربر را با یک
         دیپ‌لینک /start menu_<chat_id> به پیوی می‌فرستد)،
       - یا مستقیم با زدن /menu در پیوی، که در این حالت لیست گروه‌هایی که
         کاربر در آن‌ها ادمین است و بات هم عضوشان هست نشان داده می‌شود تا
         انتخاب کند.

«چت هدف» (گروهی که تنظیماتش دارد عوض می‌شود) در context.user_data ذخیره
می‌شود. چون user_data برای هر کاربر یکتاست (نه هر چت)، همین مقدار هم در گروه
و هم در پیوی برای همان ادمین در دسترس است و امکان جابه‌جایی بین گروه و پیوی
را فراهم می‌کند.

برای گرفتن ورودی متنی (مثل متن جدید یک پیام، یا نام+محتوای یک نوت/فیلتر/
دستور سفارشی جدید)، وضعیت «در انتظار ورودی» در context.user_data ذخیره
می‌شود؛ اولین پیام متنی بعدی از همان ادمین (چه در گروه، چه در پیوی) گرفته
و پردازش می‌شود.
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ApplicationHandlerStop
from telegram.constants import ParseMode

import database as db
from locales import t, LANGUAGES, SUPPORTED_LANGUAGES
from .utils import require_admin, is_admin_of_chat
from .custom_messages import SETTABLE_MESSAGES
from .custom_commands import RESERVED_NAMES
from .locks import LOCK_TYPES
from .aliases import ACTION_ORDER

# هر متنِ قابل‌ویرایش چه پلیس‌هولدرهایی را می‌پذیرد؛ برای ساختن راهنمای دقیق
# هنگام درخواست متن جدید استفاده می‌شود.
PLACEHOLDERS_BY_KEY = {
    "kick_msg": ["user", "admin", "reason", "group"],
    "ban_msg": ["user", "admin", "reason", "group"],
    "unban_msg": ["user", "admin"],
    "mute_msg": ["user", "admin", "reason", "duration", "group"],
    "unmute_msg": ["user", "admin"],
    "warn_msg": ["user", "admin", "reason", "warn_count", "max_warns"],
    "unwarn_msg": ["user", "admin"],
    "maxwarn_action_msg": ["user"],
    "welcome_msg": ["user", "group"],
    "goodbye_msg": ["user", "group"],
    "rules": [],
}

# کلیدهای context.user_data
TARGET_CHAT_KEY = "menu_target_chat_id"     # چت (گروه) هدفی که در حال تنظیم آن هستیم
AWAITING_TYPE = "menu_awaiting_type"        # "message" | "note_add" | "filter_add" | "cmd_add"
AWAITING_FIELD = "menu_awaiting_field"      # فقط برای نوع "message": کلید دیتابیس
AWAITING_CHAT = "menu_awaiting_chat"        # چت هدفی که ورودی برایش ذخیره می‌شود


# ---------------------------------------------------------------------------
# دکمه‌های عمومی
# ---------------------------------------------------------------------------

def _close_button(chat_id):
    return InlineKeyboardButton(t(chat_id, "menu_btn_close"), callback_data="menu_close")


def _back_button(chat_id, target="menu_main"):
    return InlineKeyboardButton(t(chat_id, "menu_btn_back"), callback_data=target)


def _clear_awaiting(context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop(AWAITING_TYPE, None)
    context.user_data.pop(AWAITING_FIELD, None)
    context.user_data.pop(AWAITING_CHAT, None)


def _get_target_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """چت هدف فعلی را برمی‌گرداند. در گروه، همیشه همان گروه است (و ذخیره می‌شود
    تا بعداً در پیوی هم در دسترس باشد). در پیوی، آخرین چتی است که کاربر انتخاب کرده."""
    if update.effective_chat.type == "private":
        return context.user_data.get(TARGET_CHAT_KEY)
    context.user_data[TARGET_CHAT_KEY] = update.effective_chat.id
    return update.effective_chat.id


def _main_markup_for_update(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> InlineKeyboardMarkup:
    if update.effective_chat.type == "private":
        extra = InlineKeyboardButton(t(chat_id, "menu_btn_switch_group"), callback_data="menu_switch")
    else:
        bot_username = context.bot.username
        dm_url = f"https://t.me/{bot_username}?start=menu_{chat_id}"
        extra = InlineKeyboardButton(t(chat_id, "menu_btn_open_dm"), url=dm_url)
    return main_menu_markup(chat_id, extra_button=extra)


# ---------------------------------------------------------------------------
# ساخت منوها
# ---------------------------------------------------------------------------

def main_menu_markup(chat_id: int, extra_button: InlineKeyboardButton = None) -> InlineKeyboardMarkup:
    rows = []
    if extra_button:
        rows.append([extra_button])
    rows += [
        [InlineKeyboardButton(t(chat_id, "menu_btn_messages"), callback_data="menu_msgs")],
        [InlineKeyboardButton(t(chat_id, "menu_btn_locks"), callback_data="menu_locks")],
        [InlineKeyboardButton(t(chat_id, "menu_btn_toggles"), callback_data="menu_toggles")],
        [InlineKeyboardButton(t(chat_id, "menu_btn_notes"), callback_data="menu_notes")],
        [InlineKeyboardButton(t(chat_id, "menu_btn_filters"), callback_data="menu_filters")],
        [InlineKeyboardButton(t(chat_id, "menu_btn_customcmds"), callback_data="menu_cmds")],
        [InlineKeyboardButton(t(chat_id, "menu_btn_aliases"), callback_data="menu_aliases")],
        [InlineKeyboardButton(t(chat_id, "menu_btn_warns"), callback_data="menu_warns")],
        [InlineKeyboardButton(t(chat_id, "menu_btn_language"), callback_data="menu_lang")],
        [InlineKeyboardButton(t(chat_id, "menu_btn_help"), callback_data="menu_help")],
        [_close_button(chat_id)],
    ]
    return InlineKeyboardMarkup(rows)


def messages_menu_markup(chat_id: int) -> InlineKeyboardMarkup:
    rows = []
    row = []
    for i, (cmd_name, (db_key, _label)) in enumerate(SETTABLE_MESSAGES.items()):
        label = t(chat_id, f"msg_label_{db_key}")
        row.append(InlineKeyboardButton(label, callback_data=f"menu_msg_{db_key}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([_back_button(chat_id), _close_button(chat_id)])
    return InlineKeyboardMarkup(rows)


def locks_menu_markup(chat_id: int) -> InlineKeyboardMarkup:
    active = set(db.get_locks(chat_id))
    rows = []
    row = []
    for lock_type in LOCK_TYPES:
        name = t(chat_id, f"lock_name_{lock_type}")
        key = "lock_on" if lock_type in active else "lock_off"
        label = t(chat_id, key, name=name)
        row.append(InlineKeyboardButton(label, callback_data=f"menu_lock_{lock_type}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([_back_button(chat_id), _close_button(chat_id)])
    return InlineKeyboardMarkup(rows)


def toggles_menu_markup(chat_id: int) -> InlineKeyboardMarkup:
    welcome_on = db.get_flag(chat_id, "welcome_enabled")
    goodbye_on = db.get_flag(chat_id, "goodbye_enabled")
    rows = [
        [InlineKeyboardButton(
            t(chat_id, "toggle_welcome_on" if welcome_on else "toggle_welcome_off"),
            callback_data="menu_toggle_welcome_enabled",
        )],
        [InlineKeyboardButton(
            t(chat_id, "toggle_goodbye_on" if goodbye_on else "toggle_goodbye_off"),
            callback_data="menu_toggle_goodbye_enabled",
        )],
        [_back_button(chat_id), _close_button(chat_id)],
    ]
    return InlineKeyboardMarkup(rows)


def warns_menu_markup(chat_id: int) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(t(chat_id, "btn_decrease"), callback_data="menu_warns_dec"),
            InlineKeyboardButton(t(chat_id, "btn_increase"), callback_data="menu_warns_inc"),
        ],
        [_back_button(chat_id), _close_button(chat_id)],
    ]
    return InlineKeyboardMarkup(rows)


def language_menu_markup(chat_id: int) -> InlineKeyboardMarkup:
    current = db.get_language(chat_id)
    rows = []
    for lang_code in SUPPORTED_LANGUAGES:
        name = LANGUAGES[lang_code]["lang_name"]
        prefix = "✅ " if lang_code == current else ""
        rows.append([InlineKeyboardButton(prefix + name, callback_data=f"menu_lang_{lang_code}")])
    rows.append([_back_button(chat_id), _close_button(chat_id)])
    return InlineKeyboardMarkup(rows)


def _items_menu_markup(chat_id: int, items, del_prefix: str, add_data: str) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(f"🗑 {name}", callback_data=f"{del_prefix}{name}")] for name in items]
    rows.append([InlineKeyboardButton(t(chat_id, "btn_add_new"), callback_data=add_data)])
    rows.append([_back_button(chat_id), _close_button(chat_id)])
    return InlineKeyboardMarkup(rows)


def _cancel_markup(chat_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton(t(chat_id, "btn_cancel"), callback_data="menu_cancel_input")]])


def _placeholder_hint(chat_id: int, db_key: str) -> str:
    placeholders = PLACEHOLDERS_BY_KEY.get(db_key, ["user", "admin", "reason", "group"])
    if not placeholders:
        return t(chat_id, "no_placeholders")
    lines = [f"{{{p}}} = " + t(chat_id, f"ph_{p}") for p in placeholders]
    return "\n".join(lines)


def aliases_menu_markup(chat_id: int) -> InlineKeyboardMarkup:
    rows = []
    for action in ACTION_ORDER:
        label = t(chat_id, f"action_label_{action}")
        current = db.get_aliases_for_action(chat_id, action)
        suffix = f" ({', '.join(current)})" if current else ""
        rows.append([InlineKeyboardButton(label + suffix, callback_data=f"menu_alias_open_{action}")])
    rows.append([_back_button(chat_id), _close_button(chat_id)])
    return InlineKeyboardMarkup(rows)


def alias_action_markup(chat_id: int, action: str) -> InlineKeyboardMarkup:
    aliases_list = db.get_aliases_for_action(chat_id, action)
    rows = [
        [InlineKeyboardButton(f"🗑 {a}", callback_data=f"menu_alias_del_{action}:{a}")]
        for a in aliases_list
    ]
    rows.append([InlineKeyboardButton(t(chat_id, "btn_add_new"), callback_data=f"menu_alias_add_{action}")])
    rows.append([_back_button(chat_id, "menu_aliases"), _close_button(chat_id)])
    return InlineKeyboardMarkup(rows)


# ---------------------------------------------------------------------------
# انتخاب گروه از پیوی
# ---------------------------------------------------------------------------

async def _show_group_picker(update: Update, context: ContextTypes.DEFAULT_TYPE, edit: bool = False):
    lang_ctx = update.effective_chat.id  # قبل از انتخاب گروه، زبان را از روی خودِ چت پیوی می‌خوانیم
    user_id = update.effective_user.id
    known = db.list_known_chats()
    rows = []
    for row in known:
        cid, title = row["chat_id"], row["title"]
        if await is_admin_of_chat(context, cid, user_id):
            rows.append([InlineKeyboardButton(title or str(cid), callback_data=f"menu_pick_{cid}")])

    if not rows:
        text = t(lang_ctx, "no_managed_groups")
        markup = None
    else:
        text = t(lang_ctx, "pick_group_title")
        rows.append([_close_button(lang_ctx)])
        markup = InlineKeyboardMarkup(rows)

    if edit:
        await update.callback_query.edit_message_text(text, reply_markup=markup)
    else:
        await update.effective_message.reply_text(text, reply_markup=markup)


async def open_dm_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    """از /start menu_<chat_id> در پیوی صدا زده می‌شود."""
    user_id = update.effective_user.id
    if not await is_admin_of_chat(context, chat_id, user_id):
        await update.effective_message.reply_text(t(chat_id, "not_admin_of_group"))
        return
    context.user_data[TARGET_CHAT_KEY] = chat_id
    title = db.get_chat_title(chat_id) or str(chat_id)
    text = t(chat_id, "menu_title") + "\n" + t(chat_id, "dm_menu_active_group", group=title)
    await update.effective_message.reply_text(text, reply_markup=_main_markup_for_update(update, context, chat_id))


# ---------------------------------------------------------------------------
# دستورات
# ---------------------------------------------------------------------------

async def menu_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat

    if chat.type == "private":
        target = context.user_data.get(TARGET_CHAT_KEY)
        if target and not await is_admin_of_chat(context, target, update.effective_user.id):
            target = None
            context.user_data.pop(TARGET_CHAT_KEY, None)
        if not target:
            await _show_group_picker(update, context)
            return
        title = db.get_chat_title(target) or str(target)
        text = t(target, "menu_title") + "\n" + t(target, "dm_menu_active_group", group=title)
        await update.effective_message.reply_text(text, reply_markup=_main_markup_for_update(update, context, target))
        return

    if not await require_admin(update, context):
        return
    db.record_chat(chat.id, chat.title or "")
    context.user_data[TARGET_CHAT_KEY] = chat.id
    await update.effective_message.reply_text(
        t(chat.id, "menu_title"), reply_markup=_main_markup_for_update(update, context, chat.id)
    )


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id

    if data == "menu_close":
        await query.answer()
        try:
            await query.message.delete()
        except Exception:
            pass
        return

    if data == "menu_switch":
        await query.answer()
        context.user_data.pop(TARGET_CHAT_KEY, None)
        await _show_group_picker(update, context, edit=True)
        return

    if data.startswith("menu_pick_"):
        try:
            picked_chat_id = int(data[len("menu_pick_"):])
        except ValueError:
            await query.answer()
            return
        if not await is_admin_of_chat(context, picked_chat_id, user_id):
            await query.answer(t(update.effective_chat.id, "not_admin_of_group"), show_alert=True)
            return
        await query.answer()
        context.user_data[TARGET_CHAT_KEY] = picked_chat_id
        title = db.get_chat_title(picked_chat_id) or str(picked_chat_id)
        text = t(picked_chat_id, "menu_title") + "\n" + t(picked_chat_id, "dm_menu_active_group", group=title)
        await query.edit_message_text(text, reply_markup=_main_markup_for_update(update, context, picked_chat_id))
        return

    # از این‌جا به بعد به یک چت هدف مشخص نیاز داریم
    chat_id = _get_target_chat(update, context)
    if not chat_id:
        await query.answer()
        await _show_group_picker(update, context, edit=True)
        return

    if not await is_admin_of_chat(context, chat_id, user_id):
        await query.answer(t(chat_id, "admin_only"), show_alert=True)
        return
    await query.answer()

    if data == "menu_main":
        title = db.get_chat_title(chat_id) or str(chat_id)
        text = t(chat_id, "menu_title")
        if update.effective_chat.type == "private":
            text += "\n" + t(chat_id, "dm_menu_active_group", group=title)
        await query.edit_message_text(text, reply_markup=_main_markup_for_update(update, context, chat_id))
        return

    # ----- متن پیام‌ها -----
    if data == "menu_msgs":
        await query.edit_message_text(
            t(chat_id, "messages_menu_title"), reply_markup=messages_menu_markup(chat_id)
        )
        return

    if data.startswith("menu_msg_"):
        db_key = data[len("menu_msg_"):]
        label = t(chat_id, f"msg_label_{db_key}")
        context.user_data[AWAITING_TYPE] = "message"
        context.user_data[AWAITING_FIELD] = db_key
        context.user_data[AWAITING_CHAT] = chat_id
        current = db.get_setting(chat_id, db_key)
        hint = _placeholder_hint(chat_id, db_key)
        await query.edit_message_text(
            t(chat_id, "send_new_text_dynamic", label=label, current=current, hint=hint),
            reply_markup=_cancel_markup(chat_id),
        )
        return

    if data == "menu_cancel_input":
        _clear_awaiting(context)
        await query.edit_message_text(t(chat_id, "input_cancelled"))
        return

    # ----- قفل‌ها -----
    if data == "menu_locks":
        await query.edit_message_text(
            t(chat_id, "locks_menu_title"), reply_markup=locks_menu_markup(chat_id)
        )
        return

    if data.startswith("menu_lock_"):
        lock_type = data[len("menu_lock_"):]
        currently_on = lock_type in db.get_locks(chat_id)
        db.set_lock(chat_id, lock_type, not currently_on)
        await query.edit_message_text(
            t(chat_id, "locks_menu_title"), reply_markup=locks_menu_markup(chat_id)
        )
        return

    # ----- خوش‌آمد/خداحافظی -----
    if data == "menu_toggles":
        await query.edit_message_text(
            t(chat_id, "toggles_menu_title"), reply_markup=toggles_menu_markup(chat_id)
        )
        return

    if data.startswith("menu_toggle_"):
        flag_key = data[len("menu_toggle_"):]
        new_value = not db.get_flag(chat_id, flag_key)
        db.set_flag(chat_id, flag_key, new_value)
        await query.edit_message_text(
            t(chat_id, "toggles_menu_title"), reply_markup=toggles_menu_markup(chat_id)
        )
        return

    # ----- نوت‌ها -----
    if data == "menu_notes":
        names = db.list_notes(chat_id)
        text = t(chat_id, "notes_menu_title") if names else t(chat_id, "notes_empty")
        await query.edit_message_text(
            text, reply_markup=_items_menu_markup(chat_id, names, "menu_notes_del_", "menu_notes_add")
        )
        return

    if data == "menu_notes_add":
        context.user_data[AWAITING_TYPE] = "note_add"
        context.user_data[AWAITING_CHAT] = chat_id
        await query.edit_message_text(t(chat_id, "ask_new_note"), reply_markup=_cancel_markup(chat_id))
        return

    if data.startswith("menu_notes_del_"):
        name = data[len("menu_notes_del_"):]
        db.remove_note(chat_id, name)
        names = db.list_notes(chat_id)
        text = t(chat_id, "notes_menu_title") if names else t(chat_id, "notes_empty")
        await query.edit_message_text(
            text, reply_markup=_items_menu_markup(chat_id, names, "menu_notes_del_", "menu_notes_add")
        )
        return

    # ----- فیلترها -----
    if data == "menu_filters":
        names = [r["keyword"] for r in db.get_filters(chat_id)]
        text = t(chat_id, "filters_menu_title") if names else t(chat_id, "filters_empty")
        await query.edit_message_text(
            text, reply_markup=_items_menu_markup(chat_id, names, "menu_filters_del_", "menu_filters_add")
        )
        return

    if data == "menu_filters_add":
        context.user_data[AWAITING_TYPE] = "filter_add"
        context.user_data[AWAITING_CHAT] = chat_id
        await query.edit_message_text(t(chat_id, "ask_new_filter"), reply_markup=_cancel_markup(chat_id))
        return

    if data.startswith("menu_filters_del_"):
        keyword = data[len("menu_filters_del_"):]
        db.remove_filter(chat_id, keyword)
        names = [r["keyword"] for r in db.get_filters(chat_id)]
        text = t(chat_id, "filters_menu_title") if names else t(chat_id, "filters_empty")
        await query.edit_message_text(
            text, reply_markup=_items_menu_markup(chat_id, names, "menu_filters_del_", "menu_filters_add")
        )
        return

    # ----- دستورات سفارشی -----
    if data == "menu_cmds":
        names = db.list_custom_commands(chat_id)
        text = t(chat_id, "customcmds_menu_title") if names else t(chat_id, "customcmds_empty")
        await query.edit_message_text(
            text, reply_markup=_items_menu_markup(chat_id, names, "menu_cmds_del_", "menu_cmds_add")
        )
        return

    if data == "menu_cmds_add":
        context.user_data[AWAITING_TYPE] = "cmd_add"
        context.user_data[AWAITING_CHAT] = chat_id
        await query.edit_message_text(t(chat_id, "ask_new_cmd"), reply_markup=_cancel_markup(chat_id))
        return

    if data.startswith("menu_cmds_del_"):
        name = data[len("menu_cmds_del_"):]
        db.remove_custom_command(chat_id, name)
        names = db.list_custom_commands(chat_id)
        text = t(chat_id, "customcmds_menu_title") if names else t(chat_id, "customcmds_empty")
        await query.edit_message_text(
            text, reply_markup=_items_menu_markup(chat_id, names, "menu_cmds_del_", "menu_cmds_add")
        )
        return

    # ----- میانبرهای دستورات -----
    if data == "menu_aliases":
        await query.edit_message_text(
            t(chat_id, "aliases_menu_title"), reply_markup=aliases_menu_markup(chat_id)
        )
        return

    if data.startswith("menu_alias_open_"):
        action = data[len("menu_alias_open_"):]
        label = t(chat_id, f"action_label_{action}")
        await query.edit_message_text(
            t(chat_id, "alias_action_title", label=label),
            reply_markup=alias_action_markup(chat_id, action),
        )
        return

    if data.startswith("menu_alias_add_"):
        action = data[len("menu_alias_add_"):]
        context.user_data[AWAITING_TYPE] = "alias_add"
        context.user_data[AWAITING_FIELD] = action
        context.user_data[AWAITING_CHAT] = chat_id
        label = t(chat_id, f"action_label_{action}")
        await query.edit_message_text(
            t(chat_id, "ask_new_alias", label=label), reply_markup=_cancel_markup(chat_id)
        )
        return

    if data.startswith("menu_alias_del_"):
        remainder = data[len("menu_alias_del_"):]
        action, _, alias = remainder.partition(":")
        db.remove_alias(chat_id, alias)
        label = t(chat_id, f"action_label_{action}")
        await query.edit_message_text(
            t(chat_id, "alias_action_title", label=label),
            reply_markup=alias_action_markup(chat_id, action),
        )
        return

    # ----- راهنما -----
    if data == "menu_help":
        rows = [[_back_button(chat_id), _close_button(chat_id)]]
        await query.edit_message_text(
            t(chat_id, "help_text"), reply_markup=InlineKeyboardMarkup(rows)
        )
        return

    # ----- سقف اخطار -----
    if data == "menu_warns":
        value = db.get_max_warns(chat_id)
        await query.edit_message_text(
            t(chat_id, "warns_menu_title", value=value), reply_markup=warns_menu_markup(chat_id)
        )
        return

    if data in ("menu_warns_inc", "menu_warns_dec"):
        value = db.get_max_warns(chat_id)
        value = value + 1 if data == "menu_warns_inc" else max(1, value - 1)
        db.set_max_warns(chat_id, value)
        await query.edit_message_text(
            t(chat_id, "warns_menu_title", value=value), reply_markup=warns_menu_markup(chat_id)
        )
        return

    # ----- زبان -----
    if data == "menu_lang":
        await query.edit_message_text(
            t(chat_id, "language_menu_title"), reply_markup=language_menu_markup(chat_id)
        )
        return

    if data.startswith("menu_lang_"):
        lang_code = data[len("menu_lang_"):]
        if lang_code in SUPPORTED_LANGUAGES:
            db.set_language(chat_id, lang_code)
        await query.edit_message_text(
            t(chat_id, "language_set"), reply_markup=_main_markup_for_update(update, context, chat_id)
        )
        return


async def capture_pending_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    اگر ادمینی از منو خواسته بود متن/نوت/فیلتر/دستوری بفرستد، این هندلر آن پیام
    را می‌گیرد، در دیتابیس ذخیره می‌کند و جلوی پردازش پیام توسط سایر هندلرها
    (مثل فیلترها یا دستورات سفارشی) را می‌گیرد.

    برای امنیت: اگر ادمین در حال ویرایش تنظیمات یک گروه است، فقط متنی که در
    خودِ همان گروه یا در پیوی بات فرستاده شود پذیرفته می‌شود - نه در گروه
    دیگری که به‌طور اتفاقی همان لحظه باز کرده.
    """
    message = update.effective_message
    if not message or not message.text:
        return

    awaiting_type = context.user_data.get(AWAITING_TYPE)
    target_chat = context.user_data.get(AWAITING_CHAT)
    if not awaiting_type or not target_chat:
        return

    current_chat = update.effective_chat
    if current_chat.type != "private" and current_chat.id != target_chat:
        return

    user_id = update.effective_user.id
    if not await is_admin_of_chat(context, target_chat, user_id):
        return

    text = message.text.strip()

    if awaiting_type == "message":
        db_key = context.user_data.get(AWAITING_FIELD)
        db.set_setting(target_chat, db_key, message.text)
        label = t(target_chat, f"msg_label_{db_key}")
        _clear_awaiting(context)
        await message.reply_text(t(target_chat, "text_updated", label=label))
        raise ApplicationHandlerStop

    if awaiting_type in ("note_add", "filter_add", "cmd_add"):
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            await message.reply_text(t(target_chat, "invalid_add_format"))
            raise ApplicationHandlerStop
        name, content = parts[0], parts[1]

        if awaiting_type == "note_add":
            db.add_note(target_chat, name, content)
            reply_key = "note_added"
        elif awaiting_type == "filter_add":
            db.add_filter(target_chat, name, content)
            reply_key = "filter_added"
        else:  # cmd_add
            if name.lstrip("/").lower() in RESERVED_NAMES:
                await message.reply_text(t(target_chat, "cmd_reserved"))
                raise ApplicationHandlerStop
            db.add_custom_command(target_chat, name, content)
            reply_key = "cmd_added"

        _clear_awaiting(context)
        await message.reply_text(t(target_chat, reply_key, name=name.lower()))
        raise ApplicationHandlerStop

    if awaiting_type == "alias_add":
        action = context.user_data.get(AWAITING_FIELD)
        alias_word = text.split()[0] if text.split() else ""
        if not alias_word or alias_word.startswith("/"):
            await message.reply_text(t(target_chat, "invalid_add_format"))
            raise ApplicationHandlerStop
        db.add_alias(target_chat, alias_word, action)
        label = t(target_chat, f"action_label_{action}")
        _clear_awaiting(context)
        await message.reply_text(t(target_chat, "alias_added", alias=alias_word.lower(), label=label))
        raise ApplicationHandlerStop
