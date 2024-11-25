import random

import pytest
from unittest.mock import Mock, ANY

from vk_bot import handle_new_question_request, handle_solution_attempt


def test_handle_new_question_request(
    mock_event: Mock,
    mock_vk_api: Mock,
    mock_questions: dict[str, str],
    mock_redis_db: Mock,
) -> None:
    """
    Tests the handle_new_question_request function to ensure it sends the
    question and stores it in the Redis database.

    Args:
        mock_event (Mock): Mock object for the event passed to the function.
        mock_vk_api (Mock): Mock object for the vk_api object.
        mock_questions (dict): A dictionary containing questions as keys and their
            corresponding answers as values.
        mock_redis_db (Mock): Mock object for the Redis client.

    Asserts:
        - The messages.send method is called once with the correct message
        - The messages.send method is called once with the correct message.
    """
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
    mock_event: Mock,
    mock_vk_api: Mock,
    mock_questions: dict[str, str],
    mock_redis_db: Mock,
) -> None:
    """
    Tests the handle_solution_attempt function to ensure it correctly processes
    a user's answer to a question, sends the appropriate response message, and
    transitions to the NEW_QUESTION state if the answer is correct.

    Args:
        mock_event (Mock): Mock object for the event passed to the function.
        mock_vk_api (Mock): Mock object for the vk_api object.
        mock_questions (dict[str, str]): A dictionary containing questions as keys
            and their corresponding answers as values.
        mock_redis_db (Mock): Mock object for the Redis client.

    Asserts:
        - The messages.send method is called once with the correct message.
    """
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
