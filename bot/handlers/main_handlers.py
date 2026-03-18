from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import psutil
from datetime import datetime

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Приветственное сообщение с кнопками"""
    builder = InlineKeyboardBuilder()
    
    # Кнопки основного меню
    builder.button(text="🖥 Статистика сервера", callback_data="server_stats")
    builder.button(text="💰 Баланс HostVDS", callback_data="host_balance")
    builder.button(text="🎮 Скидки Steam", callback_data="steam_deals")
    builder.button(text="🔍 Промокоды", callback_data="check_promo")
    builder.button(text="📦 Инвентарь Steam", callback_data="steam_inventory")
    builder.button(text="⭐ Уровень Steam", callback_data="steam_level")
    builder.button(text="📚 Помощь", callback_data="help_menu")
    
    # Настройка сетки кнопок (2 кнопки в ряд)
    builder.adjust(2, 2, 2, 1)
    
    await message.answer(
        "👋 Привет! Я твой многофункциональный бот.\n\n"
        "Выбери функцию из меню ниже:",
        reply_markup=builder.as_markup()
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Помощь с кнопками"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Главное меню", callback_data="main_menu")
    
    await message.answer(
        "📚 **Список команд:**\n\n"
        "/start - Запустить бота и показать главное меню\n"
        "/server - Показать статистику сервера (CPU, RAM, Disk)\n"
        "/host - Показать баланс хостинга HostVDS\n"
        "/steam - Показать скидки на игры в желаемом Steam\n"
        "/promo - Проверить новые промокоды\n"
        "/help - Показать это сообщение\n\n"
        "Также ты можешь использовать кнопки в главном меню для быстрого доступа к функциям! 🚀",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "main_menu")
async def show_main_menu(callback: CallbackQuery):
    """Показать главное меню"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🖥 Статистика сервера", callback_data="server_stats")
    builder.button(text="💰 Баланс HostVDS", callback_data="host_balance")
    builder.button(text="🎮 Скидки Steam", callback_data="steam_deals")
    builder.button(text="🔍 Промокоды", callback_data="check_promo")
    builder.button(text="📦 Инвентарь Steam", callback_data="steam_inventory")
    builder.button(text="⭐ Уровень Steam", callback_data="steam_level")
    builder.button(text="📚 Помощь", callback_data="help_menu")
    builder.adjust(2, 2, 2, 1)
    
    await callback.message.edit_text(
        "👋 Главное меню\n\nВыбери функцию:",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@router.callback_query(F.data == "server_stats")
async def show_server_stats(callback: CallbackQuery):
    """Показать статистику сервера"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        stats_text = (
            f"🖥 **Статистика сервера**\n\n"
            f"📊 CPU: {cpu_percent}%\n"
            f"💾 RAM: {memory.percent}% ({memory.used / 1024**3:.2f} GB / {memory.total / 1024**3:.2f} GB)\n"
            f"💿 Disk: {disk.percent}% ({disk.used / 1024**3:.2f} GB / {disk.total / 1024**3:.2f} GB)\n"
            f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        builder = InlineKeyboardBuilder()
        builder.button(text="🔄 Обновить", callback_data="server_stats")
        builder.button(text="🔙 Главное меню", callback_data="main_menu")
        builder.adjust(2)
        
        await callback.message.edit_text(stats_text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    except Exception as e:
        await callback.message.answer(f"Ошибка получения статистики: {e}")
    
    await callback.answer()


@router.callback_query(F.data == "host_balance")
async def show_host_balance(callback: CallbackQuery):
    """Показать баланс HostVDS"""
    from utils.api_clients import HostVDSClient
    from bot.config import HOSTVDS_LOGIN, HOSTVDS_PASSWORD, HOSTVDS_SERVER_ID
    
    if not HOSTVDS_LOGIN:
        await callback.message.answer("❌ Логин HostVDS не настроен в config.py")
        await callback.answer()
        return
    
    client = HostVDSClient(HOSTVDS_LOGIN, HOSTVDS_PASSWORD, HOSTVDS_SERVER_ID)
    balance = await client.get_balance()
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Обновить", callback_data="host_balance")
    builder.button(text="🔙 Главное меню", callback_data="main_menu")
    builder.adjust(2)
    
    if balance is not None:
        await callback.message.edit_text(
            f"💰 Баланс HostVDS: **{balance}₽**",
            reply_markup=builder.as_markup(),
            parse_mode="Markdown"
        )
    else:
        await callback.message.edit_text(
            "❌ Не удалось получить баланс. Проверьте логин/пароль в config.py.",
            reply_markup=builder.as_markup()
        )
    
    await client.close()
    await callback.answer()


@router.callback_query(F.data == "steam_deals")
async def show_steam_deals(callback: CallbackQuery):
    """Показать скидки в Steam желаемом"""
    from utils.api_clients import SteamClientHandler
    from bot.config import STEAM_USERNAME, STEAM_PASSWORD, STEAM_REGION
    
    if not STEAM_USERNAME:
        await callback.message.answer("❌ Steam аккаунт не настроен в config.py")
        await callback.answer()
        return
    
    client = SteamClientHandler(STEAM_USERNAME, STEAM_PASSWORD, STEAM_REGION)
    deals = await client.get_wishlist_deals()
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Обновить", callback_data="steam_deals")
    builder.button(text="🔙 Главное меню", callback_data="main_menu")
    builder.adjust(2)
    
    if deals:
        text = "🎮 **Скидки в желаемом:**\n\n"
        for deal in deals[:10]:  # Показываем максимум 10 игр
            text += f"• {deal['name']}: -{deal['discount']}% ({deal['price']})\n"
        
        if len(deals) > 10:
            text += f"\n...и еще {len(deals) - 10} игр"
        
        await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    else:
        await callback.message.edit_text(
            "ℹ️ Нет активных скидок в желаемом или ошибка получения данных.\n\n"
            "Примечание: Для работы с Steam может потребоваться Steam Guard код.",
            reply_markup=builder.as_markup()
        )
    
    await client.close()
    await callback.answer()


@router.callback_query(F.data == "help_menu")
async def show_help_menu(callback: CallbackQuery):
    """Показать меню помощи"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Главное меню", callback_data="main_menu")
    
    await callback.message.edit_text(
        "📚 **Помощь**\n\n"
        "Этот бот предоставляет следующие функции:\n\n"
        "🖥 **Статистика сервера** - показывает загрузку CPU, RAM и диска\n"
        "💰 **Баланс HostVDS** - проверяет баланс твоего хостинга\n"
        "🎮 **Скидки Steam** - показывает акции на игры из твоего желаемого\n"
        "🔍 **Промокоды** - мониторинг новых промокодов на CaseBattle и других сайтах\n"
        "📦 **Инвентарь Steam** - показывает твой инвентарь CS:GO\n"
        "⭐ **Уровень Steam** - показывает уровень твоего аккаунта\n\n"
        "Больше функций в разработке! 🚀",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()


# Оставляем поддержку команд для обратной совместимости
@router.message(Command("server"))
async def cmd_server_stats(message: Message):
    """Показать статистику сервера (команда)"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    stats_text = (
        f"🖥 **Статистика сервера**\n\n"
        f"📊 CPU: {cpu_percent}%\n"
        f"💾 RAM: {memory.percent}% ({memory.used / 1024**3:.2f} GB / {memory.total / 1024**3:.2f} GB)\n"
        f"💿 Disk: {disk.percent}% ({disk.used / 1024**3:.2f} GB / {disk.total / 1024**3:.2f} GB)\n"
        f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    await message.answer(stats_text, parse_mode="Markdown")


@router.message(Command("host"))
async def cmd_host_balance(message: Message):
    """Показать баланс HostVDS (команда)"""
    from utils.api_clients import HostVDSClient
    from bot.config import HOSTVDS_LOGIN, HOSTVDS_PASSWORD, HOSTVDS_SERVER_ID
    
    if not HOSTVDS_LOGIN:
        await message.answer("❌ Логин HostVDS не настроен в config.py")
        return
    
    client = HostVDSClient(HOSTVDS_LOGIN, HOSTVDS_PASSWORD, HOSTVDS_SERVER_ID)
    balance = await client.get_balance()
    
    if balance is not None:
        await message.answer(f"💰 Баланс HostVDS: **{balance}₽**", parse_mode="Markdown")
    else:
        await message.answer("❌ Не удалось получить баланс. Проверьте логин/пароль в config.py.")
    
    await client.close()


@router.message(Command("steam"))
async def cmd_steam_wishlist(message: Message):
    """Показать скидки в Steam желаемом (команда)"""
    from utils.api_clients import SteamClientHandler
    from bot.config import STEAM_USERNAME, STEAM_PASSWORD, STEAM_REGION
    
    if not STEAM_USERNAME:
        await message.answer("❌ Steam аккаунт не настроен в config.py")
        return
    
    client = SteamClientHandler(STEAM_USERNAME, STEAM_PASSWORD, STEAM_REGION)
    deals = await client.get_wishlist_deals()
    
    if deals:
        text = "🎮 **Скидки в желаемом:**\n\n"
        for deal in deals[:10]:
            text += f"• {deal['name']}: -{deal['discount']}% ({deal['price']})\n"
        await message.answer(text, parse_mode="Markdown")
    else:
        await message.answer("ℹ️ Нет активных скидок в желаемом или ошибка получения данных.")
    
    await client.close()
