from enum import Enum
from functools import partial
import logging
import random
import traceback

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

from settings import settings


class State(Enum):
    NEW_QUESTION = 1
    GUESS_ANSWER = 2


def start_command(update: Update, context: CallbackContext) -> int:
    """
    Initiates the bot's conversation with the user by sending a welcome message
    and displaying a keyboard with options for the user to choose from.

    Args:
        update (Update): Incoming update object that contains all the information
                         about the incoming message.
        context (CallbackContext): Provides access to context-related data.

    Returns:
        int: The next state of the conversation, which is set to NEW_QUESTION.
    """
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
    """
    Handles a user's request to receive a new question.

    This function is triggered when the user sends a message containing the
    text "Новый вопрос" or presses the corresponding button on the keyboard.

    Args:
        update (Update): Incoming update object that contains all the information
                         about the incoming message.
        context (CallbackContext): Provides access to context-related data.
        questions (dict): A dictionary containing questions as keys and their
                         corresponding answers as values.
        redis_db (Redis): A Redis database client object.

    Returns:
        int: The next state of the conversation, which is set to GUESS_ANSWER.
    """
    random_question = random.choice(list(questions.keys()))
    update.message.reply_text(random_question)
    redis_db.set(update.effective_user.id, str(random_question))
    return State.GUESS_ANSWER.value


def handle_solution_attempt(
    update: Update, context: CallbackContext, questions, redis_db
) -> int:
    """
    Handles a user's attempt to answer the current question.

    This function is triggered when the user sends a message containing their
    answer to the current question. The function checks if the answer is correct,
    and if so, sends a congratulatory message and returns to the NEW_QUESTION
    state. If the answer is incorrect, sends a message with the correct answer
    and returns to the GUESS_ANSWER state.

    Args:
        update (Update): Incoming update object that contains all the information
                         about the incoming message.
        context (CallbackContext): Provides access to context-related data.
        questions (dict): A dictionary containing questions as keys and their
                         corresponding answers as values.
        redis_db (Redis): A Redis database client object.

    Returns:
        int: The next state of the conversation, which is set to NEW_QUESTION
             if the answer is correct, or GUESS_ANSWER if the answer is incorrect.
    """
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
        correct_answer = questions[question].lstrip("Ответ:\n")
        update.message.reply_text(f"Правильный ответ: {correct_answer}")
        return start_command(update, context)
    else:
        update.message.reply_text("Неправильно. Попробуйте ещё раз.")
        start_command(update, context)
        print(correct_answer)
        return State.GUESS_ANSWER.value


def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Если хотите, можете начать заново с /start.")
    return start_command(update, context)


def main() -> None:
    """
    Initializes and starts the Telegram bot for handling quiz interactions.

    This function sets up the required components for the bot, including the
    Redis database connection, logging, and loading questions. It configures
    the updater and dispatcher to manage incoming updates and handlers for
    user interactions through commands and messages. The bot runs in polling
    mode, continuously checking for new messages and responding accordingly.

    The ConversationHandler is used to manage different states of the
    conversation, facilitating the transition between requesting a new question
    and attempting to answer it. The bot also handles exceptions, logging errors
    encountered during execution.

    Returns:
        None

    Raises:
        ConnectionError: If there is a network-related issue.
        Exception: For any other exception that occurs during bot operation.
    """
    redis_db: redis.Redis = redis.from_url(settings.redis_url)
    logger: logging.Logger = settings.setup_logging()
    questions: dict[str, str] = settings.load_questions()
    updater: Updater = Updater(settings.tg_bot_token)
    dispatcher: Dispatcher = updater.dispatcher
    """
    Creates a ConversationHandler for managing the Telegram bot's interaction flow.
    
    This handler manages the states of the conversation, handling user requests
    for new questions and solution attempts. It defines entry points for starting
    the conversation and fallbacks for canceling it.
    
    States:
        - NEW_QUESTION: Triggers when the user requests a new question.
        - GUESS_ANSWER: Triggers when the user attempts to answer a question.
    
    Entry Points:
        - CommandHandler for the "start" command to initiate the conversation.
    
    Fallbacks:
        - CommandHandler for the "cancel" command to end the conversation.
    
    The handler uses Redis to track the current question for each user.
    """
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

    bot_start_log_message: str = "tg_bot started"
    logging.info(bot_start_log_message)
    logger.info(bot_start_log_message)

    while True:
        try:
            updater.start_polling()
            updater.idle()
        except ConnectionError as connection_error:
            logging.error(f"Ошибка сети {connection_error}")
        except Exception:
            logger.error(f"Бот упал с ошибкой: {traceback.format_exc()}")


if __name__ == "__main__":
    main()
