
const API = "/api/articles";

const $ = id => document.getElementById(id);

const grid = $("articlesGrid");
const searchInput = $("search");
const resultCount = $("resultCount");
const pagination = $("pagination");
const dialog = $("articleDialog");
const articleContent = $("articleContent");

let currentCategory = "all";
let currentPage = 1;
let searchTimer = null;
let toastTimer = null;
let requestVersion = 0;

const LIMIT = 6;

const formatDate = value => {
    return new Date(value + "T12:00:00").toLocaleDateString(
        "uk-UA",
        {
            day: "numeric",
            month: "long",
            year: "numeric"
        }
    );
};

function createElement(tag, className = "", text = "") {
    const element = document.createElement(tag);

    if (className) {
        element.className = className;
    }

    element.textContent = text;

    return element;
}

function showToast(message) {
    const toast = $("toast");

    clearTimeout(toastTimer);

    toast.textContent = message;
    toast.classList.add("show");

    toastTimer = setTimeout(() => {
        toast.classList.remove("show");
    }, 3000);
}

async function apiRequest(url, options = {}) {
    const response = await fetch(url, options);

    if (!response.ok) {
        let message = `Помилка сервера: ${response.status}`;

        try {
            const data = await response.json();

            if (typeof data.detail === "string") {
                message = data.detail;
            }
        } catch {}

        throw new Error(message);
    }

    return response.json();
}

function createArticleCard(article) {
    const card = createElement("article", "article-card");

    const image = createElement("img", "article-image");
    image.src = article.image;
    image.alt = article.title;
    image.loading = "lazy";

    card.appendChild(image);

    const body = createElement("div", "article-body");

    body.appendChild(
        createElement(
            "span",
            "article-category",
            article.category_name
        )
    );

    body.appendChild(
        createElement("h3", "", article.title)
    );

    body.appendChild(
        createElement(
            "p",
            "article-description",
            article.excerpt
        )
    );

    const footer = createElement("div", "article-footer");

    footer.appendChild(
        createElement(
            "span",
            "",
            `${formatDate(article.published_at)} · ${article.read_time} хв`
        )
    );

    const readButton = createElement(
        "button",
        "read-button",
        "Читати ↗"
    );

    readButton.type = "button";

    readButton.addEventListener("click", () => {
        openArticle(article.id);
    });

    footer.appendChild(readButton);
    body.appendChild(footer);
    card.appendChild(body);

    return card;
}

async function loadArticles() {
    const version = ++requestVersion;

    grid.replaceChildren(
        createElement(
            "div",
            "loading",
            "Завантажуємо публікації..."
        )
    );

    const params = new URLSearchParams({
        search: searchInput.value.trim(),
        category: currentCategory,
        page: currentPage,
        limit: LIMIT
    });

    try {
        const data = await apiRequest(`${API}?${params}`);

        if (version !== requestVersion) {
            return;
        }

        grid.replaceChildren();

        resultCount.textContent =
            `Знайдено статей: ${data.total}`;

        if (data.items.length === 0) {
            grid.appendChild(
                createElement(
                    "div",
                    "empty-state",
                    "Статей не знайдено. Спробуйте інший запит."
                )
            );
        } else {
            data.items.forEach(article => {
                grid.appendChild(createArticleCard(article));
            });
        }

        renderPagination(data.pages);
    } catch (error) {
        if (version !== requestVersion) {
            return;
        }

        resultCount.textContent = "Помилка завантаження";

        grid.replaceChildren(
            createElement(
                "div",
                "empty-state",
                "Не вдалося завантажити статті. Перевірте FastAPI."
            )
        );

        showToast(error.message);
    }
}

function renderPagination(totalPages) {
    pagination.replaceChildren();

    if (totalPages <= 1) {
        return;
    }

    for (let page = 1; page <= totalPages; page++) {
        const button = createElement(
            "button",
            "page-button" + (
                page === currentPage ? " current" : ""
            ),
            String(page)
        );

        button.addEventListener("click", () => {
            currentPage = page;
            loadArticles();

            $("articles").scrollIntoView({
                behavior: "smooth"
            });
        });

        pagination.appendChild(button);
    }
}

function setCategory(category) {
    currentCategory = category;
    currentPage = 1;

    document.querySelectorAll(".category").forEach(button => {
        button.classList.toggle(
            "active",
            button.dataset.category === category
        );
    });

    loadArticles();
}

async function openArticle(articleId) {
    articleContent.replaceChildren(
        createElement(
            "div",
            "loading",
            "Завантажуємо статтю..."
        )
    );

    dialog.showModal();

    try {
        const article = await apiRequest(
            `${API}/${articleId}`
        );

        articleContent.replaceChildren();

        const image = createElement("img", "dialog-image");

        image.src = article.image;
        image.alt = article.title;

        articleContent.appendChild(image);

        const body = createElement("div", "dialog-body");

        body.appendChild(
            createElement(
                "span",
                "article-category",
                article.category_name
            )
        );

        body.appendChild(
            createElement("h2", "", article.title)
        );

        body.appendChild(
            createElement(
                "div",
                "dialog-meta",
                `${formatDate(article.published_at)} · ${article.read_time} хв читання`
            )
        );

        const content = createElement("div", "article-text");

        article.content
            .split(/\n\s*\n/)
            .filter(Boolean)
            .forEach(paragraph => {
                content.appendChild(
                    createElement("p", "", paragraph.trim())
                );
            });

        body.appendChild(content);

        const commentsSection = createElement(
            "section",
            "comments-section"
        );

        commentsSection.appendChild(
            createElement("h3", "", "Коментарі")
        );

        const commentsList = createElement("div");

        commentsSection.appendChild(commentsList);

        const form = createElement("form", "comment-form");

        const authorInput = createElement("input");
        authorInput.placeholder = "Ваше ім'я";
        authorInput.maxLength = 50;
        authorInput.required = true;

        const textInput = createElement("textarea");
        textInput.placeholder = "Напишіть коментар...";
        textInput.maxLength = 500;
        textInput.required = true;

        const submitButton = createElement(
            "button",
            "",
            "Опублікувати коментар"
        );

        submitButton.type = "submit";

        form.appendChild(authorInput);
        form.appendChild(textInput);
        form.appendChild(submitButton);

        commentsSection.appendChild(form);
        body.appendChild(commentsSection);

        articleContent.appendChild(body);

        async function loadComments() {
            const comments = await apiRequest(
                `${API}/${articleId}/comments`
            );

            commentsList.replaceChildren();

            if (comments.length === 0) {
                commentsList.appendChild(
                    createElement(
                        "p",
                        "dialog-meta",
                        "Поки немає коментарів. Будьте першим!"
                    )
                );

                return;
            }

            comments.forEach(comment => {
                const item = createElement("div", "comment");

                item.appendChild(
                    createElement("strong", "", comment.author)
                );

                const date = new Date(
                    comment.created_at
                ).toLocaleDateString("uk-UA");

                item.appendChild(
                    createElement("small", "", date)
                );

                item.appendChild(
                    createElement("p", "", comment.text)
                );

                commentsList.appendChild(item);
            });
        }

        form.addEventListener("submit", async event => {
            event.preventDefault();

            submitButton.disabled = true;

            try {
                await apiRequest(
                    `${API}/${articleId}/comments`,
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            author: authorInput.value.trim(),
                            text: textInput.value.trim()
                        })
                    }
                );

                form.reset();

                await loadComments();

                showToast("Коментар додано!");
            } catch (error) {
                showToast(error.message);
            } finally {
                submitButton.disabled = false;
            }
        });

        try {
            await loadComments();
        } catch (error) {
            commentsList.textContent =
                "Коментарі тимчасово недоступні.";
        }

    } catch (error) {
        articleContent.replaceChildren(
            createElement(
                "div",
                "empty-state",
                "Не вдалося відкрити статтю."
            )
        );

        showToast(error.message);
    }
}

document.querySelectorAll(".category").forEach(button => {
    button.addEventListener("click", () => {
        setCategory(button.dataset.category);
    });
});

searchInput.addEventListener("input", () => {
    clearTimeout(searchTimer);

    currentPage = 1;

    searchTimer = setTimeout(() => {
        loadArticles();
    }, 300);
});

$("closeDialog").addEventListener("click", () => {
    dialog.close();
});

dialog.addEventListener("click", event => {
    if (event.target === dialog) {
        dialog.close();
    }
});

$("menuToggle").addEventListener("click", () => {
    const isOpen = $("navLinks").classList.toggle("open");

    $("menuToggle").setAttribute(
        "aria-expanded",
        String(isOpen)
    );
});

document.querySelectorAll(".nav-links a").forEach(link => {
    link.addEventListener("click", () => {
        $("navLinks").classList.remove("open");
        $("menuToggle").setAttribute(
            "aria-expanded",
            "false"
        );
    });
});

$("shareButton").addEventListener("click", async () => {
    try {
        if (navigator.share) {
            await navigator.share({
                title: "MindBlog",
                url: window.location.href
            });
        } else {
            await navigator.clipboard.writeText(
                window.location.href
            );

            showToast("Посилання скопійовано!");
        }
    } catch (error) {
        if (error.name !== "AbortError") {
            showToast("Не вдалося поділитися посиланням");
        }
    }
});

loadArticles();
