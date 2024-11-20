from enum import Enum
from functools import partial
import json
import logging
from pathlib import Path
import random

from environs import Env
import redis
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    ConversationHandler,
)


class State(Enum):
    NEW_QUESTION = 1
    GUESS_ANSWER = 2


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


def start_command(update: Update, context: CallbackContext) -> int:
    keyboard = [
        ["Новый вопрос", "Сдаться"],
        ["Мой счёт"],
    ]
    update.message.reply_text(
        "Напряги извилины", reply_markup=ReplyKeyboardMarkup(keyboard)
    )
    return State.NEW_QUESTION.value


def handle_new_question_request(
    update: Update, context: CallbackContext, questions, redis_db
) -> int:
    random_question = random.choice(list(questions.keys()))
    update.message.reply_text(random_question)
    redis_db.set(update.effective_user.id, str(random_question))
    return State.GUESS_ANSWER.value


def handle_solution_attempt(
    update: Update, context: CallbackContext, questions, redis_db
) -> int:
    user_id = update.effective_user.id
    question = redis_db.get(user_id)

    question = question.decode("utf-8")
    user_answer = update.message.text
    correct_answer = (
        questions[question].split(". ")[0].lstrip("Ответ:\n").rstrip(".")
    )

    if correct_answer.lower() in user_answer.lower():
        update.message.reply_text("Правильно!")
        return start_command(update, context)
    elif update.message.text == "Сдаться":
        user_id = update.effective_user.id
        question = redis_db.get(user_id)
        question = question.decode("utf-8")
        correct_answer = questions[question].lstrip("Ответ:\n")
        update.message.reply_text(f"Правильный ответ: {correct_answer}")
        return start_command(update, context)
    else:
        update.message.reply_text("Неправильно. Попробуйте ещё раз.")
        print(correct_answer)
        return State.GUESS_ANSWER.value


def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Если хотите, можете начать заново с /start.")
    return start_command(update, context)


def main() -> None:
    env = Env()
    env.read_env()
    updater = Updater(env.str("TG_BOT_TOKEN"))
    redis_db = redis.Redis(
        host=env("REDIS_HOST"),
        port=env.int("REDIS_PORT"),
        password=env("REDIS_PASSWORD"),
    )

    with open(Path(env("QUESTIONS_JSON")), "r", encoding="utf-8") as json_file:
        questions = json.load(json_file)

    dispatcher = updater.dispatcher

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_command)],
        states={
            State.NEW_QUESTION.value: [
                MessageHandler(
                    Filters.text
                    & ~Filters.command
                    & Filters.regex("^Новый вопрос$"),
                    partial(
                        handle_new_question_request,
                        questions=questions,
                        redis_db=redis_db,
                    ),
                ),
            ],
            State.GUESS_ANSWER.value: [
                MessageHandler(
                    Filters.text & ~Filters.command,
                    partial(
                        handle_solution_attempt,
                        questions=questions,
                        redis_db=redis_db,
                    ),
                )
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    dispatcher.add_handler(conversation_handler)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
