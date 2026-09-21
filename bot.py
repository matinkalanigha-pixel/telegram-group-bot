import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ChatMemberHandler,
    CallbackQueryHandler,
    filters,
)
from telegram.constants import ChatMemberStatus

from config import BOT_TOKEN
import database as db
from handlers import (
    moderation,
    custom_messages,
    custom_commands,
    welcome,
    filters as filter_h,
    locks,
    menu,
    aliases,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start_cmd(update: Update, context):
    # دیپ‌لینک مدیریت در پیوی: t.me/<bot>?start=menu_<chat_id>
    # این لینک از دکمه‌ی «🔐 ادامه در پیوی» زیر منوی گروه ساخته می‌شود.
    args = context.args
    if args and args[0].startswith("menu_"):
        raw = args[0][len("menu_"):]
        try:
            target_chat_id = int(raw)
        except ValueError:
            target_chat_id = None
        if target_chat_id is not None:
            await menu.open_dm_menu(update, context, target_chat_id)
            return

    await update.effective_message.reply_text(
        "سلام! من یک بات مدیریت گروه هستم 🤖\n"
        "من رو به گروهت اضافه کن و ادمین بده تا شروع کنیم.\n"
        "برای دیدن راهنما /help را بزن.\n\n"
        "🔐 اگه ادمین یکی از گروه‌هام هستی، همین‌جا هم می‌تونی /menu رو بزنی "
        "و تنظیمات اون گروه رو از توی پیوی، بدون شلوغی توی گروه، تغییر بدی."
    )


HELP_TEXT = """
📖 راهنمای دستورات

🖲 /menu - باز کردن منوی شیشه‌ای برای تنظیم همه‌چیز با دکمه (متن پیام‌ها، قفل‌ها،
خوش‌آمد/خداحافظی، نوت‌ها، فیلترها، دستورات سفارشی، سقف اخطار، تغییر زبان بات).
از داخل منو می‌تونی با دکمه‌ی «🔐 ادامه در پیوی» همین کار رو تو پیوی بات هم انجام بدی.
همچنین کافیه در پیوی بات هم /menu رو بزنی تا از بین گروه‌هایی که ادمینشونی یکی رو انتخاب کنی.

👮 مدیریت اعضا
/kick <ریپلای یا آیدی> [دلیل] - اخراج
/ban <ریپلای یا آیدی> [دلیل] - بن
/unban <آیدی> - آنبن
/mute <ریپلای یا آیدی> [مدت مثل 1h] [دلیل] - سایلنت
/unmute <ریپلای یا آیدی> - آنمیوت
/warn <ریپلای یا آیدی> [دلیل] - اخطار
/unwarn <ریپلای یا آیدی> - حذف یک اخطار
/warnings [ریپلای] - نمایش تعداد اخطار
/setmaxwarns <عدد> - سقف اخطار قبل از حذف خودکار
/pin [silent] - پین پیام ریپلای‌شده
/unpin - برداشتن پین

✏️ سفارشی‌سازی متن‌ها (فقط ادمین)
/setkickmsg /setbanmsg /setunbanmsg /setmutemsg /setunmutemsg
/setwarnmsg /setunwarnmsg /setmaxwarnactionmsg
/setwelcomemsg /setgoodbyemsg /setrules
هر کدام را با متن دلخواه بزن، مثلاً:
/setkickmsg {user} با لگد رفت بیرون! توسط {admin}
پلیس‌هولدرهای مجاز: {user} {admin} {reason} {group} {duration} {warn_count} {max_warns}
/showmessages - نمایش همه متن‌های فعلی
/resetmsg <کلید> - بازگشت یک متن به پیش‌فرض

🛠 دستورات سفارشی نامحدود
/setcmd <نام> <پاسخ> - ساخت دستور جدید مثل /setcmd rules قوانین گروه...
/delcmd <نام> - حذف دستور سفارشی
/commands - لیست دستورات سفارشی

🔍 فیلتر کلمات
/filter <کلمه> <پاسخ> - وقتی کلمه گفته شد بات پاسخ بدهد
/stopfilter <کلمه> - حذف فیلتر
/filters - لیست فیلترها

🔒 قفل محتوا
/lock <link|photo|video|sticker|gif|forward|voice|document>
/unlock <نوع>
/locks - لیست قفل‌های فعال

🗒 نوت‌ها
/note <نام> <محتوا> - ذخیره نوت
/delnote <نام> - حذف نوت
/notes - لیست نوت‌ها
بعد با #نام قابل فراخوانی است.

👋 خوش‌آمدگویی
/togglewelcome - فعال/غیرفعال کردن پیام خوش‌آمد
/togglegoodbye - فعال/غیرفعال کردن پیام خداحافظی
/rules - نمایش قوانین گروه

⚡ میانبر دستورات (بدون نیاز به /kick و ...)
از داخل /menu -> «⚡ میانبرهای دستورات» می‌تونی برای اخراج، بن، سایلنت، اخطار
و... یک کلمه‌ی دلخواه فارسی تعریف کنی. بعدش کافیه با ریپلای روی پیام فرد،
همون کلمه رو بنویسی تا همون کار انجام بشه.
"""


async def help_cmd(update: Update, context):
    await update.effective_message.reply_text(HELP_TEXT)


async def track_chat_membership(update: Update, context):
    """
    هر بار وضعیت عضویت بات در یک چت تغییر کند این هندلر اجرا می‌شود (اضافه شدن،
    ادمین شدن، حذف شدن، ترک گروه و ...). این‌طور می‌توانیم لیست گروه‌هایی که
    بات در آن‌هاست را برای پنل خصوصی (پیوی) به‌روز نگه داریم.
    """
    result = update.my_chat_member
    if not result:
        return
    chat = result.chat
    new_status = result.new_chat_member.status
    if new_status in (ChatMemberStatus.LEFT, ChatMemberStatus.BANNED):
        db.remove_known_chat(chat.id)
    else:
        db.record_chat(chat.id, chat.title or "")


async def error_handler(update: object, context):
    """
    یک هندلر خطای سراسری: هر خطایی که داخل هیچ‌کدام از هندلرها گرفته نشده
    باشد، اینجا لاگ می‌شود تا به‌جای «هیچ اتفاقی نیفتاد و سکوت»، در لاگ سرور
    مشخص باشد دقیقاً چه چیزی و کجا خراب شده.
    """
    logger.error("خطای پیش‌بینی‌نشده هنگام پردازش یک آپدیت:", exc_info=context.error)


def main():
    db.init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    # دستورات پایه
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))

    # ردیابی عضویت بات در گروه‌ها (برای پنل خصوصی/پیوی)
    app.add_handler(ChatMemberHandler(track_chat_membership, ChatMemberHandler.MY_CHAT_MEMBER))

    # مدیریت اعضا
    app.add_handler(CommandHandler("kick", moderation.kick_cmd))
    app.add_handler(CommandHandler("ban", moderation.ban_cmd))
    app.add_handler(CommandHandler("unban", moderation.unban_cmd))
    app.add_handler(CommandHandler("mute", moderation.mute_cmd))
    app.add_handler(CommandHandler("unmute", moderation.unmute_cmd))
    app.add_handler(CommandHandler("warn", moderation.warn_cmd))
    app.add_handler(CommandHandler("unwarn", moderation.unwarn_cmd))
    app.add_handler(CommandHandler("warnings", moderation.warnings_cmd))
    app.add_handler(CommandHandler("setmaxwarns", moderation.setmaxwarns_cmd))
    app.add_handler(CommandHandler("pin", moderation.pin_cmd))
    app.add_handler(CommandHandler("unpin", moderation.unpin_cmd))

    # منوی شیشه‌ای (هم در گروه، هم در پیوی کار می‌کند)
    app.add_handler(CommandHandler("menu", menu.menu_cmd))
    app.add_handler(CallbackQueryHandler(menu.menu_callback, pattern="^menu_"))
    # گرفتن متن ورودی ادمین برای منو - باید قبل از فیلترها/دستورات سفارشی اجرا شود
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, menu.capture_pending_text),
        group=0,
    )

    # سفارشی‌سازی متن‌ها
    for cmd_name, (db_key, label) in custom_messages.SETTABLE_MESSAGES.items():
        app.add_handler(
            CommandHandler(cmd_name, custom_messages.make_setter(db_key, label))
        )
    app.add_handler(CommandHandler("showmessages", custom_messages.show_messages_cmd))
    app.add_handler(CommandHandler("resetmsg", custom_messages.resetmsg_cmd))

    # دستورات سفارشی نامحدود
    app.add_handler(CommandHandler("setcmd", custom_commands.setcmd_cmd))
    app.add_handler(CommandHandler("delcmd", custom_commands.delcmd_cmd))
    app.add_handler(CommandHandler("commands", custom_commands.list_custom_commands_cmd))

    # فیلترها
    app.add_handler(CommandHandler("filter", filter_h.filter_cmd))
    app.add_handler(CommandHandler("stopfilter", filter_h.stopfilter_cmd))
    app.add_handler(CommandHandler("filters", filter_h.list_filters_cmd))

    # قفل‌ها
    app.add_handler(CommandHandler("lock", locks.lock_cmd))
    app.add_handler(CommandHandler("unlock", locks.unlock_cmd))
    app.add_handler(CommandHandler("locks", locks.list_locks_cmd))

    # نوت‌ها
    app.add_handler(CommandHandler("note", locks.savenote_cmd))
    app.add_handler(CommandHandler("delnote", locks.delnote_cmd))
    app.add_handler(CommandHandler("notes", locks.list_notes_cmd))

    # خوش‌آمدگویی و قوانین
    app.add_handler(CommandHandler("togglewelcome", welcome.togglewelcome_cmd))
    app.add_handler(CommandHandler("togglegoodbye", welcome.togglegoodbye_cmd))
    app.add_handler(CommandHandler("rules", welcome.rules_cmd))
    app.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome.greet_new_members)
    )
    app.add_handler(
        MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, welcome.farewell_member)
    )

    # اجرای قفل‌ها روی هر پیام (باید قبل از دیسپچرهای متنی باشد)
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, locks.enforce_locks), group=1)

    # میانبرهای متنی اقدامات مدیریتی (مثلاً «اخراج» به‌جای /kick)
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, aliases.dispatch_alias), group=2
    )

    # فیلتر کلمات روی پیام‌های متنی معمولی
    # نکته‌ی مهم: هر گروه هندلر در python-telegram-bot فقط اولین هندلر منطبقش
    # را اجرا می‌کند. چون apply_filters و hashtag_note_dispatcher هر دو روی
    # «هر پیام متنیِ غیر دستور» تطبیق پیدا می‌کنند، اگر هر دو در یک گروه باشند
    # فقط اولی همیشه اجرا می‌شود و دومی هیچ‌وقت صدا زده نمی‌شود. برای همین
    # هرکدام گروه جداگانه‌ی خودش را دارد.
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, filter_h.apply_filters), group=3
    )
    # نوت‌ها با #نام
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, locks.hashtag_note_dispatcher),
        group=4,
    )

    # دیسپچر دستورات سفارشی ادمین‌ساخته (باید آخرین هندلر دستورات باشد)
    app.add_handler(
        MessageHandler(filters.COMMAND, custom_commands.dynamic_command_dispatcher),
        group=5,
    )

    app.add_error_handler(error_handler)

    logger.info("بات در حال اجراست...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
