"""
سیستم چندزبانه ساده. هر گروه یک زبان مستقل دارد (پیش‌فرض فارسی).
برای اضافه کردن زبان جدید کافیست یک دیکشنری جدید مثل "fa" و "en" اضافه کنی
و کلیدهای همان را کامل کنی؛ اگر کلیدی جا بیفتد، به‌صورت خودکار از فارسی خوانده می‌شود.
"""

import database as db

LANGUAGES = {
    "fa": {
        "lang_name": "🇮🇷 فارسی",
        "admin_only": "⛔ این دستور فقط برای ادمین‌های گروه است.",
        "bot_not_admin": (
            "⛔ من هنوز در این گروه ادمین نیستم. لطفاً ابتدا من را ادمین کن و "
            "دسترسی‌های لازم را فعال کن."
        ),
        "user_not_specified": "کاربر مشخص نشد. روی پیام فرد ریپلای کن یا آیدی عددی‌اش را بده.",

        "menu_title": "⚙️ پنل مدیریت گروه\nاز دکمه‌های زیر برای تنظیم بات استفاده کن:",
        "menu_btn_messages": "💬 متن پیام‌ها",
        "menu_btn_locks": "🔒 قفل‌ها",
        "menu_btn_toggles": "👋 خوش‌آمد/خداحافظی",
        "menu_btn_warns": "⚠️ سقف اخطار",
        "menu_btn_language": "🌐 زبان",
        "menu_btn_close": "❌ بستن",
        "menu_btn_back": "🔙 بازگشت",
        "menu_btn_open_dm": "🔐 ادامه در پیوی",
        "menu_btn_switch_group": "🔁 تغییر گروه",
        "menu_btn_notes": "🗒 نوت‌ها",
        "menu_btn_filters": "🔍 فیلترها",
        "menu_btn_customcmds": "🛠 دستورات سفارشی",
        "menu_btn_aliases": "⚡ میانبرهای دستورات",
        "menu_btn_help": "❓ راهنما",

        "messages_menu_title": "💬 روی هر پیام بزن تا متنش را عوض کنی:",
        "send_new_text": (
            "✏️ متن جدید برای «{label}» را بفرست.\n"
            "پلیس‌هولدرهای مجاز: {{user}} {{admin}} {{reason}} {{group}}\n\n"
            "برای انصراف روی دکمه لغو بزن."
        ),
        "send_new_text_dynamic": (
            "✏️ متن جدید برای «{label}» را بفرست.\n"
            "متن فعلی:\n{current}\n\n"
            "پلیس‌هولدرهای قابل استفاده در این متن:\n{hint}\n\n"
            "کافیه همون کلمه رو داخل جمله‌ات بذاری، بات خودش موقع ارسال جایگزینش می‌کنه.\n"
            "برای انصراف روی دکمه لغو بزن."
        ),
        "no_placeholders": "این متن پلیس‌هولدر خاصی نداره، هرچی دوست داری بنویس.",
        "ph_user": "منشن کاربر هدف (کسی که اکشن روش اجرا شده)",
        "ph_admin": "منشن ادمینی که دستور را زده",
        "ph_reason": "دلیلی که ادمین موقع دستور نوشته (اگر ننویسد: «ذکر نشده»)",
        "ph_group": "نام گروه",
        "ph_duration": "مدت‌زمان سایلنت (مثل 1h)، فقط برای پیام میوت",
        "ph_warn_count": "تعداد اخطار فعلی کاربر، فقط برای پیام اخطار",
        "ph_max_warns": "سقف اخطار این گروه، فقط برای پیام اخطار",
        "btn_cancel": "🚫 لغو",
        "btn_add_new": "➕ افزودن جدید",
        "text_updated": "✅ متن «{label}» با موفقیت به‌روزرسانی شد.",
        "input_cancelled": "❌ عملیات لغو شد.",
        "invalid_add_format": "❌ فرمت درست نیست. یک بار دیگر به‌شکل «نام محتوا» بفرست یا لغو کن.",

        "locks_menu_title": "🔒 برای فعال/غیرفعال کردن قفل روی آن بزن:",
        "lock_on": "✅ {name}",
        "lock_off": "⬜ {name}",

        "toggles_menu_title": "👋 پیام‌های ورود و خروج اعضا:",
        "toggle_welcome_on": "✅ خوش‌آمدگویی فعال",
        "toggle_welcome_off": "⬜ خوش‌آمدگویی غیرفعال",
        "toggle_goodbye_on": "✅ خداحافظی فعال",
        "toggle_goodbye_off": "⬜ خداحافظی غیرفعال",

        "warns_menu_title": "⚠️ سقف فعلی اخطار قبل از حذف خودکار: {value}",
        "btn_increase": "➕ افزایش",
        "btn_decrease": "➖ کاهش",

        "language_menu_title": "🌐 زبان بات برای این گروه را انتخاب کن:",
        "language_set": "✅ زبان به فارسی تغییر کرد.",

        "lock_name_link": "لینک",
        "lock_name_photo": "عکس",
        "lock_name_video": "ویدیو",
        "lock_name_sticker": "استیکر",
        "lock_name_gif": "گیف",
        "lock_name_forward": "فوروارد",
        "lock_name_voice": "ویس",
        "lock_name_document": "فایل",

        "msg_label_kick_msg": "پیام اخراج",
        "msg_label_ban_msg": "پیام بن",
        "msg_label_unban_msg": "پیام آنبن",
        "msg_label_mute_msg": "پیام سایلنت",
        "msg_label_unmute_msg": "پیام آنمیوت",
        "msg_label_warn_msg": "پیام اخطار",
        "msg_label_unwarn_msg": "پیام حذف اخطار",
        "msg_label_maxwarn_action_msg": "پیام رسیدن به سقف اخطار",
        "msg_label_welcome_msg": "پیام خوش‌آمدگویی",
        "msg_label_goodbye_msg": "پیام خداحافظی",
        "msg_label_rules": "قوانین گروه",

        "notes_menu_title": "🗒 نوت‌های این گروه (برای حذف روی نوت بزن):",
        "notes_empty": "هنوز نوتی ثبت نشده. با دکمه‌ی زیر یکی اضافه کن.",
        "ask_new_note": (
            "✏️ نام و محتوای نوت را این‌طور در یک پیام بفرست:\n"
            "‌<نام> <محتوا>\n"
            "مثال: faq سوالات متداول اینجاست...\n\n"
            "برای انصراف روی دکمه لغو بزن."
        ),
        "note_added": "✅ نوت «{name}» ذخیره شد. با #{name} در گروه قابل مشاهده است.",
        "note_deleted": "✅ نوت «{name}» حذف شد.",

        "filters_menu_title": "🔍 فیلترهای این گروه (برای حذف روی کلمه بزن):",
        "filters_empty": "هنوز فیلتری تعریف نشده. با دکمه‌ی زیر یکی اضافه کن.",
        "ask_new_filter": (
            "✏️ کلمه و پاسخ را این‌طور در یک پیام بفرست:\n"
            "<کلمه> <پاسخ>\n"
            "مثال: تبلیغ تبلیغات ممنوع است!\n\n"
            "برای انصراف روی دکمه لغو بزن."
        ),
        "filter_added": "✅ فیلتر «{name}» ثبت شد.",
        "filter_deleted": "✅ فیلتر «{name}» حذف شد.",

        "customcmds_menu_title": "🛠 دستورات سفارشی این گروه (برای حذف روی دستور بزن):",
        "customcmds_empty": "هنوز دستور سفارشی‌ای ساخته نشده. با دکمه‌ی زیر یکی بساز.",
        "ask_new_cmd": (
            "✏️ نام دستور و پاسخش را این‌طور در یک پیام بفرست:\n"
            "<نام> <پاسخ>\n"
            "مثال: rules قوانین گروه اینجاست...\n\n"
            "برای انصراف روی دکمه لغو بزن."
        ),
        "cmd_added": "✅ دستور /{name} ساخته شد.",
        "cmd_deleted": "✅ دستور /{name} حذف شد.",
        "cmd_reserved": "⛔ این نام رزرو شده و قابل استفاده نیست، نام دیگری انتخاب کن.",

        "pick_group_title": "📋 مدیریت کدام گروه را می‌خواهی از اینجا انجام بدهی؟",
        "no_managed_groups": (
            "هیچ گروهی پیدا نشد که تو در آن ادمین باشی و بات هم عضوش باشد.\n\n"
            "برای شروع، داخل گروه‌ات دستور /menu را بزن و از دکمه‌ی «ادامه در پیوی» استفاده کن."
        ),
        "not_admin_of_group": "⛔ تو دیگر ادمین این گروه نیستی یا بات دیگر در آن عضو نیست.",
        "dm_menu_active_group": "📍 گروه فعال: {group}",

        "aliases_menu_title": (
            "⚡ برای هر اکشن، به‌جای دستور انگلیسی (مثل /kick) می‌تونی یک یا چند "
            "کلمه‌ی دلخواه فارسی تعریف کنی. بعدش کافیه با ریپلای روی پیام کاربر "
            "همون کلمه رو بنویسی تا همون کار انجام بشه:"
        ),
        "alias_action_title": "{label}\nمیانبرهای فعلی (برای حذف روی هرکدوم بزن):",
        "ask_new_alias": (
            "✏️ یک کلمه برای «{label}» بفرست (بدون فاصله و بدون /).\n"
            "بعدش کافیه ادمین با ریپلای روی پیام یک نفر همین کلمه رو بنویسه تا "
            "«{label}» روی اون فرد اجرا بشه.\n"
            "مثال برای اخراج: اخراج یا برو\n\n"
            "برای انصراف روی دکمه لغو بزن."
        ),
        "alias_added": "✅ میانبر «{alias}» برای «{label}» ثبت شد. کافیه با ریپلای بنویسی: {alias}",

        "action_label_kick": "🚪 اخراج (کیک)",
        "action_label_ban": "🔨 بن",
        "action_label_unban": "✅ آنبن",
        "action_label_mute": "🔇 سایلنت (میوت)",
        "action_label_unmute": "🔊 آنمیوت",
        "action_label_warn": "⚠️ اخطار",
        "action_label_unwarn": "➖ حذف اخطار",
        "action_label_pin": "📌 پین",
        "action_label_unpin": "📍 آنپین",

        "help_text": (
            "❓ راهنمای پنل مدیریت\n\n"
            "💬 متن پیام‌ها: متنی که برای هر اکشن (اخراج، بن، خوش‌آمد و...) "
            "نشون داده می‌شه رو عوض می‌کنه. هر متن یک‌سری پلیس‌هولدر مثل "
            "{user} یا {reason} داره که موقع ارسال با اطلاعات واقعی جایگزین "
            "می‌شن؛ لیست دقیق پلیس‌هولدرهای هر متن، همون لحظه که روی دکمه‌اش "
            "می‌زنی نشونت داده می‌شه.\n\n"
            "🔒 قفل‌ها: جلوی ارسال نوع خاصی از محتوا (لینک، عکس، ویدیو و...) "
            "توسط کاربرای عادی رو می‌گیره. ادمین‌ها از قفل‌ها معافن.\n\n"
            "🗒 نوت‌ها / 🔍 فیلترها / 🛠 دستورات سفارشی: برای افزودن، روی «افزودن "
            "جدید» بزن و یک پیام به‌شکل «نام محتوا» بفرست (مثلاً: faq سوالات "
            "متداول اینجاست...). نوت‌ها با #نام، فیلترها با گفتن همون کلمه، و "
            "دستورات سفارشی با /نام قابل فراخوانی‌ان.\n\n"
            "⚡ میانبرهای دستورات: به‌جای /kick و بقیه‌ی دستورات انگلیسی، یک "
            "کلمه‌ی دلخواه فارسی تعریف کن. بعدش با ریپلای روی پیام کسی و "
            "نوشتن همون کلمه، همون اکشن اجرا می‌شه.\n\n"
            "🔐 پیوی: با دکمه‌ی «ادامه در پیوی» یا با زدن /menu در پیوی بات، "
            "همین پنل رو بدون شلوغی توی گروه، خصوصی مدیریت کن."
        ),
    },
    "en": {
        "lang_name": "🇬🇧 English",
        "admin_only": "⛔ This command is for group admins only.",
        "bot_not_admin": (
            "⛔ I'm not an admin in this group yet. Please make me an admin "
            "with the required permissions first."
        ),
        "user_not_specified": "No user specified. Reply to their message or give a numeric ID.",

        "menu_title": "⚙️ Group Admin Panel\nUse the buttons below to configure the bot:",
        "menu_btn_messages": "💬 Message Texts",
        "menu_btn_locks": "🔒 Locks",
        "menu_btn_toggles": "👋 Welcome/Goodbye",
        "menu_btn_warns": "⚠️ Max Warns",
        "menu_btn_language": "🌐 Language",
        "menu_btn_close": "❌ Close",
        "menu_btn_back": "🔙 Back",
        "menu_btn_open_dm": "🔐 Continue in DM",
        "menu_btn_switch_group": "🔁 Switch group",
        "menu_btn_notes": "🗒 Notes",
        "menu_btn_filters": "🔍 Filters",
        "menu_btn_customcmds": "🛠 Custom Commands",
        "menu_btn_aliases": "⚡ Command Shortcuts",
        "menu_btn_help": "❓ Help",

        "messages_menu_title": "💬 Tap a message to change its text:",
        "send_new_text": (
            "✏️ Send the new text for \"{label}\".\n"
            "Allowed placeholders: {{user}} {{admin}} {{reason}} {{group}}\n\n"
            "Tap Cancel to abort."
        ),
        "send_new_text_dynamic": (
            "✏️ Send the new text for \"{label}\".\n"
            "Current text:\n{current}\n\n"
            "Placeholders you can use in this text:\n{hint}\n\n"
            "Just put the placeholder anywhere in your sentence — the bot fills it in when sending.\n"
            "Tap Cancel to abort."
        ),
        "no_placeholders": "This text has no special placeholders, write anything you like.",
        "ph_user": "mention of the target user (the one the action was taken on)",
        "ph_admin": "mention of the admin who ran the command",
        "ph_reason": "the reason the admin typed (\"not specified\" if none)",
        "ph_group": "the group's name",
        "ph_duration": "the mute duration (e.g. 1h), mute message only",
        "ph_warn_count": "the user's current warn count, warn message only",
        "ph_max_warns": "this group's max warns, warn message only",
        "btn_cancel": "🚫 Cancel",
        "btn_add_new": "➕ Add new",
        "text_updated": "✅ \"{label}\" was updated successfully.",
        "input_cancelled": "❌ Cancelled.",
        "invalid_add_format": "❌ Wrong format. Send it as \"name content\" again, or cancel.",

        "locks_menu_title": "🔒 Tap to enable/disable a lock:",
        "lock_on": "✅ {name}",
        "lock_off": "⬜ {name}",

        "toggles_menu_title": "👋 Join/leave messages:",
        "toggle_welcome_on": "✅ Welcome enabled",
        "toggle_welcome_off": "⬜ Welcome disabled",
        "toggle_goodbye_on": "✅ Goodbye enabled",
        "toggle_goodbye_off": "⬜ Goodbye disabled",

        "warns_menu_title": "⚠️ Current max warns before auto-remove: {value}",
        "btn_increase": "➕ Increase",
        "btn_decrease": "➖ Decrease",

        "language_menu_title": "🌐 Choose the bot's language for this group:",
        "language_set": "✅ Language changed to English.",

        "lock_name_link": "Link",
        "lock_name_photo": "Photo",
        "lock_name_video": "Video",
        "lock_name_sticker": "Sticker",
        "lock_name_gif": "GIF",
        "lock_name_forward": "Forward",
        "lock_name_voice": "Voice",
        "lock_name_document": "Document",

        "msg_label_kick_msg": "Kick message",
        "msg_label_ban_msg": "Ban message",
        "msg_label_unban_msg": "Unban message",
        "msg_label_mute_msg": "Mute message",
        "msg_label_unmute_msg": "Unmute message",
        "msg_label_warn_msg": "Warn message",
        "msg_label_unwarn_msg": "Unwarn message",
        "msg_label_maxwarn_action_msg": "Max-warn action message",
        "msg_label_welcome_msg": "Welcome message",
        "msg_label_goodbye_msg": "Goodbye message",
        "msg_label_rules": "Group rules",

        "notes_menu_title": "🗒 Notes in this group (tap one to delete):",
        "notes_empty": "No notes yet. Add one with the button below.",
        "ask_new_note": (
            "✏️ Send the note name and content in one message:\n"
            "<name> <content>\n"
            "Example: faq Here are the FAQs...\n\n"
            "Tap Cancel to abort."
        ),
        "note_added": "✅ Note \"{name}\" saved. Call it with #{name} in the group.",
        "note_deleted": "✅ Note \"{name}\" deleted.",

        "filters_menu_title": "🔍 Filters in this group (tap one to delete):",
        "filters_empty": "No filters yet. Add one with the button below.",
        "ask_new_filter": (
            "✏️ Send the keyword and the reply in one message:\n"
            "<keyword> <reply>\n"
            "Example: spam Advertising is not allowed here!\n\n"
            "Tap Cancel to abort."
        ),
        "filter_added": "✅ Filter \"{name}\" saved.",
        "filter_deleted": "✅ Filter \"{name}\" deleted.",

        "customcmds_menu_title": "🛠 Custom commands in this group (tap one to delete):",
        "customcmds_empty": "No custom commands yet. Create one with the button below.",
        "ask_new_cmd": (
            "✏️ Send the command name and its reply in one message:\n"
            "<name> <reply>\n"
            "Example: rules Here are the group rules...\n\n"
            "Tap Cancel to abort."
        ),
        "cmd_added": "✅ Command /{name} created.",
        "cmd_deleted": "✅ Command /{name} deleted.",
        "cmd_reserved": "⛔ This name is reserved, pick another one.",

        "pick_group_title": "📋 Which group's settings do you want to manage here?",
        "no_managed_groups": (
            "No groups found where you're an admin and the bot is also a member.\n\n"
            "To get started, run /menu inside your group and use the \"Continue in DM\" button."
        ),
        "not_admin_of_group": "⛔ You're no longer an admin of that group, or the bot left it.",
        "dm_menu_active_group": "📍 Active group: {group}",

        "aliases_menu_title": (
            "⚡ For each action, instead of an English command (like /kick) you can "
            "define one or more custom words. Then just reply to a user's message "
            "with that word to trigger the same action:"
        ),
        "alias_action_title": "{label}\nCurrent shortcuts (tap one to delete):",
        "ask_new_alias": (
            "✏️ Send one word for \"{label}\" (no spaces, no /).\n"
            "Afterwards, an admin can reply to someone's message with that exact "
            "word to trigger \"{label}\" on them.\n"
            "Example for kick: kickout or gtfo\n\n"
            "Tap Cancel to abort."
        ),
        "alias_added": "✅ Shortcut \"{alias}\" linked to \"{label}\". Just reply with: {alias}",

        "action_label_kick": "🚪 Kick",
        "action_label_ban": "🔨 Ban",
        "action_label_unban": "✅ Unban",
        "action_label_mute": "🔇 Mute",
        "action_label_unmute": "🔊 Unmute",
        "action_label_warn": "⚠️ Warn",
        "action_label_unwarn": "➖ Unwarn",
        "action_label_pin": "📌 Pin",
        "action_label_unpin": "📍 Unpin",

        "help_text": (
            "❓ Admin panel help\n\n"
            "💬 Message Texts: change what gets shown for each action (kick, ban, "
            "welcome, etc). Each text has its own set of placeholders like {user} "
            "or {reason} that get filled in automatically when sent; the exact list "
            "for each text is shown right when you tap it.\n\n"
            "🔒 Locks: block regular members from sending a certain type of content "
            "(link, photo, video, etc). Admins are exempt from locks.\n\n"
            "🗒 Notes / 🔍 Filters / 🛠 Custom Commands: tap \"Add new\" and send one "
            "message shaped like \"name content\" (e.g. faq Here are the FAQs...). "
            "Notes are called with #name, filters trigger on that word, and custom "
            "commands are called with /name.\n\n"
            "⚡ Command Shortcuts: instead of /kick and the other English commands, "
            "define a custom word. Then reply to someone's message with that word "
            "to run the same action.\n\n"
            "🔐 DM: use the \"Continue in DM\" button, or run /menu in the bot's DM, "
            "to manage this same panel privately without cluttering the group."
        ),
    },
}

SUPPORTED_LANGUAGES = list(LANGUAGES.keys())


def t(chat_id: int, key: str, **kwargs) -> str:
    lang = db.get_language(chat_id)
    table = LANGUAGES.get(lang, LANGUAGES["fa"])
    template = table.get(key) or LANGUAGES["fa"].get(key, key)
    if kwargs:
        try:
            return template.format(**kwargs)
        except (KeyError, IndexError):
            return template
    return template
