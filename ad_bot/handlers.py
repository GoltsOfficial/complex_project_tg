# handlers.py
import logging
import json
from aiogram import F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup,
    InlineKeyboardButton, LabeledPrice, PreCheckoutQuery,
    ContentType, WebAppInfo
)
from aiogram.methods import AnswerPreCheckoutQuery

from loader import dp, bot
from config import PROVIDER_TOKEN, CURRENCY, PRICE_PER_MONTH_RUB
from models import Order, init_db, db


# клавиатура с Web App кнопкой
def get_kbd():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🛒 Открыть магазин",
            web_app=WebAppInfo(url="https://ваш-username.github.io")
        )],
        [InlineKeyboardButton(text="Купить подписку 1 мес", callback_data="buy_1")],
        [InlineKeyboardButton(text="Купить подписку 3 мес", callback_data="buy_3")],
        [InlineKeyboardButton(text="Купить подписку 6 мес", callback_data="buy_6")],
        [InlineKeyboardButton(text="Мои заказы", callback_data="my_orders")],
    ])


# /start — корректно через F
@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    await message.answer("Привет! Можно купить подписку на бота.", reply_markup=get_kbd())


# Обработчик данных из Web App
@dp.message(F.content_type == 'web_app_data')
async def handle_web_app_data(message: Message):
    try:
        data = json.loads(message.web_app_data.data)
        action = data.get('action')

        if action == 'buy_subscription':
            months = data.get('months')
            price = data.get('price')
            user_id = data.get('user_id')

            # Создаем заказ в БД
            total_rub = price
            amount_cents = int(total_rub * 100)

            with db.atomic():
                order = Order.create(
                    user_id=user_id or message.from_user.id,
                    payload="",
                    months=months,
                    amount=amount_cents,
                    currency=CURRENCY,
                    status="pending"
                )
                order.payload = f"order:{order.id}"
                order.save()

            prices = [LabeledPrice(label=f"Подписка {months} мес.", amount=amount_cents)]

            if PROVIDER_TOKEN.strip().lower().endswith("test"):
                await message.answer("Внимание: используется тестовый provider token.")

            # Отправляем инвойс
            await bot.send_invoice(
                chat_id=message.chat.id,
                title="Подписка на бота",
                description=f"Оплата подписки на {months} месяц(а): {total_rub} ₽",
                payload=order.payload,
                provider_token=PROVIDER_TOKEN,
                currency=CURRENCY,
                prices=prices,
                start_parameter=f"subscribe_{months}",
                is_flexible=False
            )

            await message.answer("✅ Заказ создан! Проверьте инвойс выше для оплаты.")

    except Exception as e:
        logging.error(f"Web app data error: {e}")
        await message.answer("❌ Ошибка обработки заказа из магазина")


# Колбек: показать заказы
@dp.callback_query(F.data == "my_orders")
async def cb_my_orders(callback: CallbackQuery):
    orders = Order.select().where(Order.user_id == callback.from_user.id).order_by(Order.created_at.desc())
    if orders.count() == 0:
        await callback.message.answer("У вас пока нет заказов.")
    else:
        texts = []
        for o in orders:
            amt = o.amount / 100.0
            texts.append(f"#{o.id} — {o.months} мес — {amt:.2f} {o.currency} — {o.status}")
        await callback.message.answer("Ваши заказы:\n" + "\n".join(texts))
    await callback.answer()


# Колбек: покупка (buy_1 / buy_3 / buy_6)
@dp.callback_query(F.data.startswith("buy_"))
async def cb_buy(callback: CallbackQuery):
    data = callback.data

    # Определяем количество месяцев и цену
    if data == "buy_1":
        months = 1
        total_rub = 250  # цена за 1 месяц
    elif data == "buy_3":
        months = 3
        total_rub = 500  # цена за 3 месяца
    elif data == "buy_6":
        months = 6
        total_rub = 750  # цена за 6 месяцев
    else:
        await callback.answer("❌ Неверный вариант подписки")
        return

    amount_cents = int(total_rub * 100)

    # создаём заказ в БД
    with db.atomic():
        order = Order.create(
            user_id=callback.from_user.id,
            payload="",
            months=months,
            amount=amount_cents,
            currency=CURRENCY,
            status="pending"
        )
        order.payload = f"order:{order.id}"
        order.save()

    prices = [LabeledPrice(label=f"Подписка {months} мес.", amount=amount_cents)]

    if PROVIDER_TOKEN.strip().lower().endswith("test"):
        await callback.message.answer("Внимание: используется тестовый provider token.")

    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="Подписка на бота",
        description=f"Оплата подписки на {months} месяц(а): {total_rub} ₽",
        payload=order.payload,
        provider_token=PROVIDER_TOKEN,
        currency=CURRENCY,
        prices=prices,
        start_parameter=f"subscribe_{months}",
        is_flexible=False
    )

    await callback.answer()


# pre_checkout_query — без дополнительных kwargs (оставляем декоратор как есть)
@dp.pre_checkout_query()
async def process_pre_checkout(pre: PreCheckoutQuery):
    try:
        payload = pre.invoice_payload
    except Exception:
        payload = None

    if not payload:
        logging.warning("PreCheckout without payload")
        await AnswerPreCheckoutQuery(pre_checkout_query_id=pre.id, ok=False, error_message="Invalid payload")
        return

    order_id = None
    if payload.startswith("order:"):
        try:
            order_id = int(payload.split(":", 1)[1])
        except Exception:
            order_id = None

    if not order_id:
        logging.warning("PreCheckout payload parse failed: %s", payload)
        await AnswerPreCheckoutQuery(pre_checkout_query_id=pre.id, ok=False, error_message="Order not found")
        return

    order = Order.get_or_none(Order.id == order_id)
    if not order:
        logging.warning("Order not found for precheckout: %s", order_id)
        await AnswerPreCheckoutQuery(pre_checkout_query_id=pre.id, ok=False, error_message="Order not found")
        return

    # проверяем сумму и валюту
    if pre.total_amount != order.amount or pre.currency != order.currency:
        logging.warning("Amount mismatch: pre=%s %s db=%s %s", pre.total_amount, pre.currency, order.amount,
                        order.currency)
        await AnswerPreCheckoutQuery(pre_checkout_query_id=pre.id, ok=False, error_message="Amount mismatch")
        return

    await AnswerPreCheckoutQuery(pre_checkout_query_id=pre.id, ok=True)


# successful_payment — заменяем content_types аргумент на фильтр F
@dp.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: Message):
    pay = message.successful_payment
    # payload обычно находится в pay.invoice_payload (варианты зависят от версии)
    payload = getattr(pay, "invoice_payload", None) or getattr(pay, "payload", None)
    provider_id = getattr(pay, "provider_payment_charge_id", None)
    telegram_id = getattr(pay, "telegram_payment_charge_id", None)

    order = None
    if payload and payload.startswith("order:"):
        try:
            oid = int(payload.split(":", 1)[1])
            order = Order.get_or_none(Order.id == oid)
        except Exception:
            order = None

    if not order:
        logging.error("Successful payment but order not found. payload=%s", payload)
        await message.answer("Платёж получен, но заказ не найден. Сообщите админу.")
        return

    order.status = "paid"
    order.provider_payment_charge_id = provider_id
    order.telegram_payment_charge_id = telegram_id
    order.save()

    total = pay.total_amount / 100.0
    await message.answer(
        f"Платёж успешно получен ✅\nСумма: {total:.2f} {pay.currency}\nЗаказ #{order.id} помечен как оплаченный.")
    await message.answer("Доступ выдан — спасибо! (тут добавьте логику выдачи подписки)")