
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
import sqlite3

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field


BASE = Path(__file__).resolve().parent
DB = BASE / "mindblog_v2.db"

ARTICLES = [
    (
        "Як почати вивчати Python з нуля",
        "python",
        "Python",
        "Простий маршрут для тих, хто хоче зробити перші кроки у програмуванні.",
        "Python — чудовий вибір для першої мови програмування.\n\n"
        "Почніть зі змінних, умов, циклів та функцій. Не намагайтеся вивчити все одразу.\n\n"
        "Після основ створіть невеликий проєкт: калькулятор, список справ або простого Telegram-бота.\n\n"
        "Найважливіше — писати код регулярно та розбиратися у власних помилках.",
        "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=1200&q=85",
        6,
        "2026-10-20",
        1,
    ),
    (
        "FastAPI: створюємо перше REST API",
        "backend",
        "Backend",
        "Від першого ендпоінта до невеликого серверного застосунку.",
        "FastAPI дозволяє швидко створювати API на Python.\n\n"
        "Почніть з об'єкта FastAPI та простого маршруту GET. Потім додайте POST-запити й Pydantic-моделі.\n\n"
        "Коли базові запити працюють, підключіть SQLite або PostgreSQL.\n\n"
        "Обов'язково тестуйте свої ендпоінти через автоматичну документацію /docs.",
        "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=1200&q=85",
        8,
        "2026-10-18",
        1,
    ),
    (
        "Як зберігати концентрацію під час навчання",
        "productivity",
        "Продуктивність",
        "Маленькі звички, які допомагають працювати над важливим без перевантаження.",
        "Концентрація починається з простого плану.\n\n"
        "Оберіть одну конкретну задачу й приберіть зайві сповіщення.\n\n"
        "Працюйте короткими зручними блоками, робіть перерви та залишайте час на відпочинок.\n\n"
        "Поступовість і регулярність зазвичай корисніші за спроби зробити все за один день.",
        "https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=1200&q=85",
        5,
        "2026-10-15",
        0,
    ),
    (
        "Git та GitHub: основи для розробника",
        "tools",
        "Інструменти",
        "Як працювати з комітами, гілками та власним портфоліо.",
        "Git допомагає відстежувати зміни у коді.\n\n"
        "Створіть репозиторій, додайте файли й зробіть перший коміт.\n\n"
        "Використовуйте окремі гілки для нових функцій і пишіть зрозумілі повідомлення комітів.\n\n"
        "На GitHub додайте README з описом, інструкцією запуску та прикладами роботи.",
        "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=1200&q=85",
        7,
        "2026-10-12",
        0,
    ),
    (
        "SQL для початківців: перші запити",
        "backend",
        "Backend",
        "SELECT, WHERE та ORDER BY на практичних прикладах.",
        "SQL потрібен для роботи з реляційними базами даних.\n\n"
        "Команда SELECT отримує дані, WHERE фільтрує результати, а ORDER BY сортує їх.\n\n"
        "Після цього вивчіть INSERT, UPDATE та DELETE.\n\n"
        "Практикуйте запити на невеликій базі з користувачами, книгами чи завданнями.",
        "https://images.unsplash.com/photo-1544383835-bda2bc66a55d?w=1200&q=85",
        6,
        "2026-10-09",
        0,
    ),
    (
        "Як створити перший проєкт для портфоліо",
        "career",
        "Кар'єра",
        "Ідеї для простого, але завершеного вебзастосунку.",
        "Хороший портфоліо-проєкт не обов'язково має бути величезним.\n\n"
        "Оберіть зрозумілу задачу: менеджер справ, каталог книг або невеликий блог.\n\n"
        "Створіть API, підключіть базу даних і протестуйте основні сценарії.\n\n"
        "Важливо вміти пояснити архітектуру, рішення та обмеження свого застосунку.",
        "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=1200&q=85",
        5,
        "2026-10-05",
        0,
    ),
]


class CommentCreate(BaseModel):
    author: str = Field(min_length=1, max_length=50)
    text: str = Field(min_length=1, max_length=500)


def connect():
    connection = sqlite3.connect(DB, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def serialize(row):
    return dict(row)


@asynccontextmanager
async def lifespan(app: FastAPI):
    with connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                category_name TEXT NOT NULL,
                excerpt TEXT NOT NULL,
                content TEXT NOT NULL,
                image TEXT NOT NULL,
                read_time INTEGER NOT NULL,
                published_at TEXT NOT NULL,
                featured INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id INTEGER NOT NULL,
                author TEXT NOT NULL,
                text TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(article_id)
                    REFERENCES articles(id)
                    ON DELETE CASCADE
            )
            """
        )

        count = connection.execute(
            "SELECT COUNT(*) FROM articles"
        ).fetchone()[0]

        if count == 0:
            connection.executemany(
                """
                INSERT INTO articles (
                    title, category, category_name,
                    excerpt, content, image, read_time,
                    published_at, featured
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                ARTICLES,
            )

    yield


app = FastAPI(
    title="MindBlog API",
    description="Демонстраційний блог на FastAPI та SQLite",
    version="2.0.0",
    lifespan=lifespan,
)


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(BASE / "index.html")


@app.get("/style.css", include_in_schema=False)
def stylesheet():
    return FileResponse(
        BASE / "style.css",
        media_type="text/css",
    )


@app.get("/app.js", include_in_schema=False)
def javascript():
    return FileResponse(
        BASE / "app.js",
        media_type="application/javascript",
    )


@app.get("/api/articles")
def list_articles(
    search: str = Query(default="", max_length=100),
    category: str = Query(default="all", max_length=30),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=6, ge=1, le=20),
):
    conditions = []
    params = []

    if search.strip():
        conditions.append(
            "(title LIKE ? OR excerpt LIKE ? OR content LIKE ?)"
        )
        term = f"%{search.strip()}%"
        params.extend([term, term, term])

    if category != "all":
        conditions.append("category = ?")
        params.append(category)

    where = ""

    if conditions:
        where = " WHERE " + " AND ".join(conditions)

    with connect() as connection:
        total = connection.execute(
            "SELECT COUNT(*) FROM articles" + where,
            params,
        ).fetchone()[0]

        rows = connection.execute(
            """
            SELECT id, title, category, category_name,
                   excerpt, image, read_time,
                   published_at, featured
            FROM articles
            """
            + where
            + """
            ORDER BY published_at DESC, id DESC
            LIMIT ? OFFSET ?
            """,
            [*params, limit, (page - 1) * limit],
        ).fetchall()

    return {
        "items": [serialize(row) for row in rows],
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
    }


@app.get("/api/articles/{article_id}")
def get_article(article_id: int):
    with connect() as connection:
        article = connection.execute(
            "SELECT * FROM articles WHERE id = ?",
            (article_id,),
        ).fetchone()

    if article is None:
        raise HTTPException(404, "Статтю не знайдено")

    return serialize(article)


@app.get("/api/articles/{article_id}/comments")
def list_comments(article_id: int):
    with connect() as connection:
        article = connection.execute(
            "SELECT id FROM articles WHERE id = ?",
            (article_id,),
        ).fetchone()

        if article is None:
            raise HTTPException(404, "Статтю не знайдено")

        rows = connection.execute(
            """
            SELECT id, author, text, created_at
            FROM comments
            WHERE article_id = ?
            ORDER BY id DESC
            LIMIT 100
            """,
            (article_id,),
        ).fetchall()

    return [serialize(row) for row in rows]


@app.post("/api/articles/{article_id}/comments", status_code=201)
def add_comment(article_id: int, data: CommentCreate):
    author = data.author.strip()
    text = data.text.strip()

    if not author or not text:
        raise HTTPException(
            422,
            "Ім'я та коментар не можуть бути порожніми",
        )

    with connect() as connection:
        article = connection.execute(
            "SELECT id FROM articles WHERE id = ?",
            (article_id,),
        ).fetchone()

        if article is None:
            raise HTTPException(404, "Статтю не знайдено")

        cursor = connection.execute(
            """
            INSERT INTO comments (
                article_id, author, text, created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                article_id,
                author,
                text,
                datetime.now(timezone.utc).isoformat(),
            ),
        )

        comment = connection.execute(
            """
            SELECT id, author, text, created_at
            FROM comments
            WHERE id = ?
            """,
            (cursor.lastrowid,),
        ).fetchone()

    return serialize(comment)
