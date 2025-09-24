# bot/handlers.py
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from bot.db.database import (
    add_feed, get_all_feeds, update_feed, delete_feed,
    add_ad, get_all_ads, decrement_ad_view
)
from bot.states import user_states


# ====================== КЛАВИАТУРЫ ======================
def get_main_menu_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📰 RSS Management", callback_data="mode_rss")],
        [InlineKeyboardButton(text="📢 AD Management", callback_data="mode_ad")],
        [InlineKeyboardButton(text="ℹ️ Help", callback_data="help")]
    ])
    return keyboard


def get_rss_menu_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Add RSS", callback_data="add_rss")],
        [InlineKeyboardButton(text="📋 List RSS", callback_data="list_rss")],
        [InlineKeyboardButton(text="🗑️ Remove RSS", callback_data="remove_rss")],
        [InlineKeyboardButton(text="🔙 Back to Main", callback_data="back_main")]
    ])
    return keyboard


def get_ad_menu_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Add AD", callback_data="add_ad")],
        [InlineKeyboardButton(text="📋 List ADS", callback_data="list_ads")],
        [InlineKeyboardButton(text="🗑️ Remove AD", callback_data="remove_ad")],
        [InlineKeyboardButton(text="🔙 Back to Main", callback_data="back_main")]
    ])
    return keyboard


def get_back_to_rss_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Back to RSS Menu", callback_data="mode_rss")]
    ])
    return keyboard


def get_back_to_ad_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Back to AD Menu", callback_data="mode_ad")]
    ])
    return keyboard


def get_ad_preview_keyboard(button_text, button_url):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=button_text, url=button_url)]
    ])
    return keyboard


# ====================== ОБРАБОТЧИКИ КОМАНД ======================
async def cmd_start(message: types.Message):
    welcome_text = (
        "🤖 <b>RSS & AD Management Bot</b>\n\n"
        "Choose a mode to manage:\n"
        "📰 <b>RSS</b> - Manage RSS feeds for automatic posting\n"
        "📢 <b>AD</b> - Create beautiful ad cards with photos and buttons\n\n"
        "Use buttons below to navigate:"
    )
    await message.answer(welcome_text, reply_markup=get_main_menu_keyboard())


async def cmd_help(message: types.Message):
    help_text = (
        "🆘 <b>Help Guide</b>\n\n"
        "<b>RSS Mode:</b>\n"
        "• Add RSS feeds for automatic news posting\n"
        "• Set update intervals\n"
        "• Remove existing feeds\n\n"
        "<b>AD Mode:</b>\n"
        "• Create beautiful ad cards with photos\n"
        "• Add titles, descriptions and buttons\n"
        "• Set posting interval and number of views\n\n"
        "<b>Navigation:</b>\n"
        "• Use inline buttons to navigate\n"
        "• /start - Main menu\n"
        "• /help - This help message"
    )
    await message.answer(help_text, reply_markup=get_main_menu_keyboard())


# ====================== ОБРАБОТЧИКИ CALLBACK ======================
async def handle_callback(callback: types.CallbackQuery):
    data = callback.data
    chat_id = callback.from_user.id

    if data == "back_main":
        await callback.message.edit_text(
            "🤖 <b>Main Menu</b>\n\nChoose a mode:",
            reply_markup=get_main_menu_keyboard()
        )

    elif data == "mode_rss":
        await callback.message.edit_text(
            "📰 <b>RSS Management</b>\n\nManage your RSS feeds:",
            reply_markup=get_rss_menu_keyboard()
        )

    elif data == "mode_ad":
        await callback.message.edit_text(
            "📢 <b>AD Management</b>\n\nCreate beautiful ad cards:",
            reply_markup=get_ad_menu_keyboard()
        )

    elif data == "help":
        await callback.message.edit_text(
            "🆘 <b>Help Guide</b>\n\nUse buttons to navigate between modes.",
            reply_markup=get_main_menu_keyboard()
        )

    # RSS операции
    elif data == "list_rss":
        feeds = get_all_feeds()
        if not feeds:
            text = "📭 <b>No RSS feeds</b>\n\nYour RSS list is empty."
        else:
            text = "📃 <b>Your RSS Feeds:</b>\n\n" + "\n".join(
                f"🆔 <b>ID:</b> {f['id']}\n"
                f"📝 <b>Name:</b> {f['name']}\n"
                f"🔗 <b>URL:</b> {f['url']}\n"
                f"⏰ <b>Interval:</b> {f['interval']} min\n{'-' * 30}"
                for f in feeds
            )
        await callback.message.edit_text(text, reply_markup=get_back_to_rss_keyboard())

    elif data == "add_rss":
        user_states[chat_id] = {"mode": "add_rss", "step": 1}
        await callback.message.edit_text(
            "➕ <b>Add RSS Feed</b>\n\nPlease send me the RSS URL:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Cancel", callback_data="mode_rss")]
            ])
        )

    elif data == "remove_rss":
        feeds = get_all_feeds()
        if not feeds:
            await callback.message.edit_text(
                "📭 <b>No RSS feeds to remove</b>",
                reply_markup=get_back_to_rss_keyboard()
            )
            return

        text = "🗑️ <b>Remove RSS Feed</b>\n\nSend me the ID of the feed to remove:\n\n" + "\n".join(
            f"🆔 {f['id']} - {f['name']}" for f in feeds
        )
        await callback.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Back to RSS", callback_data="mode_rss")]
            ])
        )
        user_states[chat_id] = {"mode": "remove_rss", "step": 1}

    # AD операции
    elif data == "list_ads":
        ads = get_all_ads()
        if not ads:
            text = "📭 <b>No advertisements</b>\n\nYour AD list is empty."
        else:
            text = "📢 <b>Your Advertisements:</b>\n\n" + "\n".join(
                f"🆔 <b>ID:</b> {a['id']}\n"
                f"📝 <b>Title:</b> {a['title']}\n"
                f"⏰ <b>Interval:</b> {a['interval']} min\n"
                f"👁️ <b>Views left:</b> {a['views']}\n{'-' * 30}"
                for a in ads
            )
        await callback.message.edit_text(text, reply_markup=get_back_to_ad_keyboard())

    elif data == "add_ad":
        user_states[chat_id] = {"mode": "add_ad", "step": 1}
        await callback.message.edit_text(
            "📸 <b>Step 1/7: Add Photo URL</b>\n\n"
            "Please send me the URL of the photo for your ad:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Cancel", callback_data="mode_ad")]
            ])
        )

    elif data == "remove_ad":
        ads = get_all_ads()
        if not ads:
            await callback.message.edit_text(
                "📭 <b>No ads to remove</b>",
                reply_markup=get_back_to_ad_keyboard()
            )
            return

        text = "🗑️ <b>Remove Advertisement</b>\n\nSend me the ID of the AD to remove:\n\n" + "\n".join(
            f"🆔 {a['id']} - {a['title']} (Views: {a['views']})" for a in ads
        )
        await callback.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Back to AD", callback_data="mode_ad")]
            ])
        )
        user_states[chat_id] = {"mode": "remove_ad", "step": 1}

    await callback.answer()


# ====================== ОБРАБОТЧИКИ СООБЩЕНИЙ ======================
async def handle_message(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()

    if text == "/start":
        await cmd_start(message)
        return
    elif text == "/help":
        await cmd_help(message)
        return

    if chat_id not in user_states:
        await message.answer("Please use /start to begin.", reply_markup=get_main_menu_keyboard())
        return

    state = user_states[chat_id]

    # Добавление RSS
    if state["mode"] == "add_rss":
        if state["step"] == 1:
            state["url"] = text
            state["step"] = 2
            await message.answer("📝 Now send me the RSS feed name:")
        elif state["step"] == 2:
            state["name"] = text
            state["step"] = 3
            await message.answer("⏱ Now send me the update interval in minutes:")
        elif state["step"] == 3:
            try:
                interval = int(text)
                add_feed(state["name"], state["url"], interval)
                await message.answer(
                    "✅ <b>RSS feed added successfully!</b>\n\n"
                    f"📝 Name: {state['name']}\n"
                    f"🔗 URL: {state['url']}\n"
                    f"⏰ Interval: {interval} min",
                    reply_markup=get_back_to_rss_keyboard()
                )
                del user_states[chat_id]
            except ValueError:
                await message.answer("❌ Please enter a valid number for interval.")

    # Удаление RSS
    elif state["mode"] == "remove_rss":
        try:
            feed_id = int(text)
            delete_feed(feed_id)
            await message.answer("✅ <b>RSS feed removed successfully!</b>", reply_markup=get_back_to_rss_keyboard())
            del user_states[chat_id]
        except ValueError:
            await message.answer("❌ Please enter a valid feed ID.")

    # ====================== СОЗДАНИЕ РЕКЛАМЫ ======================
    elif state["mode"] == "add_ad":
        if state["step"] == 1:  # Фото URL
            state["photo_url"] = text
            state["step"] = 2
            await message.answer("🏷️ <b>Step 2/7: Add Title</b>\n\nPlease send me the title:")

        elif state["step"] == 2:  # Заголовок
            state["title"] = text
            state["step"] = 3
            await message.answer("📝 <b>Step 3/7: Add Description</b>\n\nPlease send me the description:")

        elif state["step"] == 3:  # Описание
            state["description"] = text
            state["step"] = 4
            await message.answer("🔗 <b>Step 4/7: Add Button URL</b>\n\nPlease send me the URL for the button:")

        elif state["step"] == 4:  # URL кнопки
            state["button_url"] = text
            state["step"] = 5
            await message.answer(
                "📋 <b>Step 5/7: Add Button Text</b>\n\nPlease send me the text for the button (or 'skip' for default):")

        elif state["step"] == 5:  # Текст кнопки
            if text.lower() == 'skip':
                state["button_text"] = "Перейти →"
            else:
                state["button_text"] = text
            state["step"] = 6
            await message.answer("⏱️ <b>Step 6/7: Add Posting Interval</b>\n\nPlease send me the interval in minutes:")

        elif state["step"] == 6:  # Интервал
            try:
                state["interval"] = int(text)
                state["step"] = 7
                await message.answer("👁️ <b>Step 7/7: Add Views Count</b>\n\nPlease send me the number of views:")
            except ValueError:
                await message.answer("❌ Please enter a valid number for interval.")

        elif state["step"] == 7:  # Количество показов
            try:
                views = int(text)

                add_ad(
                    state["photo_url"],
                    state["title"],
                    state["description"],
                    state["button_text"],
                    state["button_url"],
                    views,
                    state["interval"]
                )

                caption = f"<b>{state['title']}</b>\n\n{state['description']}\n\n⏰ Interval: {state['interval']} min\n👁️ Views: {views}"
                keyboard = get_ad_preview_keyboard(state["button_text"], state["button_url"])

                try:
                    await message.answer_photo(
                        photo=state["photo_url"],
                        caption=caption,
                        reply_markup=keyboard
                    )
                except:
                    await message.answer(f"📸 Photo: {state['photo_url']}\n\n{caption}", reply_markup=keyboard)

                await message.answer("✅ <b>Advertisement created successfully!</b>",
                                     reply_markup=get_back_to_ad_keyboard())
                del user_states[chat_id]

            except ValueError:
                await message.answer("❌ Please enter a valid number for views.")

    # Удаление AD
    elif state["mode"] == "remove_ad":
        try:
            ad_id = int(text)
            decrement_ad_view(ad_id)
            await message.answer("✅ <b>Advertisement removed!</b>", reply_markup=get_back_to_ad_keyboard())
            del user_states[chat_id]
        except ValueError:
            await message.answer("❌ Please enter a valid AD ID.")