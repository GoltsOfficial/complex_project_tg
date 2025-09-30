import sqlite3
from ad_bot.main import DATABASE_PATH

def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS payments
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  amount INTEGER NOT NULL,
                  currency TEXT NOT NULL,
                  status TEXT DEFAULT 'pending',
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def save_payment(user_id, amount, currency):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO payments (user_id, amount, currency) VALUES (?, ?, ?)",
              (user_id, amount, currency))
    conn.commit()
    payment_id = c.lastrowid
    conn.close()
    return payment_id

def get_payment_by_id(payment_id):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM payments WHERE id = ?", (payment_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            'id': row[0],
            'user_id': row[1],
            'amount': row[2],
            'currency': row[3],
            'status': row[4],
            'created_at': row[5]
        }
    return None

def update_payment_status(payment_id, status):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("UPDATE payments SET status = ? WHERE id = ?", (status, payment_id))
    conn.commit()
    conn.close()