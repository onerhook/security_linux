import asyncio
import logging
from aiogram import Bot, Dispatcher
from bot.config import BOT_TOKEN, ADMIN_ID
from bot.handlers.main_handlers import router as main_router
from bot.handlers.steam_handlers import router as steam_router, start_promo_monitoring

# Настройка логирования
logging.basicConfig(level=logging.INFO)

async def main():
    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    # Регистрация роутеров
    dp.include_router(main_router)
    dp.include_router(steam_router)
    
    # Проверка данных администратора
    if ADMIN_ID == 0:
        logging.warning("⚠️ ADMIN_ID не настроен! Рекомендуется указать свой Telegram ID в config.py")
    
    logging.info("🤖 Бот запускается...")
    
    # Запускаем фоновую задачу для мониторинга промокодов
    asyncio.create_task(start_promo_monitoring(bot, ADMIN_ID))
    
    try:
        # Запуск polling
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()
        logging.info("Бот остановлен")


if __name__ == "__main__":
    asyncio.run(main())
