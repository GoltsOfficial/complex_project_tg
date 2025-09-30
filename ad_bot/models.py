# models.py
from peewee import (
    Model, SqliteDatabase, AutoField, IntegerField,
    CharField, DateTimeField, TextField
)
from datetime import datetime
from config import DATABASE_PATH

db = SqliteDatabase(DATABASE_PATH, pragmas={
    'journal_mode': 'wal',
    'cache_size': -1024 * 64
})

class BaseModel(Model):
    class Meta:
        database = db

class Order(BaseModel):
    id = AutoField()
    user_id = IntegerField(index=True)
    payload = CharField(null=True)  # payload, который отправляем в invoice (строка)
    months = IntegerField(default=1)
    amount = IntegerField()  # в наименьших единицах (копейки)
    currency = CharField(default='RUB')
    status = CharField(default='pending')  # pending / paid / failed
    provider_payment_charge_id = CharField(null=True)
    telegram_payment_charge_id = CharField(null=True)
    created_at = DateTimeField(default=datetime.utcnow)
    extra = TextField(null=True)  # для любых заметок (необязательно)

def init_db():
    db.connect(reuse_if_open=True)
    db.create_tables([Order])
    db.close()
