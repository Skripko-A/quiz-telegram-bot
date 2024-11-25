import random

import pytest
from unittest.mock import Mock, ANY

from vk_bot import handle_new_question_request, handle_solution_attempt


def test_handle_new_question_request(
    mock_event,
    mock_vk_api,
    mock_questions,
    mock_redis_db,
):

    handle_new_question_request(
        event=mock_event,
        vk_api=mock_vk_api,
        questions=mock_questions,
        redis_db=mock_redis_db,
    )
    mock_vk_api.messages.send.assert_called_once_with(
        message=mock_redis_db.get(mock_event.user_id),
        user_id=mock_event.user_id,
        random_id=ANY,
    )


def test_handle_solution_attempt(
    mock_event,
    mock_vk_api,
    mock_questions,
    mock_redis_db,
):
    mock_redis_db.set(
        mock_event.user_id,
        random.choice(list(mock_questions.keys())).encode(),
    )
    mock_event.text = mock_questions[
        mock_redis_db.get(mock_event.user_id).decode("utf-8")
    ]

    result = handle_solution_attempt(
        event=mock_event,
        vk_api=mock_vk_api,
        questions=mock_questions,
        redis_db=mock_redis_db,
    )

    mock_vk_api.messages.send.assert_called_once_with(
        message="Правильно!",
        user_id=mock_event.user_id,
        random_id=ANY,
    )
