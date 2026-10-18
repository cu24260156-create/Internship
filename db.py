import os
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "internship_assistant.db"


def get_db():
    """Get a connection with row factory enabled."""
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables and indexes safely without dropping existing data."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_db() as conn:
        cursor = conn.cursor()

        # 1. Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                google_id TEXT,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                picture TEXT,
                created_at TEXT NOT NULL
            )
        """)

        # 2. Chat sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)

        # 3. Messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                text TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES chat_sessions (id) ON DELETE CASCADE
            )
        """)

        # 4. User settings & custom instructions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                user_id TEXT PRIMARY KEY,
                theme TEXT DEFAULT 'system',
                language TEXT DEFAULT 'en',
                answer_style TEXT DEFAULT 'detailed',
                default_category TEXT DEFAULT 'fullstack',
                preferred_categories TEXT DEFAULT '["fullstack","python","java","javascript"]',
                experience_level TEXT DEFAULT 'beginner',
                career_goals TEXT DEFAULT '',
                current_skills TEXT DEFAULT '',
                desired_skills TEXT DEFAULT '',
                learning_style TEXT DEFAULT 'practical',
                daily_learning_time TEXT DEFAULT '1-2 hours',
                custom_instructions TEXT DEFAULT '',
                response_guidelines TEXT DEFAULT '',
                memory_enabled INTEGER DEFAULT 1,
                enter_to_send INTEGER DEFAULT 1,
                delete_confirmation INTEGER DEFAULT 1,
                font_size TEXT DEFAULT 'medium',
                high_contrast INTEGER DEFAULT 0,
                reduced_motion INTEGER DEFAULT 0,
                notifications_enabled INTEGER DEFAULT 1,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)

        # Safe column migrations for existing user_settings
        cursor.execute("PRAGMA table_info(user_settings)")
        existing_cols = {row["name"] for row in cursor.fetchall()}
        migration_cols = [
            ("preferred_categories", "TEXT DEFAULT '[\"fullstack\",\"python\",\"java\",\"javascript\"]'"),
            ("experience_level", "TEXT DEFAULT 'beginner'"),
            ("career_goals", "TEXT DEFAULT ''"),
            ("current_skills", "TEXT DEFAULT ''"),
            ("desired_skills", "TEXT DEFAULT ''"),
            ("learning_style", "TEXT DEFAULT 'practical'"),
            ("daily_learning_time", "TEXT DEFAULT '1-2 hours'"),
            ("custom_instructions", "TEXT DEFAULT ''"),
            ("response_guidelines", "TEXT DEFAULT ''"),
            ("memory_enabled", "INTEGER DEFAULT 1"),
            ("delete_confirmation", "INTEGER DEFAULT 1"),
            ("font_size", "TEXT DEFAULT 'medium'"),
            ("high_contrast", "INTEGER DEFAULT 0"),
            ("reduced_motion", "INTEGER DEFAULT 0"),
            ("notifications_enabled", "INTEGER DEFAULT 1")
        ]
        for col_name, col_def in migration_cols:
            if col_name not in existing_cols:
                try:
                    cursor.execute(f"ALTER TABLE user_settings ADD COLUMN {col_name} {col_def}")
                except Exception:
                    pass

        # 5. User memory items (opt-in remembered details)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)

        # 6. Skill and Roadmap progress tracker
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skill_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                category TEXT NOT NULL,
                skill_name TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Not Started',
                updated_at TEXT NOT NULL,
                UNIQUE(user_id, category, skill_name),
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)

        # 7. Internship Bookmarks
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookmarks (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                company TEXT NOT NULL,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                category TEXT NOT NULL,
                notes TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)

        # 8. Application Tracker records
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                company TEXT NOT NULL,
                role TEXT NOT NULL,
                url TEXT NOT NULL,
                category TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Saved',
                application_date TEXT,
                deadline TEXT,
                follow_up_date TEXT,
                notes TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)

        # 9. Reminders and deadlines
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                reminder_type TEXT NOT NULL,
                due_date TEXT NOT NULL,
                is_completed INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)

        # Safe migrations for interview_scores
        cursor.execute("PRAGMA table_info(interview_scores)")
        existing_scores_cols = {row["name"] for row in cursor.fetchall()}
        if "total" not in existing_scores_cols:
            try:
                cursor.execute("ALTER TABLE interview_scores ADD COLUMN total INTEGER DEFAULT 10")
            except Exception:
                pass
        if "feedback" not in existing_scores_cols:
            try:
                cursor.execute("ALTER TABLE interview_scores ADD COLUMN feedback TEXT DEFAULT ''")
            except Exception:
                pass

        # Indexes for fast lookup
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user ON chat_sessions (user_id, updated_at DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_session ON messages (session_id, id ASC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_skill_user ON skill_progress (user_id, category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_bookmarks_user ON bookmarks (user_id, created_at DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_apps_user ON applications (user_id, updated_at DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_reminders_user ON reminders (user_id, due_date ASC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_interview_user ON interview_scores (user_id, completed_at DESC)")

        conn.commit()


# --------------------------------------------------
# User Profile Operations
# --------------------------------------------------

def get_or_create_user(google_id, email, name, picture=""):
    """Fetch an existing user by email or create a new user profile."""
    now = datetime.utcnow().isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()

        if row:
            cursor.execute("""
                UPDATE users SET name = ?, picture = ?, google_id = COALESCE(?, google_id)
                WHERE email = ?
            """, (name, picture, google_id, email))
            conn.commit()
            return dict(row)

        user_id = f"usr_{uuid.uuid4().hex[:12]}"
        cursor.execute("""
            INSERT INTO users (id, google_id, email, name, picture, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, google_id, email, name, picture, now))
        conn.commit()

        # Initialize default settings for user
        cursor.execute("""
            INSERT OR IGNORE INTO user_settings (user_id, updated_at)
            VALUES (?, ?)
        """, (user_id, now))
        conn.commit()

        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return dict(cursor.fetchone())


def get_user_by_id(user_id):
    """Fetch user by primary key id."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


# --------------------------------------------------
# Chat Sessions & Messages
# --------------------------------------------------

def create_chat_session(user_id, title="New Conversation"):
    """Create a new chat session for a user."""
    session_id = f"sess_{uuid.uuid4().hex[:16]}"
    now = datetime.utcnow().isoformat()

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO chat_sessions (id, user_id, title, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (session_id, user_id, title, now, now))
        conn.commit()

        cursor.execute("SELECT * FROM chat_sessions WHERE id = ?", (session_id,))
        return dict(cursor.fetchone())


def get_user_sessions(user_id):
    """Retrieve all chat sessions for a user, sorted newest first."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.*, 
                   (SELECT text FROM messages WHERE session_id = s.id ORDER BY id DESC LIMIT 1) as last_message,
                   (SELECT COUNT(*) FROM messages WHERE session_id = s.id) as message_count
            FROM chat_sessions s
            WHERE s.user_id = ?
            ORDER BY s.updated_at DESC
        """, (user_id,))
        return [dict(row) for row in cursor.fetchall()]


def get_session_messages(session_id):
    """Fetch all messages for a given session."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, role, text, created_at
            FROM messages
            WHERE session_id = ?
            ORDER BY id ASC
        """, (session_id,))
        return [dict(row) for row in cursor.fetchall()]


def save_message(session_id, role, text):
    """Save a single message and update the session's timestamp."""
    now = datetime.utcnow().isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO messages (session_id, role, text, created_at)
            VALUES (?, ?, ?, ?)
        """, (session_id, role, text, now))

        cursor.execute("""
            UPDATE chat_sessions
            SET updated_at = ?
            WHERE id = ?
        """, (now, session_id))
        conn.commit()


def rename_session(session_id, user_id, new_title):
    """Rename a session, ensuring ownership."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE chat_sessions
            SET title = ?, updated_at = ?
            WHERE id = ? AND user_id = ?
        """, (new_title, datetime.utcnow().isoformat(), session_id, user_id))
        conn.commit()
        return cursor.rowcount > 0


def delete_session(session_id, user_id):
    """Delete a session and all its messages."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM chat_sessions WHERE id = ? AND user_id = ?", (session_id, user_id))
        if not cursor.fetchone():
            return False

        cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        cursor.execute("DELETE FROM chat_sessions WHERE id = ? AND user_id = ?", (session_id, user_id))
        conn.commit()
        return True


def clear_all_user_sessions(user_id):
    """Delete all chat sessions and messages for a user."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM chat_sessions WHERE user_id = ?", (user_id,))
        session_ids = [row["id"] for row in cursor.fetchall()]
        if session_ids:
            placeholders = ",".join(["?"] * len(session_ids))
            cursor.execute(f"DELETE FROM messages WHERE session_id IN ({placeholders})", session_ids)
            cursor.execute("DELETE FROM chat_sessions WHERE user_id = ?", (user_id,))
            conn.commit()
        return True


def search_user_history(user_id, query):
    """Search user's past chat history messages for a keyword."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.id, m.session_id, m.role, m.text, m.created_at, s.title as session_title
            FROM messages m
            JOIN chat_sessions s ON m.session_id = s.id
            WHERE s.user_id = ? AND m.text LIKE ?
            ORDER BY m.id DESC
            LIMIT 10
        """, (user_id, f"%{query}%"))
        return [dict(row) for row in cursor.fetchall()]


# --------------------------------------------------
# Settings & Personalization Operations
# --------------------------------------------------

def get_user_settings(user_id):
    """Retrieve settings for user, returning defaults if not found."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_settings WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)

        now = datetime.utcnow().isoformat()
        cursor.execute("""
            INSERT OR IGNORE INTO user_settings (user_id, updated_at)
            VALUES (?, ?)
        """, (user_id, now))
        conn.commit()

        cursor.execute("SELECT * FROM user_settings WHERE user_id = ?", (user_id,))
        return dict(cursor.fetchone())


def save_user_settings(user_id, settings_dict):
    """Update user settings fields."""
    now = datetime.utcnow().isoformat()
    fields = [
        "theme", "language", "answer_style", "default_category",
        "preferred_categories", "experience_level", "career_goals",
        "current_skills", "desired_skills", "learning_style",
        "daily_learning_time", "custom_instructions", "response_guidelines",
        "memory_enabled", "enter_to_send", "delete_confirmation",
        "font_size", "high_contrast", "reduced_motion", "notifications_enabled"
    ]

    updates = []
    values = []
    for f in fields:
        if f in settings_dict:
            updates.append(f"{f} = ?")
            values.append(settings_dict[f])

    if not updates:
        return get_user_settings(user_id)

    updates.append("updated_at = ?")
    values.append(now)
    values.append(user_id)

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE user_settings SET {', '.join(updates)} WHERE user_id = ?", values)
        conn.commit()
        return get_user_settings(user_id)


# --------------------------------------------------
# User Memory (Opt-in Remembered Preferences)
# --------------------------------------------------

def get_user_memory(user_id):
    """Get all saved memory items for user."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_memory WHERE user_id = ? ORDER BY id ASC", (user_id,))
        return [dict(row) for row in cursor.fetchall()]


def add_user_memory(user_id, key, value, category="preference"):
    """Add a memory item."""
    now = datetime.utcnow().isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_memory (user_id, key, value, created_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, key, value, now))
        conn.commit()
        return cursor.lastrowid


def delete_user_memory(arg1, arg2=None):
    """Delete a single memory item ensuring user ownership. Accepts (user_id, memory_id) or (memory_id, user_id)."""
    with get_db() as conn:
        cursor = conn.cursor()
        if arg2 is not None:
            # Check if arg1 is user_id (string like usr_...) or int
            if isinstance(arg1, str) and arg1.startswith("usr_"):
                user_id, memory_id = arg1, arg2
            else:
                memory_id, user_id = arg1, arg2
            cursor.execute("DELETE FROM user_memory WHERE id = ? AND user_id = ?", (memory_id, user_id))
        else:
            cursor.execute("DELETE FROM user_memory WHERE id = ?", (arg1,))
        conn.commit()
        return cursor.rowcount > 0


def clear_user_memory(user_id):
    """Clear all memory items for a user."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_memory WHERE user_id = ?", (user_id,))
        conn.commit()
        return True


# --------------------------------------------------
# Skill Progress Tracker
# --------------------------------------------------

def get_user_skill_progress(user_id, category=None):
    """Get skill progress records for user, optionally filtered by category."""
    with get_db() as conn:
        cursor = conn.cursor()
        if category:
            cursor.execute("""
                SELECT * FROM skill_progress WHERE user_id = ? AND category = ?
                ORDER BY skill_name ASC
            """, (user_id, category))
        else:
            cursor.execute("""
                SELECT * FROM skill_progress WHERE user_id = ?
                ORDER BY category ASC, skill_name ASC
            """, (user_id,))
        return [dict(row) for row in cursor.fetchall()]


def update_skill_progress(user_id, category, skill_name, status):
    """Update or insert skill progress."""
    now = datetime.utcnow().isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO skill_progress (user_id, category, skill_name, status, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id, category, skill_name) DO UPDATE SET
                status = excluded.status,
                updated_at = excluded.updated_at
        """, (user_id, category, skill_name, status, now))
        conn.commit()
        return True


# --------------------------------------------------
# Bookmarks Operations
# --------------------------------------------------

def get_bookmarks(user_id):
    """Get all saved bookmarks for user."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bookmarks WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
        return [dict(row) for row in cursor.fetchall()]


def add_bookmark(user_id, company, title, url, category, notes=""):
    """Add a new bookmark."""
    bm_id = f"bm_{uuid.uuid4().hex[:12]}"
    now = datetime.utcnow().isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO bookmarks (id, user_id, company, title, url, category, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (bm_id, user_id, company, title, url, category, notes, now))
        conn.commit()
        cursor.execute("SELECT * FROM bookmarks WHERE id = ?", (bm_id,))
        return dict(cursor.fetchone())


def delete_bookmark(user_id, bookmark_id):
    """Delete a bookmark ensuring ownership."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM bookmarks WHERE id = ? AND user_id = ?", (bookmark_id, user_id))
        conn.commit()
        return cursor.rowcount > 0


# --------------------------------------------------
# Applications Tracker Operations
# --------------------------------------------------

def get_applications(user_id):
    """Get all internship applications for user."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM applications WHERE user_id = ? ORDER BY updated_at DESC", (user_id,))
        return [dict(row) for row in cursor.fetchall()]


def add_application(user_id, company, role, url="", category="General", status="Saved",
                    application_date=None, deadline=None, follow_up_date=None, notes="", **kwargs):
    """Add a new application record with flexible kwargs."""
    app_id = f"app_{uuid.uuid4().hex[:12]}"
    now = datetime.utcnow().isoformat()
    applied = application_date or kwargs.get("applied_date")
    followup = follow_up_date or kwargs.get("followup_date")

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO applications (
                id, user_id, company, role, url, category, status,
                application_date, deadline, follow_up_date, notes, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (app_id, user_id, company, role, url, category, status,
              applied, deadline, followup, notes, now, now))
        conn.commit()
        cursor.execute("SELECT * FROM applications WHERE id = ?", (app_id,))
        return dict(cursor.fetchone())


def update_application(arg1, arg2, update_fields=None, **kwargs):
    """Update fields of an application record. Accepts (user_id, app_id) or (app_id, user_id)."""
    now = datetime.utcnow().isoformat()
    if isinstance(arg1, str) and arg1.startswith("usr_"):
        user_id, app_id = arg1, arg2
    else:
        app_id, user_id = arg1, arg2

    fields = dict(update_fields or {})
    fields.update(kwargs)
    allowed = ["company", "role", "url", "category", "status", "application_date", "applied_date", "deadline", "follow_up_date", "followup_date", "notes"]

    updates = []
    values = []
    for k in allowed:
        if k in fields:
            col = "application_date" if k == "applied_date" else ("follow_up_date" if k == "followup_date" else k)
            updates.append(f"{col} = ?")
            values.append(fields[k])

    if not updates:
        return None

    updates.append("updated_at = ?")
    values.append(now)
    values.append(app_id)
    values.append(user_id)

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE applications SET {', '.join(updates)} WHERE id = ? AND user_id = ?", values)
        conn.commit()
        cursor.execute("SELECT * FROM applications WHERE id = ? AND user_id = ?", (app_id, user_id))
        row = cursor.fetchone()
        return dict(row) if row else None


def delete_application(arg1, arg2):
    """Delete an application record ensuring ownership. Accepts (user_id, app_id) or (app_id, user_id)."""
    if isinstance(arg1, str) and arg1.startswith("usr_"):
        user_id, app_id = arg1, arg2
    else:
        app_id, user_id = arg1, arg2

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM applications WHERE id = ? AND user_id = ?", (app_id, user_id))
        conn.commit()
        return cursor.rowcount > 0


# --------------------------------------------------
# Reminders Operations
# --------------------------------------------------

def get_reminders(user_id):
    """Get all active reminders for user."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reminders WHERE user_id = ? ORDER BY due_date ASC", (user_id,))
        return [dict(row) for row in cursor.fetchall()]


def add_reminder(user_id, title, due_date=None, reminder_type="deadline", related_id=None, **kwargs):
    """Add a new reminder."""
    rem_id = f"rem_{uuid.uuid4().hex[:12]}"
    now = datetime.utcnow().isoformat()
    # Check if due_date and reminder_type swapped
    if due_date and due_date in ["deadline", "followup", "interview", "assessment"]:
        reminder_type, due_date = due_date, kwargs.get("due_date", "")

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO reminders (id, user_id, title, reminder_type, due_date, is_completed, created_at)
            VALUES (?, ?, ?, ?, ?, 0, ?)
        """, (rem_id, user_id, title, reminder_type, due_date or "", now))
        conn.commit()
        cursor.execute("SELECT * FROM reminders WHERE id = ?", (rem_id,))
        return dict(cursor.fetchone())


def toggle_reminder(arg1, arg2):
    """Toggle completed status of reminder. Accepts (user_id, reminder_id) or (reminder_id, user_id)."""
    if isinstance(arg1, str) and arg1.startswith("usr_"):
        user_id, reminder_id = arg1, arg2
    else:
        reminder_id, user_id = arg1, arg2

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE reminders
            SET is_completed = CASE WHEN is_completed = 1 THEN 0 ELSE 1 END
            WHERE id = ? AND user_id = ?
        """, (reminder_id, user_id))
        conn.commit()
        cursor.execute("SELECT * FROM reminders WHERE id = ? AND user_id = ?", (reminder_id, user_id))
        row = cursor.fetchone()
        return dict(row) if row else None


def delete_reminder(arg1, arg2):
    """Delete a reminder ensuring ownership. Accepts (user_id, reminder_id) or (reminder_id, user_id)."""
    if isinstance(arg1, str) and arg1.startswith("usr_"):
        user_id, reminder_id = arg1, arg2
    else:
        reminder_id, user_id = arg1, arg2

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reminders WHERE id = ? AND user_id = ?", (reminder_id, user_id))
        conn.commit()
        return cursor.rowcount > 0


# --------------------------------------------------
# Interview Practice Scores
# --------------------------------------------------

def save_interview_score(user_id, topic, score=0, total=0, percentage=0.0, answers=None, **kwargs):
    """Record an interview quiz / mock result."""
    now = datetime.utcnow().isoformat()
    feedback = kwargs.get("feedback", "")
    category = kwargs.get("category", topic)

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(interview_scores)")
        cols = {row["name"] for row in cursor.fetchall()}

        insert_cols = ["user_id", "completed_at"]
        insert_vals = [user_id, now]

        if "topic" in cols:
            insert_cols.append("topic")
            insert_vals.append(topic)
        if "category" in cols:
            insert_cols.append("category")
            insert_vals.append(category)
        if "score" in cols:
            insert_cols.append("score")
            insert_vals.append(score)
        if "total_questions" in cols:
            insert_cols.append("total_questions")
            insert_vals.append(total)
        if "total" in cols:
            insert_cols.append("total")
            insert_vals.append(total)
        if "percentage" in cols:
            insert_cols.append("percentage")
            insert_vals.append(percentage)
        if "feedback" in cols:
            insert_cols.append("feedback")
            insert_vals.append(feedback)

        placeholders = ", ".join(["?"] * len(insert_vals))
        col_str = ", ".join(insert_cols)
        cursor.execute(f"INSERT INTO interview_scores ({col_str}) VALUES ({placeholders})", insert_vals)
        conn.commit()
        return cursor.lastrowid


def get_user_interview_scores(user_id):
    """Fetch user's recent interview scores."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM interview_scores
            WHERE user_id = ?
            ORDER BY completed_at DESC
            LIMIT 20
        """, (user_id,))
        results = []
        for row in cursor.fetchall():
            d = dict(row)
            if "total" not in d and "total_questions" in d:
                d["total"] = d["total_questions"]
            results.append(d)
        return results


# --------------------------------------------------
# Complete Data Export & Account Deletion
# --------------------------------------------------

def export_user_data(user_id):
    """Export all user-associated data into a structured dictionary."""
    user = get_user_by_id(user_id)
    if not user:
        return None

    settings = get_user_settings(user_id)
    memory = get_user_memory(user_id)
    sessions = get_user_sessions(user_id)

    full_sessions = []
    for s in sessions:
        msgs = get_session_messages(s["id"])
        full_sessions.append({
            "session": s,
            "messages": msgs
        })

    skills = get_user_skill_progress(user_id)
    bookmarks = get_bookmarks(user_id)
    apps = get_applications(user_id)
    reminders = get_reminders(user_id)
    scores = get_user_interview_scores(user_id)

    return {
        "export_date": datetime.utcnow().isoformat(),
        "user_profile": {
            "name": user["name"],
            "email": user["email"],
            "created_at": user["created_at"]
        },
        "settings": settings,
        "memory": memory,
        "chat_sessions": full_sessions,
        "skill_progress": skills,
        "bookmarks": bookmarks,
        "applications": apps,
        "reminders": reminders,
        "interview_scores": scores
    }


def delete_user_account(user_id):
    """Permanently delete user and all associated data."""
    with get_db() as conn:
        cursor = conn.cursor()
        # Delete user record (foreign keys cascade)
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        cursor.execute("DELETE FROM user_settings WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM user_memory WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM skill_progress WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM bookmarks WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM applications WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM reminders WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM interview_scores WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM chat_sessions WHERE user_id = ?", (user_id,))
        conn.commit()
        return True
