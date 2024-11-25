import random

from unittest.mock import Mock
from telegram import ReplyKeyboardMarkup

from tg_bot import (
    start_command,
    handle_new_question_request,
    handle_solution_attempt,
    State,
)


def test_start_command(mock_update, mock_context):
    result = start_command(mock_update, mock_context)

    mock_update.message.reply_text.assert_called_once_with(
        "Напряги извилины",
        reply_markup=ReplyKeyboardMarkup(
            [["Новый вопрос", "Сдаться"], ["Мой счёт"]]
        ),
    )

    assert result == State.NEW_QUESTION.value


def test_handle_new_question_request(
    mock_update,
    mock_context,
    mock_questions,
    mock_redis_db,
):
    mock_update.message.text = "Нagagвопрос"
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
    mock_update,
    mock_context,
    mock_questions,
    mock_redis_db,
):
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
