"""
توابع کمکی مشترک بین همه‌ی هندلرها:
- چک کردن ادمین بودن فرستنده و بات
- پیدا کردن کاربر هدف (از روی ریپلای، یوزرنیم یا آیدی عددی)
- جایگزینی پلیس‌هولدرهای متن سفارشی مثل {user} {admin} {reason}
"""

from telegram import Update, ChatMember
from telegram.ext import ContextTypes
from telegram.constants import ChatMemberStatus
from telegram.helpers import mention_html

from locales import t


async def is_user_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    try:
        member = await context.bot.get_chat_member(update.effective_chat.id, user_id)
        return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
    except Exception:
        return False


async def is_admin_of_chat(context: ContextTypes.DEFAULT_TYPE, chat_id: int, user_id: int) -> bool:
    """
    مثل is_user_admin ولی به‌جای اینکه از update.effective_chat استفاده کند،
    chat_id را صریح می‌گیرد. لازم است چون در پنل خصوصی (پیوی)، effective_chat
    همان چت خصوصی کاربر با بات است، نه گروهی که داریم تنظیماتش را عوض می‌کنیم.
    """
    try:
        member = await context.bot.get_chat_member(chat_id, user_id)
        return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
    except Exception:
        return False


async def require_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """اگر فرستنده پیام ادمین گروه نباشد، پیام خطا می‌فرستد و False برمی‌گرداند."""
    user = update.effective_user
    if not await is_user_admin(update, context, user.id):
        await update.effective_message.reply_text(t(update.effective_chat.id, "admin_only"))
        return False
    return True


async def require_bot_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """اطمینان از اینکه خود بات در گروه ادمین است و اجازه‌ی لازم برای اقدام را دارد."""
    bot_member = await context.bot.get_chat_member(
        update.effective_chat.id, context.bot.id
    )
    if bot_member.status != ChatMemberStatus.ADMINISTRATOR:
        await update.effective_message.reply_text(t(update.effective_chat.id, "bot_not_admin"))
        return False
    return True


class _ResolvedUser:
    """
    یک آبجکت سبک شبیه telegram.User، برای زمانی که کاربر را فقط از روی
    یوزرنیم (نه ریپلای یا آیدی عددی) پیدا کرده‌ایم. get_chat روی یوزرنیم،
    آبجکت Chat برمی‌گرداند نه User؛ Chat فیلد full_name ندارد، برای همین
    اینجا یک نسخه‌ی سازگار با user_mention() می‌سازیم.
    """

    def __init__(self, chat):
        self.id = chat.id
        self.first_name = chat.first_name or (chat.username or str(chat.id))
        self.last_name = chat.last_name

    @property
    def full_name(self) -> str:
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name


async def get_target_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    کاربر هدف را از روی ریپلای پیام، آیدی عددی یا یوزرنیم (@user) پیدا می‌کند.
    خروجی: آبجکت User (یا معادل آن) یا None.
    """
    message = update.effective_message
    if message.reply_to_message:
        return message.reply_to_message.from_user

    if context.args:
        arg = context.args[0]
        if arg.startswith("@"):
            # فقط برای یوزرنیم‌های عمومی کار می‌کند (تلگرام یوزرنیم خصوصی را
            # جستجو نمی‌دهد مگر اینکه کاربر قبلاً در چتی با بات دیده شده باشد).
            try:
                chat = await context.bot.get_chat(arg)
            except Exception:
                return None
            if chat.type != "private":
                return None
            return _ResolvedUser(chat)
        try:
            user_id = int(arg)
        except ValueError:
            return None
        try:
            member = await context.bot.get_chat_member(update.effective_chat.id, user_id)
            return member.user
        except Exception:
            return None
    return None


def get_reason(context: ContextTypes.DEFAULT_TYPE, skip_first_arg: bool = False) -> str:
    args = context.args or []
    if skip_first_arg and args:
        args = args[1:]
    return " ".join(args) if args else "ذکر نشده"


def render_template(template: str, **kwargs) -> str:
    """جایگزینی امن پلیس‌هولدرها؛ اگر کلیدی موجود نباشد کرش نمی‌کند."""
    class SafeDict(dict):
        def __missing__(self, key):
            return "{" + key + "}"

    return template.format_map(SafeDict(**kwargs))


def user_mention(user) -> str:
    return mention_html(user.id, user.full_name)

