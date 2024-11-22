import random

import pytest
from unittest.mock import Mock
from telegram import ReplyKeyboardMarkup

from tg_bot import (
    start_command,
    handle_new_question_request,
    handle_solution_attempt,
    State,
)


@pytest.fixture()
def mock_update():
    update = Mock()
    user = Mock(id=123456)
    update.effective_user = user
    return update


@pytest.fixture()
def mock_context():
    """Создание мока для CallbackContext"""
    return Mock()


@pytest.fixture()
def questions():
    return {
        "Вопрос 1": "Ответ 1",
        "Вопрос 2": "Ответ 2",
        "Вопрос 3": "Ответ 3",
    }


@pytest.fixture
def redis_db():
    class MockRedis:
        def __init__(self):
            self.data = {}

        def get(self, user_id):
            return self.data.get(user_id, "No question found")

        def set(self, user_id, question):
            self.data[user_id] = question

    return MockRedis()


def test_start_command(mock_update, mock_context):
    mock_update.message = Mock()
    mock_update.message.reply_text = Mock()

    result = start_command(mock_update, mock_context)

    mock_update.message.reply_text.assert_called_once_with(
        "Напряги извилины",
        reply_markup=ReplyKeyboardMarkup(
            [["Новый вопрос", "Сдаться"], ["Мой счёт"]]
        ),
    )
    assert result == State.NEW_QUESTION.value


def test_handle_new_question_request(
    mock_update, mock_context, questions, redis_db
):
    mock_update.message = Mock()
    mock_update.message.reply_text = Mock()

    result = handle_new_question_request(
        update=mock_update,
        context=mock_context,
        questions=questions,
        redis_db=redis_db,
    )
    mock_update.message.reply_text.assert_called_once_with(
        redis_db.get(mock_update.effective_user.id)
    )
    assert result == State.GUESS_ANSWER.value


def test_handle_solution_attempt(
    mock_update, mock_context, questions, redis_db
):
    redis_db.set(
        mock_update.effective_user.id,
        random.choice(list(questions.keys())).encode(),
    )
    mock_update.message.text = questions[
        redis_db.get(mock_update.effective_user.id).decode("utf-8")
    ]
    mock_update.message.reply_text = Mock()

    handle_solution_attempt(
        update=mock_update,
        context=mock_context,
        questions=questions,
        redis_db=redis_db,
    )
    mock_update.message.reply_text.assert_called_with(
        "Напряги извилины",
        reply_markup=ReplyKeyboardMarkup(
            [["Новый вопрос", "Сдаться"], ["Мой счёт"]]
        ),
    )
