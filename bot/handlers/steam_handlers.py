from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.promo_monitor import PromoMonitor, SteamExtendedClient
from bot.config import STEAM_USERNAME, STEAM_PASSWORD, ADMIN_ID, PROMO_CHECK_INTERVAL
import asyncio

router = Router()

# Глобальный монитор промокодов
promo_monitor = PromoMonitor()
steam_extended = SteamExtendedClient(STEAM_USERNAME, STEAM_PASSWORD) if STEAM_USERNAME else None


@router.message(Command("promo"))
async def cmd_check_promo(message: Message):
    """Ручная проверка новых промокодов"""
    await message.answer("🔍 Проверяю промокоды...")
    
    try:
        await promo_monitor.start()
        new_promos = await promo_monitor.get_new_promos()
        
        if new_promos:
            for promo in new_promos:
                text = f"🎁 **Новый промокод!**\n\n"
                text += f"📌 Источник: {promo['source']}\n"
                text += f"📝 Название: {promo['title']}\n"
                if promo['code']:
                    text += f"🔑 Код: `{promo['code']}`\n"
                if promo['link']:
                    text += f"🔗 Ссылка: {promo['link']}"
                
                await message.answer(text, parse_mode="Markdown")
        else:
            await message.answer("ℹ️ Новых промокодов не найдено.")
            
    except Exception as e:
        await message.answer(f"❌ Ошибка при проверке промокодов: {e}")
    finally:
        await promo_monitor.stop()


@router.callback_query(F.data == "check_promo")
async def callback_check_promo(callback: CallbackQuery):
    """Проверка промокодов через кнопку"""
    await callback.answer("🔍 Проверяю промокоды...")
    
    try:
        await promo_monitor.start()
        new_promos = await promo_monitor.get_new_promos()
        
        if new_promos:
            for promo in new_promos[:5]:  # Максимум 5 за раз
                text = f"🎁 **Новый промокод!**\n\n"
                text += f"📌 Источник: {promo['source']}\n"
                text += f"📝 Название: {promo['title']}\n"
                if promo['code']:
                    text += f"🔑 Код: `{promo['code']}`\n"
                if promo['link']:
                    text += f"🔗 Ссылка: {promo['link']}"
                
                await callback.message.answer(text, parse_mode="Markdown")
        else:
            await callback.message.answer("ℹ️ Новых промокодов не найдено.")
            
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка при проверке промокодов: {e}")
    finally:
        await promo_monitor.stop()


@router.callback_query(F.data == "steam_inventory")
async def callback_steam_inventory(callback: CallbackQuery):
    """Показ инвентаря Steam"""
    await callback.answer("🎒 Загружаю инвентарь...")
    
    if not steam_extended:
        await callback.message.answer("❌ Steam аккаунт не настроен")
        return
    
    try:
        inventory = await steam_extended.get_inventory(730)  # CS:GO
        
        if inventory:
            text = f"🎒 **Инвентарь CS:GO**\n\n"
            text += f"Всего предметов: {len(inventory)}\n\n"
            
            # Показываем первые 10 предметов
            for item in inventory[:10]:
                name = item.get('name', 'Unknown')
                text += f"• {name}\n"
            
            if len(inventory) > 10:
                text += f"\n...и еще {len(inventory) - 10} предметов"
            
            builder = InlineKeyboardBuilder()
            builder.button(text="🔄 Обновить", callback_data="steam_inventory")
            builder.button(text="🔙 Главное меню", callback_data="main_menu")
            builder.adjust(2)
            
            await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
        else:
            await callback.message.answer("ℹ️ Инвентарь пуст или профиль закрыт")
            
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка: {e}")


@router.callback_query(F.data == "steam_level")
async def callback_steam_level(callback: CallbackQuery):
    """Показ уровня Steam аккаунта"""
    await callback.answer("📊 Загружаю информацию...")
    
    if not steam_extended:
        await callback.message.answer("❌ Steam аккаунт не настроен")
        return
    
    try:
        level = await steam_extended.get_account_level()
        
        text = f"📊 **Уровень Steam аккаунта**\n\n"
        text += f"Пользователь: {STEAM_USERNAME}\n"
        text += f"Уровень: **{level}** ⭐"
        
        builder = InlineKeyboardBuilder()
        builder.button(text="🔄 Обновить", callback_data="steam_level")
        builder.button(text="🔙 Главное меню", callback_data="main_menu")
        builder.adjust(2)
        
        await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
        
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка: {e}")


@router.callback_query(F.data == "steam_market")
async def callback_steam_market(callback: CallbackQuery):
    """Поиск на торговом рынке Steam"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Главное меню", callback_data="main_menu")
    
    await callback.message.answer(
        "🏪 **Торговая площадка Steam**\n\n"
        "Функция в разработке. Скоро можно будет искать предметы по названию!",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "trade_offers")
async def callback_trade_offers(callback: CallbackQuery):
    """Показ активных трейд-офферов"""
    await callback.answer("📦 Загружаю трейд-офферы...")
    
    if not steam_extended:
        await callback.message.answer("❌ Steam аккаунт не настроен")
        return
    
    try:
        offers = await steam_extended.get_trade_offers()
        
        if offers:
            text = f"📦 **Активные трейд-офферы**\n\n"
            text += f"Найдено: {len(offers)}\n\n"
            
            for i, offer in enumerate(offers[:5], 1):
                text += f"{i}. Статус: {offer['status']}\n"
            
            builder = InlineKeyboardBuilder()
            builder.button(text="🔄 Обновить", callback_data="trade_offers")
            builder.button(text="🔙 Главное меню", callback_data="main_menu")
            builder.adjust(2)
            
            await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
        else:
            await callback.message.answer("ℹ️ Активных трейд-офферов нет")
            
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка: {e}")


async def start_promo_monitoring(bot: Bot, chat_id: int):
    """Фоновая задача для мониторинга промокодов"""
    while True:
        try:
            await promo_monitor.start()
            new_promos = await promo_monitor.get_new_promos()
            
            if new_promos:
                for promo in new_promos:
                    text = f"🎁 **Новый промокод!**\n\n"
                    text += f"📌 Источник: {promo['source']}\n"
                    text += f"📝 Название: {promo['title']}\n"
                    if promo['code']:
                        text += f"🔑 Код: `{promo['code']}`\n"
                    if promo['link']:
                        text += f"🔗 Ссылка: {promo['link']}"
                    
                    try:
                        await bot.send_message(chat_id, text, parse_mode="Markdown")
                    except Exception as e:
                        print(f"Ошибка отправки уведомления: {e}")
            
            await promo_monitor.stop()
            
        except Exception as e:
            print(f"Ошибка в мониторинге промокодов: {e}")
        
        await asyncio.sleep(PROMO_CHECK_INTERVAL)
