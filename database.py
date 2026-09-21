"""
لایه دیتابیس بات. از SQLite استفاده می‌شود تا نصب و راه‌اندازی ساده بماند.
هر گروه (chat_id) تنظیمات مستقل خودش را دارد: متن‌های سفارشی دستورات،
فیلترهای کلمه، دستورات سفارشی، نوت‌ها، قفل‌ها و تعداد اخطارها.

جدول known_chats برای این است که بدانیم بات در چه گروه‌هایی عضو است، تا در
پنل خصوصی (پیوی) بتوانیم لیست گروه‌هایی که کاربر در آن‌ها ادمین است را نشانش
بدهیم و دیگر نیاز نباشد حتماً از طریق لینک داخل گروه وارد شود.
"""

import sqlite3
import threading
from contextlib import contextmanager

from config import DB_PATH

_local = threading.local()


def _get_conn():
    if not hasattr(_local, "conn"):
        _local.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        _local.conn.row_factory = sqlite3.Row
    return _local.conn


@contextmanager
def get_cursor():
    conn = _get_conn()
    cur = conn.cursor()
    try:
        yield cur
        conn.commit()
    finally:
        cur.close()


DEFAULT_MESSAGES = {
    "welcome_msg": "سلام {user}! به {group} خوش اومدی 🌸",
    "goodbye_msg": "{user} از گروه رفت. خداحافظ 👋",
    "kick_msg": "🚪 {user} توسط {admin} از گروه اخراج شد.\nدلیل: {reason}",
    "ban_msg": "🔨 {user} توسط {admin} بن شد.\nدلیل: {reason}",
    "unban_msg": "✅ {user} توسط {admin} از بن خارج شد.",
    "mute_msg": "🔇 {user} توسط {admin} سایلنت شد.\nمدت: {duration}\nدلیل: {reason}",
    "unmute_msg": "🔊 {user} توسط {admin} از سایلنت خارج شد.",
    "warn_msg": "⚠️ {user} توسط {admin} اخطار گرفت. ({warn_count}/{max_warns})\nدلیل: {reason}",
    "unwarn_msg": "✅ یک اخطار از {user} توسط {admin} حذف شد.",
    "maxwarn_action_msg": "🚫 {user} به سقف اخطار رسید و به‌صورت خودکار حذف شد.",
    "rules": "قوانینی برای این گروه تنظیم نشده است.",
}


def init_db():
    with get_cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_settings (
                chat_id INTEGER PRIMARY KEY,
                welcome_msg TEXT,
                goodbye_msg TEXT,
                kick_msg TEXT,
                ban_msg TEXT,
                unban_msg TEXT,
                mute_msg TEXT,
                unmute_msg TEXT,
                warn_msg TEXT,
                unwarn_msg TEXT,
                maxwarn_action_msg TEXT,
                rules TEXT,
                max_warns INTEGER DEFAULT 3,
                welcome_enabled INTEGER DEFAULT 1,
                goodbye_enabled INTEGER DEFAULT 1,
                antiflood_limit INTEGER DEFAULT 0,
                language TEXT DEFAULT 'fa'
            )
            """
        )
        # مهاجرت نرم: اگر جدول از نسخه قبلی بدون ستون language ساخته شده باشد
        cur.execute("PRAGMA table_info(chat_settings)")
        existing_cols = {row["name"] for row in cur.fetchall()}
        if "language" not in existing_cols:
            cur.execute(
                "ALTER TABLE chat_settings ADD COLUMN language TEXT DEFAULT 'fa'"
            )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS warns (
                chat_id INTEGER,
                user_id INTEGER,
                count INTEGER DEFAULT 0,
                PRIMARY KEY (chat_id, user_id)
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS filters (
                chat_id INTEGER,
                keyword TEXT,
                response TEXT,
                PRIMARY KEY (chat_id, keyword)
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS custom_commands (
                chat_id INTEGER,
                cmd_name TEXT,
                response TEXT,
                PRIMARY KEY (chat_id, cmd_name)
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                chat_id INTEGER,
                note_name TEXT,
                content TEXT,
                PRIMARY KEY (chat_id, note_name)
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS locks (
                chat_id INTEGER,
                lock_type TEXT,
                PRIMARY KEY (chat_id, lock_type)
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS known_chats (
                chat_id INTEGER PRIMARY KEY,
                title TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS action_aliases (
                chat_id INTEGER,
                alias TEXT,
                action TEXT,
                PRIMARY KEY (chat_id, alias)
            )
            """
        )


def ensure_chat(chat_id: int):
    with get_cursor() as cur:
        cur.execute("SELECT chat_id FROM chat_settings WHERE chat_id=?", (chat_id,))
        if cur.fetchone() is None:
            cur.execute(
                "INSERT INTO chat_settings (chat_id) VALUES (?)", (chat_id,)
            )


def get_setting(chat_id: int, key: str):
    ensure_chat(chat_id)
    with get_cursor() as cur:
        cur.execute(f"SELECT {key} FROM chat_settings WHERE chat_id=?", (chat_id,))
        row = cur.fetchone()
        value = row[key] if row else None
        return value if value is not None else DEFAULT_MESSAGES.get(key)


def set_setting(chat_id: int, key: str, value):
    ensure_chat(chat_id)
    with get_cursor() as cur:
        cur.execute(
            f"UPDATE chat_settings SET {key}=? WHERE chat_id=?", (value, chat_id)
        )


def get_max_warns(chat_id: int) -> int:
    ensure_chat(chat_id)
    with get_cursor() as cur:
        cur.execute("SELECT max_warns FROM chat_settings WHERE chat_id=?", (chat_id,))
        row = cur.fetchone()
        return row["max_warns"] if row and row["max_warns"] else 3


def set_max_warns(chat_id: int, value: int):
    ensure_chat(chat_id)
    with get_cursor() as cur:
        cur.execute(
            "UPDATE chat_settings SET max_warns=? WHERE chat_id=?", (value, chat_id)
        )


def get_flag(chat_id: int, key: str) -> bool:
    ensure_chat(chat_id)
    with get_cursor() as cur:
        cur.execute(f"SELECT {key} FROM chat_settings WHERE chat_id=?", (chat_id,))
        row = cur.fetchone()
        return bool(row[key]) if row else True


def set_flag(chat_id: int, key: str, value: bool):
    ensure_chat(chat_id)
    with get_cursor() as cur:
        cur.execute(
            f"UPDATE chat_settings SET {key}=? WHERE chat_id=?",
            (1 if value else 0, chat_id),
        )


# ---------- زبان ----------

def get_language(chat_id: int) -> str:
    ensure_chat(chat_id)
    with get_cursor() as cur:
        cur.execute("SELECT language FROM chat_settings WHERE chat_id=?", (chat_id,))
        row = cur.fetchone()
        return (row["language"] if row and row["language"] else "fa")


def set_language(chat_id: int, lang: str):
    ensure_chat(chat_id)
    with get_cursor() as cur:
        cur.execute(
            "UPDATE chat_settings SET language=? WHERE chat_id=?", (lang, chat_id)
        )


# ---------- warns ----------

def add_warn(chat_id: int, user_id: int) -> int:
    with get_cursor() as cur:
        cur.execute(
            "SELECT count FROM warns WHERE chat_id=? AND user_id=?",
            (chat_id, user_id),
        )
        row = cur.fetchone()
        count = (row["count"] if row else 0) + 1
        cur.execute(
            "INSERT INTO warns (chat_id, user_id, count) VALUES (?, ?, ?) "
            "ON CONFLICT(chat_id, user_id) DO UPDATE SET count=?",
            (chat_id, user_id, count, count),
        )
        return count


def remove_warn(chat_id: int, user_id: int) -> int:
    with get_cursor() as cur:
        cur.execute(
            "SELECT count FROM warns WHERE chat_id=? AND user_id=?",
            (chat_id, user_id),
        )
        row = cur.fetchone()
        count = max(0, (row["count"] if row else 0) - 1)
        cur.execute(
            "INSERT INTO warns (chat_id, user_id, count) VALUES (?, ?, ?) "
            "ON CONFLICT(chat_id, user_id) DO UPDATE SET count=?",
            (chat_id, user_id, count, count),
        )
        return count


def reset_warns(chat_id: int, user_id: int):
    with get_cursor() as cur:
        cur.execute(
            "DELETE FROM warns WHERE chat_id=? AND user_id=?", (chat_id, user_id)
        )


def get_warns(chat_id: int, user_id: int) -> int:
    with get_cursor() as cur:
        cur.execute(
            "SELECT count FROM warns WHERE chat_id=? AND user_id=?",
            (chat_id, user_id),
        )
        row = cur.fetchone()
        return row["count"] if row else 0


# ---------- filters ----------

def add_filter(chat_id: int, keyword: str, response: str):
    with get_cursor() as cur:
        cur.execute(
            "INSERT INTO filters (chat_id, keyword, response) VALUES (?, ?, ?) "
            "ON CONFLICT(chat_id, keyword) DO UPDATE SET response=?",
            (chat_id, keyword.lower(), response, response),
        )


def remove_filter(chat_id: int, keyword: str) -> bool:
    with get_cursor() as cur:
        cur.execute(
            "DELETE FROM filters WHERE chat_id=? AND keyword=?",
            (chat_id, keyword.lower()),
        )
        return cur.rowcount > 0


def get_filters(chat_id: int):
    with get_cursor() as cur:
        cur.execute("SELECT keyword, response FROM filters WHERE chat_id=?", (chat_id,))
        return cur.fetchall()


# ---------- custom commands ----------

def add_custom_command(chat_id: int, name: str, response: str):
    with get_cursor() as cur:
        cur.execute(
            "INSERT INTO custom_commands (chat_id, cmd_name, response) VALUES (?, ?, ?) "
            "ON CONFLICT(chat_id, cmd_name) DO UPDATE SET response=?",
            (chat_id, name.lower(), response, response),
        )


def remove_custom_command(chat_id: int, name: str) -> bool:
    with get_cursor() as cur:
        cur.execute(
            "DELETE FROM custom_commands WHERE chat_id=? AND cmd_name=?",
            (chat_id, name.lower()),
        )
        return cur.rowcount > 0


def get_custom_command(chat_id: int, name: str):
    with get_cursor() as cur:
        cur.execute(
            "SELECT response FROM custom_commands WHERE chat_id=? AND cmd_name=?",
            (chat_id, name.lower()),
        )
        row = cur.fetchone()
        return row["response"] if row else None


def list_custom_commands(chat_id: int):
    with get_cursor() as cur:
        cur.execute(
            "SELECT cmd_name FROM custom_commands WHERE chat_id=?", (chat_id,)
        )
        return [r["cmd_name"] for r in cur.fetchall()]


# ---------- notes ----------

def add_note(chat_id: int, name: str, content: str):
    with get_cursor() as cur:
        cur.execute(
            "INSERT INTO notes (chat_id, note_name, content) VALUES (?, ?, ?) "
            "ON CONFLICT(chat_id, note_name) DO UPDATE SET content=?",
            (chat_id, name.lower(), content, content),
        )


def remove_note(chat_id: int, name: str) -> bool:
    with get_cursor() as cur:
        cur.execute(
            "DELETE FROM notes WHERE chat_id=? AND note_name=?",
            (chat_id, name.lower()),
        )
        return cur.rowcount > 0


def get_note(chat_id: int, name: str):
    with get_cursor() as cur:
        cur.execute(
            "SELECT content FROM notes WHERE chat_id=? AND note_name=?",
            (chat_id, name.lower()),
        )
        row = cur.fetchone()
        return row["content"] if row else None


def list_notes(chat_id: int):
    with get_cursor() as cur:
        cur.execute("SELECT note_name FROM notes WHERE chat_id=?", (chat_id,))
        return [r["note_name"] for r in cur.fetchall()]


# ---------- locks ----------

def set_lock(chat_id: int, lock_type: str, enabled: bool):
    with get_cursor() as cur:
        if enabled:
            cur.execute(
                "INSERT OR IGNORE INTO locks (chat_id, lock_type) VALUES (?, ?)",
                (chat_id, lock_type),
            )
        else:
            cur.execute(
                "DELETE FROM locks WHERE chat_id=? AND lock_type=?",
                (chat_id, lock_type),
            )


def is_locked(chat_id: int, lock_type: str) -> bool:
    with get_cursor() as cur:
        cur.execute(
            "SELECT 1 FROM locks WHERE chat_id=? AND lock_type=?",
            (chat_id, lock_type),
        )
        return cur.fetchone() is not None


def get_locks(chat_id: int):
    with get_cursor() as cur:
        cur.execute("SELECT lock_type FROM locks WHERE chat_id=?", (chat_id,))
        return [r["lock_type"] for r in cur.fetchall()]


# ---------- known_chats (برای پیدا کردن گروه‌ها از پیوی) ----------

def record_chat(chat_id: int, title: str):
    """هر بار بات عضو/ادمین گروهی می‌شود یا از /menu در گروه استفاده می‌شود صدا زده می‌شود."""
    with get_cursor() as cur:
        cur.execute(
            "INSERT INTO known_chats (chat_id, title) VALUES (?, ?) "
            "ON CONFLICT(chat_id) DO UPDATE SET title=?",
            (chat_id, title, title),
        )


def remove_known_chat(chat_id: int):
    with get_cursor() as cur:
        cur.execute("DELETE FROM known_chats WHERE chat_id=?", (chat_id,))


def list_known_chats():
    with get_cursor() as cur:
        cur.execute("SELECT chat_id, title FROM known_chats")
        return cur.fetchall()


def get_chat_title(chat_id: int):
    with get_cursor() as cur:
        cur.execute("SELECT title FROM known_chats WHERE chat_id=?", (chat_id,))
        row = cur.fetchone()
        return row["title"] if row else None


# ---------- action_aliases (میانبرهای متنی برای اقدامات مدیریتی) ----------
# مثال: ادمین کلمه‌ی «اخراج» را به اکشن kick وصل می‌کند؛ از این پس با ریپلای
# روی پیام کسی و نوشتن «اخراج» همان کاری که /kick می‌کرد انجام می‌شود.

def add_alias(chat_id: int, alias: str, action: str):
    with get_cursor() as cur:
        cur.execute(
            "INSERT INTO action_aliases (chat_id, alias, action) VALUES (?, ?, ?) "
            "ON CONFLICT(chat_id, alias) DO UPDATE SET action=?",
            (chat_id, alias.lower(), action, action),
        )


def remove_alias(chat_id: int, alias: str) -> bool:
    with get_cursor() as cur:
        cur.execute(
            "DELETE FROM action_aliases WHERE chat_id=? AND alias=?",
            (chat_id, alias.lower()),
        )
        return cur.rowcount > 0


def get_aliases(chat_id: int):
    with get_cursor() as cur:
        cur.execute(
            "SELECT alias, action FROM action_aliases WHERE chat_id=?", (chat_id,)
        )
        return cur.fetchall()


def get_aliases_for_action(chat_id: int, action: str):
    with get_cursor() as cur:
        cur.execute(
            "SELECT alias FROM action_aliases WHERE chat_id=? AND action=?",
            (chat_id, action),
        )
        return [r["alias"] for r in cur.fetchall()]


def find_action_for_alias(chat_id: int, text: str):
    with get_cursor() as cur:
        cur.execute(
            "SELECT action FROM action_aliases WHERE chat_id=? AND alias=?",
            (chat_id, text.lower()),
        )
        row = cur.fetchone()
        return row["action"] if row else None
