import sqlite3
import time


# ====================== RSS ======================
def init_db():
    conn = sqlite3.connect('rss.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS rss_feeds
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  url TEXT NOT NULL,
                  interval INTEGER DEFAULT 60,
                  last_posted INTEGER DEFAULT 0)''')

    c.execute('''CREATE TABLE IF NOT EXISTS ads
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  photo_url TEXT,
                  title TEXT NOT NULL,
                  description TEXT,
                  button_text TEXT DEFAULT 'Перейти →',
                  button_url TEXT,
                  views INTEGER NOT NULL,
                  interval INTEGER DEFAULT 60,
                  last_posted INTEGER DEFAULT 0)''')

    conn.commit()
    conn.close()


def check_db_structure():
    conn = sqlite3.connect('rss.db')
    c = conn.cursor()

    try:
        c.execute("SELECT interval, last_posted FROM ads LIMIT 1")
    except sqlite3.OperationalError:
        print("Обновляем структуру таблицы ads...")
        c.execute("DROP TABLE IF EXISTS ads")
        c.execute('''CREATE TABLE ads
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      photo_url TEXT,
                      title TEXT NOT NULL,
                      description TEXT,
                      button_text TEXT DEFAULT 'Перейти →',
                      button_url TEXT,
                      views INTEGER NOT NULL,
                      interval INTEGER DEFAULT 60,
                      last_posted INTEGER DEFAULT 0)''')
        conn.commit()
        print("Таблица ads пересоздана с новой структурой")

    conn.close()


# Инициализируем базу
init_db()
check_db_structure()

seen_links = set()


# ===== RSS =====
def get_all_feeds():
    conn = sqlite3.connect('rss.db')
    c = conn.cursor()
    c.execute("SELECT * FROM rss_feeds")
    feeds = [{"id": row[0], "name": row[1], "url": row[2], "interval": row[3], "last_posted": row[4]} for row in
             c.fetchall()]
    conn.close()
    return feeds


def add_feed(name, url, interval):
    conn = sqlite3.connect('rss.db')
    c = conn.cursor()
    c.execute("INSERT INTO rss_feeds (name, url, interval) VALUES (?, ?, ?)", (name, url, interval))
    conn.commit()
    conn.close()


def update_feed(feed_id, field, value):
    conn = sqlite3.connect('rss.db')
    c = conn.cursor()
    c.execute(f"UPDATE rss_feeds SET {field} = ? WHERE id = ?", (value, feed_id))
    conn.commit()
    conn.close()


def update_feed_last_posted(feed_id):
    conn = sqlite3.connect('rss.db')
    c = conn.cursor()
    c.execute("UPDATE rss_feeds SET last_posted = ? WHERE id = ?", (int(time.time()), feed_id))
    conn.commit()
    conn.close()


def delete_feed(feed_id):
    conn = sqlite3.connect('rss.db')
    c = conn.cursor()
    c.execute("DELETE FROM rss_feeds WHERE id = ?", (feed_id,))
    conn.commit()
    conn.close()


# ===== Ads =====
def get_all_ads():
    conn = sqlite3.connect('rss.db')
    c = conn.cursor()
    c.execute("SELECT * FROM ads")
    ads = [{
        "id": row[0],
        "photo_url": row[1],
        "title": row[2],
        "description": row[3],
        "button_text": row[4],
        "button_url": row[5],
        "views": row[6],
        "interval": row[7],
        "last_posted": row[8]
    } for row in c.fetchall()]
    conn.close()
    return ads


def add_ad(photo_url, title, description, button_text, button_url, views, interval=60):
    conn = sqlite3.connect('rss.db')
    c = conn.cursor()

    if photo_url is None:
        photo_url = ""

    c.execute(
        "INSERT INTO ads (photo_url, title, description, button_text, button_url, views, interval) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (photo_url, title, description, button_text, button_url, views, interval))
    conn.commit()
    conn.close()
    print(f"Реклама добавлена: {title}, интервал: {interval} мин")


def update_ad_last_posted(ad_id):
    conn = sqlite3.connect('rss.db')
    c = conn.cursor()
    c.execute("UPDATE ads SET last_posted = ? WHERE id = ?", (int(time.time()), ad_id))
    conn.commit()
    conn.close()


def decrement_ad_view(ad_id):
    conn = sqlite3.connect('rss.db')
    c = conn.cursor()
    c.execute("UPDATE ads SET views = views - 1 WHERE id = ?", (ad_id,))
    c.execute("DELETE FROM ads WHERE views <= 0")
    conn.commit()
    conn.close()


def update_ad(ad_id, photo_url=None, title=None, description=None, button_text=None, button_url=None, interval=None):
    conn = sqlite3.connect('rss.db')
    c = conn.cursor()

    updates = []
    params = []

    if photo_url is not None:
        updates.append("photo_url = ?")
        params.append(photo_url)
    if title is not None:
        updates.append("title = ?")
        params.append(title)
    if description is not None:
        updates.append("description = ?")
        params.append(description)
    if button_text is not None:
        updates.append("button_text = ?")
        params.append(button_text)
    if button_url is not None:
        updates.append("button_url = ?")
        params.append(button_url)
    if interval is not None:
        updates.append("interval = ?")
        params.append(interval)

    if updates:
        params.append(ad_id)
        c.execute(f"UPDATE ads SET {', '.join(updates)} WHERE id = ?", params)

    conn.commit()
    conn.close()


def get_ad_by_id(ad_id):
    conn = sqlite3.connect('rss.db')
    c = conn.cursor()
    c.execute("SELECT * FROM ads WHERE id = ?", (ad_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "photo_url": row[1],
            "title": row[2],
            "description": row[3],
            "button_text": row[4],
            "button_url": row[5],
            "views": row[6],
            "interval": row[7],
            "last_posted": row[8]
        }
    return None