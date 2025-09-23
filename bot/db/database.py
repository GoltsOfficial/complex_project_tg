import sqlite3

# ====================== RSS ======================
def init_db():
    conn = sqlite3.connect('rss.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS rss_feeds
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  url TEXT NOT NULL,
                  interval INTEGER DEFAULT 60)''')
    c.execute('''CREATE TABLE IF NOT EXISTS ads
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  text TEXT NOT NULL,
                  views INTEGER NOT NULL)''')
    conn.commit()
    conn.close()

init_db()

seen_links = set()
news_queue = []

# ===== RSS =====
def get_all_feeds():
    conn = sqlite3.connect('rss.db')
    c = conn.cursor()
    c.execute("SELECT * FROM rss_feeds")
    feeds = [{"id": row[0], "name": row[1], "url": row[2], "interval": row[3]} for row in c.fetchall()]
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
    ads = [{"id": row[0], "text": row[1], "views": row[2]} for row in c.fetchall()]
    conn.close()
    return ads

def add_ad(text, views):
    conn = sqlite3.connect('rss.db')
    c = conn.cursor()
    c.execute("INSERT INTO ads (text, views) VALUES (?, ?)", (text, views))
    conn.commit()
    conn.close()

def decrement_ad_view(ad_id):
    conn = sqlite3.connect('rss.db')
    c = conn.cursor()
    c.execute("UPDATE ads SET views = views - 1 WHERE id = ?", (ad_id,))
    c.execute("DELETE FROM ads WHERE views <= 0")
    conn.commit()
    conn.close()

# ===== Ads =====
def update_ad(ad_id, new_text):
    conn = sqlite3.connect('rss.db')
    c = conn.cursor()
    c.execute("UPDATE ads SET text = ? WHERE id = ?", (new_text, ad_id))
    conn.commit()
    conn.close()