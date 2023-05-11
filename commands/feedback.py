# encoding: utf-8
import time
from datetime import datetime
from datetime import timezone
from logging import getLogger

import psycopg2
from telegram import Update
from telegram.constants import ChatAction
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from telegram.ext import ConversationHandler

from configurations.settings import ADMIN_TELEGRAM_USER_ID
from connectors.postgresql import create_user
from constants import YES, NO
from constants.keys import BACK_KEY
from constants.messages import GOODBYE_WE_ARE_SORRY, FEEDBACK_MESSAGE, NEW_MESSAGE, YOUR_MESSAGE_WAS_SENT, NEW_TEXT_MESSAGE, WHAT_DO_YOU_WANT
from constants.messages import PRIVACY_MESSAGE
from constants.messages import WELCOME_MESSAGE
from constants.states import HOME_STATE, FEEDBACK_STATE
from core.keyboards import base_keyboard, back_keyboard
from utils.decorators import send_action

# Init logger

logger = getLogger(__name__)


@send_action(ChatAction.TYPING)
async def get_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Select an action: Adding parent/child or show data."""
    # pylint: disable=unused-argument
    await context.bot.send_message(
        chat_id=update.message.chat_id, text=FEEDBACK_MESSAGE)
    return FEEDBACK_STATE


@send_action(ChatAction.TYPING)
async def send_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Select an action: Adding parent/child or show data."""
    # pylint: disable=unused-argument
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name
    last_name = update.effective_user.last_name
    username = update.effective_user.username
    if update.message.text == BACK_KEY:
        await update.message.reply_text(WHAT_DO_YOU_WANT,
                                        reply_markup=base_keyboard)
        return HOME_STATE

    if update.message.text:
        await context.bot.send_message(
            chat_id=ADMIN_TELEGRAM_USER_ID,
            text=NEW_TEXT_MESSAGE.format(
                user_id=user_id, first_name=first_name,
                last_name=last_name, username=username,
                message=update.message.text
            ),
            parse_mode=ParseMode.MARKDOWN
        )
    elif update.message.video:
        await context.bot.send_video(
            chat_id=ADMIN_TELEGRAM_USER_ID,
            video=update.message.video,
        )
        await context.bot.send_message(
            chat_id=ADMIN_TELEGRAM_USER_ID,
            text=NEW_TEXT_MESSAGE.format(
                user_id=user_id, first_name=first_name,
                last_name=last_name, username=username,
                message=update.message.text
            ),
            parse_mode=ParseMode.MARKDOWN
        )
    elif update.message.audio:
        await context.bot.send_audio(
            chat_id=ADMIN_TELEGRAM_USER_ID,
            audio=update.message.audio
        )
        await context.bot.send_message(
            chat_id=ADMIN_TELEGRAM_USER_ID,
            text=NEW_TEXT_MESSAGE.format(
                user_id=user_id, first_name=first_name,
                last_name=last_name, username=username,
                message=update.message.text
            ),
            parse_mode=ParseMode.MARKDOWN
        )
    elif update.message.document:
        await context.bot.document(
            chat_id=ADMIN_TELEGRAM_USER_ID,
            document=update.message.document
        )
        await context.bot.send_message(
            chat_id=ADMIN_TELEGRAM_USER_ID,
            text=NEW_TEXT_MESSAGE.format(
                user_id=user_id, first_name=first_name,
                last_name=last_name, username=username,
                message=update.message.text
            ),
            parse_mode=ParseMode.MARKDOWN
        )
    elif update.message.photo:
        await context.bot.photo(
            chat_id=ADMIN_TELEGRAM_USER_ID,
            photo=update.message.photo
        )
        await context.bot.send_message(
            chat_id=ADMIN_TELEGRAM_USER_ID,
            text=NEW_TEXT_MESSAGE.format(
                user_id=user_id, first_name=first_name,
                last_name=last_name, username=username,
                message=update.message.text
            ),
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await update.message.reply_text(
            "Your Message Not Valid, Please Try Again",
            reply_markup=back_keyboard
        )
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text=YOUR_MESSAGE_WAS_SENT,
        reply_markup=base_keyboard
    )
    return HOME_STATE