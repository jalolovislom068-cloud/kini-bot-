import aiosqlite

DB_PATH = "movies.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                file_id TEXT NOT NULL,
                description TEXT DEFAULT ''
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


async def add_user(user_id: int, username: str, full_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (id, username, full_name) VALUES (?, ?, ?)",
            (user_id, username, full_name)
        )
        await db.commit()


async def get_all_user_ids():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT id FROM users") as cursor:
            rows = await cursor.fetchall()
            return [r[0] for r in rows]


async def add_movie(code: str, title: str, file_id: str, description: str = ""):
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute(
                "INSERT INTO movies (code, title, file_id, description) VALUES (?, ?, ?, ?)",
                (code.upper(), title, file_id, description)
            )
            await db.commit()
            return True
        except aiosqlite.IntegrityError:
            return False


async def get_movie(code: str):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT code, title, file_id, description FROM movies WHERE code = ?",
            (code.upper(),)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return {"code": row[0], "title": row[1], "file_id": row[2], "description": row[3]}
            return None


async def delete_movie(code: str):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "DELETE FROM movies WHERE code = ?", (code.upper(),)
        )
        await db.commit()
        return cursor.rowcount > 0


async def get_all_movies():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT code, title, description FROM movies ORDER BY code") as cursor:
            rows = await cursor.fetchall()
            return [{"code": r[0], "title": r[1], "description": r[2]} for r in rows]


async def get_movie_count():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM movies") as cursor:
            row = await cursor.fetchone()
            return row[0]


async def get_user_count():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            row = await cursor.fetchone()
            return row[0]
