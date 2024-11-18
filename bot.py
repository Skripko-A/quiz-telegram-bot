from functools import partial
import logging
import random

from environs import Env
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)

from prepare_questions import create_questions_answers

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


def start_command(update: Update, context: CallbackContext) -> None:
    custom_keyboard = [
        ["Новый вопрос", "Сдаться"],
        ["Мой счёт"],
    ]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    update.message.reply_text(
        "Custom Keyboard test", reply_markup=reply_markup
    )


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Help")


def keyboard_handler(
    update: Update, context: CallbackContext, questions: dict
) -> None:
    random_question = random.choice(list(questions.keys()))
    if update.message.text == "Новый вопрос":
        update.message.reply_text(random_question)


def main() -> None:
    env = Env()
    env.read_env()
    updater = Updater(env.str("TG_BOT_TOKEN"))
    questions = create_questions_answers("questions/1vs1200.txt")
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("help", help_command))

    dispatcher.add_handler(
        MessageHandler(
            Filters.text & ~Filters.command,
            partial(keyboard_handler, questions=questions),
        )
    )

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
