import random

import pytest
from unittest.mock import Mock


@pytest.fixture()
def mock_update():
    update = Mock()
    user = Mock(id=random.randint(1, 1000))
    update.effective_user = user
    return update


@pytest.fixture()
def mock_context():
    """Создание мока для CallbackContext"""
    return Mock()


@pytest.fixture()
def mock_questions():
    return {
        "Вопрос 1": "Ответ 1",
        "Вопрос 2": "Ответ 2",
        "Вопрос 3": "Ответ 3",
    }


@pytest.fixture
def mock_redis_db():
    class MockRedis:
        def __init__(self):
            self.data = {}

        def get(self, user_id):
            return self.data.get(user_id, "No question found")

        def set(self, user_id, question):
            self.data[user_id] = question

    return MockRedis()


@pytest.fixture()
def mock_vk_api():
    vk_api = Mock()
    return vk_api


@pytest.fixture()
def mock_event():
    event = Mock()
    user = Mock(id=random.randint(1, 1000))
    event.user_id = user
    return event
