import random

import pytest
from unittest.mock import Mock


@pytest.fixture()
def mock_update() -> Mock:
    """
    Creates a mock object for the Update class.

    This fixture simulates a Telegram Update object with a mock user having
    a randomly generated ID.

    Returns:
        Mock: A mock instance representing the Update with a mock effective user.
    """
    update = Mock()
    user = Mock(id=random.randint(1, 1000))
    update.effective_user = user
    return update


@pytest.fixture()
def mock_context() -> Mock:
    """Creates a mock object for the CallbackContext.

    Returns:
        Mock: A mock instance representing the CallbackContext.
    """
    return Mock()


@pytest.fixture()
def mock_questions() -> dict[str, str]:
    """
    Provides a mock dictionary of questions and their corresponding answers.

    This fixture simulates a set of questions and answers for testing purposes,
    where each question is mapped to its correct answer in the dictionary.

    Returns:
        dict[str, str]: A mock dictionary containing questions as keys and answers as values.
    """
    return {
        "Вопрос 1": "Ответ 1",
        "Вопрос 2": "Ответ 2",
        "Вопрос 3": "Ответ 3",
    }


@pytest.fixture
def mock_redis_db() -> MockRedis:
    """
    Provides a mock Redis database client.

    This fixture simulates a Redis-like database for testing purposes, allowing
    storage and retrieval of questions based on user IDs. It mimics basic
    get and set operations to manage questions for different users.

    Returns:
        MockRedis: An instance of a mock Redis client with get and set methods.
    """

    class MockRedis:
        def __init__(self) -> None:
            self.data = {}

        def get(self, user_id: int) -> str:
            return self.data.get(user_id, "No question found")

        def set(self, user_id: int, question: str) -> None:
            self.data[user_id] = question

    return MockRedis()


@pytest.fixture()
def mock_vk_api() -> Mock:
    """
    Provides a mock VK API object.

    This fixture returns a mock instance of the VK API object, which can be used
    to simulate VK API interactions for testing purposes.

    Returns:
        Mock: A mock instance of the VK API object.
    """
    vk_api: Mock = Mock()
    return vk_api


@pytest.fixture()
def mock_event() -> Mock:
    """
    Provides a mock VK event object.

    This fixture returns a mock instance of the event object containing a
    randomly generated user ID of type int, which can be used to simulate VK events for
    testing purposes.

    Returns:
        Mock: A mock instance of the event object with an integer user ID.
    """
    event: Mock = Mock()
    user: Mock = Mock(id=random.randint(1, 1000))
    event.user_id = user
    return event
