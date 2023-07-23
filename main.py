import datetime

import pytz
import sentry_sdk
from telegram.ext import (Application, CommandHandler, MessageHandler,
                          PicklePersistence, filters)

from commands.admin import admin, get_insight
from commands.maintenance import maintenance
from configurations import settings
from configurations.settings import (ADMIN_TELEGRAM_USER_ID, IS_MAINTENANCE,
                                     SENTRY_DSN)
from core.handlers import admin_conversation_handler, base_conversation_handler
from utils import create_requirement_folders, logger
from utils.logger import clear_logs_file_daily

if __name__ == "__main__":
    logger.init_logger(f"logs/{settings.NAME}.log")
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0,
    )
    create_requirement_folders()
    persistence = PicklePersistence(filepath="conversation states")
    application = (
        Application.builder()
        .token(settings.TOKEN)
        .read_timeout(50)
        .write_timeout(50)
        .get_updates_read_timeout(50)
        .persistence(persistence)
        .build()
    )
    application.job_queue.run_daily(
        callback=clear_logs_file_daily,
        time=datetime.time(hour=0, minute=0, tzinfo=pytz.timezone("Asia/Tehran")),
        days=(0, 1, 2, 3, 4, 5, 6),
    )
    application.job_queue.run_daily(
        callback=get_insight,
        time=datetime.time(hour=0, minute=0, tzinfo=pytz.timezone("Asia/Tehran")),
        days=(0, 1, 2, 3, 4, 5, 6),
        chat_id=ADMIN_TELEGRAM_USER_ID,
    )
    if IS_MAINTENANCE:
        application.add_handler(CommandHandler("start", maintenance))
        application.add_handler(admin_conversation_handler())
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, maintenance)
        )
    else:
        application.add_handler(base_conversation_handler())
    application.run_polling()
