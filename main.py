
from contextlib import asynccontextmanager
from pathlib import Path
import sqlite3

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "mindblog_render.db"

ARTICLES = [
    (
        "Як почати вивчати Python з нуля",
        "python",
        "Python",
        "Простий маршрут для тих, хто робить перші кроки у програмуванні.",
        "Python — чудова мова для початку програмування.\n\n"
        "Спочатку вивчіть змінні, типи даних, умови, цикли та функції.\n\n"
        "Після основ спробуйте створити калькулятор, список справ "
        "або простий застосунок, що працює з файлами.\n\n"
        "Не намагайтеся запам'ятати весь синтаксис. "
        "Набагато важливіше розуміти логіку та практикуватися.",
        "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=1200&q=85",
        6,
        "2026-10-20",
        1,
    ),
    (
        "FastAPI: створюємо перше REST API",
        "backend",
        "Backend",
        "Знайомимося з ендпоінтами, Pydantic та HTTP-запитами.",
        "FastAPI — сучасний фреймворк для розробки API на Python.\n\n"
        "Почніть зі створення застосунку FastAPI та маршруту GET.\n\n"
        "Потім спробуйте POST-запит із Pydantic-моделлю для перевірки даних.\n\n"
        "Наступний крок — підключення бази даних і розділення "
        "проєкту на роутери та сервіси.\n\n"
        "Для перевірки API використовуйте інтерактивну документацію /docs.",
        "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=1200&q=85",
        8,
        "2026-10-18",
        1,
    ),
    (
        "Як зберігати концентрацію під час навчання",
        "productivity",
        "Продуктивність",
        "Прості звички для навчання та роботи над проєктами.",
        "Хороший план починається з однієї зрозумілої задачі.\n\n"
        "Спробуйте прибрати зайві сповіщення та визначити, "
        "що найважливіше зробити сьогодні.\n\n"
        "Працюйте зручними короткими блоками, робіть перерви "
        "та залишайте достатньо часу на сон.\n\n"
        "Не обов'язково виконувати все за один день. "
        "Регулярність допомагає розвиватися поступово.",
        "https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=1200&q=85",
        5,
        "2026-10-15",
        0,
    ),
    (
        "Git та GitHub: основи для розробника",
        "tools",
        "Інструменти",
        "Коміти, гілки та перші репозиторії без зайвої складності.",
        "Git дозволяє відстежувати історію змін у проєкті.\n\n"
        "Команда git add готує зміни, а git commit зберігає їх "
        "у локальній історії.\n\n"
        "Git push надсилає коміти до віддаленого репозиторію.\n\n"
        "Для нових функцій зручно створювати окремі гілки.\n\n"
        "Додайте до свого GitHub-проєкту README з інструкцією запуску.",
        "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=1200&q=85",
        7,
        "2026-10-12",
        0,
    ),
    (
        "SQL для початківців: перші запити",
        "backend",
        "Backend",
        "Вчимося отримувати та фільтрувати дані з таблиць.",
        "SQL використовується для роботи з реляційними базами даних.\n\n"
        "SELECT дозволяє отримати рядки з таблиці.\n\n"
        "WHERE додає умову, а ORDER BY визначає порядок результатів.\n\n"
        "Після цього спробуйте INSERT, UPDATE та DELETE.\n\n"
        "Для практики створіть базу книг або менеджер задач.",
        "https://images.unsplash.com/photo-1544383835-bda2bc66a55d?w=1200&q=85",
        6,
        "2026-10-09",
        0,
    ),
    (
        "Як створити перший проєкт для портфоліо",
        "career",
        "Кар'єра",
        "Від невеликої ідеї до завершеного вебзастосунку.",
        "Перший проєкт для портфоліо не повинен бути величезним.\n\n"
        "Оберіть проблему, яку можна розв'язати невеликим застосунком.\n\n"
        "Наприклад, створіть менеджер задач або каталог книг.\n\n"
        "Реалізуйте API, додайте базу даних і перевірте основні сценарії.\n\n"
        "Напишіть README, підготуйте скриншоти та поясніть, "
        "які рішення ви прийняли під час розробки.",
        "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=1200&q=85",
        5,
        "2026-10-05",
        0,
    ),
]


def connect():
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    with connect() as db:
        db.execute(
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

        count = db.execute(
            "SELECT COUNT(*) FROM articles"
        ).fetchone()[0]

        if count == 0:
            db.executemany(
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
    description="Демонстраційний блог про технології",
    version="2.1.0",
    lifespan=lifespan,
)


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(BASE_DIR / "index.html")


@app.get("/style.css", include_in_schema=False)
def css():
    return FileResponse(
        BASE_DIR / "style.css",
        media_type="text/css",
    )


@app.get("/app.js", include_in_schema=False)
def javascript():
    return FileResponse(
        BASE_DIR / "app.js",
        media_type="application/javascript",
    )


@app.get("/health")
def health():
    return {"status": "ok", "service": "mindblog"}


@app.get("/api/articles")
def list_articles(
    search: str = Query(default="", max_length=100),
    category: str = Query(default="all", max_length=30),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=6, ge=1, le=20),
):
    filters = []
    parameters = []

    if search.strip():
        filters.append(
            "(title LIKE ? OR excerpt LIKE ? OR content LIKE ?)"
        )

        value = f"%{search.strip()}%"
        parameters.extend([value, value, value])

    if category != "all":
        filters.append("category = ?")
        parameters.append(category)

    where = ""

    if filters:
        where = " WHERE " + " AND ".join(filters)

    with connect() as db:
        total = db.execute(
            "SELECT COUNT(*) FROM articles" + where,
            parameters,
        ).fetchone()[0]

        rows = db.execute(
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
            [*parameters, limit, (page - 1) * limit],
        ).fetchall()

    return {
        "items": [dict(row) for row in rows],
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
    }


@app.get("/api/articles/{article_id}")
def get_article(article_id: int):
    with connect() as db:
        article = db.execute(
            "SELECT * FROM articles WHERE id = ?",
            (article_id,),
        ).fetchone()

    if article is None:
        raise HTTPException(
            status_code=404,
            detail="Статтю не знайдено",
        )

    return dict(article)


@app.get("/api/articles/{article_id}/comments")
def list_comments(article_id: int):
    with connect() as db:
        article = db.execute(
            "SELECT id FROM articles WHERE id = ?",
            (article_id,),
        ).fetchone()

    if article is None:
        raise HTTPException(
            status_code=404,
            detail="Статтю не знайдено",
        )

    return []
