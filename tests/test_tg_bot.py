import random

from unittest.mock import Mock
from telegram import ReplyKeyboardMarkup

from tg_bot import (
    start_command,
    handle_new_question_request,
    handle_solution_attempt,
    State,
)


def test_start_command(mock_update: Mock, mock_context: Mock) -> None:
    """
    Tests the start_command function to ensure it sends the welcome message
    with the correct keyboard layout and returns the NEW_QUESTION state.

    Args:
        mock_update (Mock): Mock object for the Update class.
        mock_context (Mock): Mock object for the CallbackContext.

    Returns:
        None

    Asserts:
        - The reply_text method is called once with the correct message and keyboard.
        - The function returns the NEW_QUESTION state.
    """
    result = start_command(mock_update, mock_context)

    mock_update.message.reply_text.assert_called_once_with(
        "Напряги извилины",
        reply_markup=ReplyKeyboardMarkup(
            [["Новый вопрос", "Сдаться"], ["Мой счёт"]]
        ),
    )

    assert result == State.NEW_QUESTION.value


def test_handle_new_question_request(
    mock_update: Mock,
    mock_context: Mock,
    mock_questions: dict,
    mock_redis_db: Mock,
) -> None:
    """
    Tests the handle_new_question_request function to ensure it sends the question
    and stores it in the Redis database, then returns the GUESS_ANSWER state.

    Args:
        mock_update (Mock): Mock object for the Update class
        mock_context (Mock): Mock object for the CallbackContext
        mock_questions (dict[str, str]): A dictionary containing questions as keys and their
            corresponding answers as values
        mock_redis_db (Mock): Mock object for the Redis client

    Returns:
        None

    Asserts:
        - The reply_text method is called once with the correct question.
        - The question is stored in the Redis database.
        - The function returns the GUESS_ANSWER state.
    """
    result = handle_new_question_request(
        update=mock_update,
        context=mock_context,
        questions=mock_questions,
        redis_db=mock_redis_db,
    )
    mock_update.message.reply_text.assert_called_once_with(
        mock_redis_db.get(mock_update.effective_user.id)
    )
    assert result == State.GUESS_ANSWER.value


def test_handle_solution_attempt(
    mock_update: Mock,
    mock_context: Mock,
    mock_questions: dict[str, str],
    mock_redis_db: Mock,
) -> None:
    """
    Tests the handle_solution_attempt function to ensure it correctly processes
    a user's answer to a question, sends the appropriate response message, and
    transitions to the NEW_QUESTION state if the answer is correct.

    Args:
        mock_update (Mock): Mock object for the Update class.
        mock_context (Mock): Mock object for the CallbackContext.
        mock_questions (dict[str, str]): A dictionary containing questions as keys and their
            corresponding answers as values.
        mock_redis_db (Mock): Mock object for the Redis client.

    Returns:
        None

    Asserts:
        - The reply_text method is called twice with the correct messages.
        - The function returns the NEW_QUESTION state.
    """
    mock_redis_db.set(
        mock_update.effective_user.id,
        random.choice(list(mock_questions.keys())).encode(),
    )
    mock_update.message.text = mock_questions[
        mock_redis_db.get(mock_update.effective_user.id).decode("utf-8")
    ]

    result = handle_solution_attempt(
        update=mock_update,
        context=mock_context,
        questions=mock_questions,
        redis_db=mock_redis_db,
    )
    assert mock_update.message.reply_text.call_count == 2
    mock_update.message.reply_text.assert_any_call("Правильно!")
    mock_update.message.reply_text.assert_any_call(
        "Напряги извилины",
        reply_markup=ReplyKeyboardMarkup(
            [["Новый вопрос", "Сдаться"], ["Мой счёт"]]
        ),
    )

    assert result == State.NEW_QUESTION.value
