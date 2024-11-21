import logging
import random
import traceback

import redis
import vk_api as vk
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType

from settings import settings


def make_keyboard(event, vk_api, keyboard):
    vk_api.messages.send(
        user_id=event.user_id,
        message="Напряги извилины",
        keyboard=keyboard.get_keyboard(),
        random_id=random.randint(1, 1000),
    )


def handle_new_question_request(event, vk_api, questions, redis_db):
    random_question = random.choice(list(questions.keys()))
    vk_api.messages.send(
        message=random_question,
        user_id=event.user_id,
        random_id=random.randint(1, 1000),
    )
    redis_db.set(event.user_id, str(random_question))


def handle_solution_attempt(event, vk_api, questions, redis_db):
    user_id = event.user_id
    question = redis_db.get(user_id)

    question = question.decode("utf-8")
    user_answer = event.text
    correct_answer = (
        questions[question].split(". ")[0].lstrip("Ответ:\n").rstrip(".")
    )

    if correct_answer.lower() in user_answer.lower():
        vk_api.messages.send(
            message="Правильно!",
            user_id=event.user_id,
            random_id=random.randint(1, 1000),
        )
    elif event.text == "Сдаться":
        correct_answer = questions[question].lstrip("Ответ:\n")
        vk_api.messages.send(
            message=f"Правильный ответ: {correct_answer}",
            user_id=event.user_id,
            random_id=random.randint(1, 1000),
        )
    else:
        vk_api.messages.send(
            message="Неправильно",
            user_id=event.user_id,
            random_id=random.randint(1, 1000),
        )
        print(correct_answer)


def set_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("Новый вопрос", color=VkKeyboardColor.POSITIVE)
    keyboard.add_button("Сдаться", color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button("Мой счёт", color=VkKeyboardColor.PRIMARY)
    return keyboard


def main():
    redis_db = redis.from_url(settings.redis_url)
    logger = settings.setup_logging()
    questions = settings.load_questions()
    keyboard = set_keyboard()

    vk_bot_start_log_message = "vk_bot started"
    while True:
        try:
            vk_session = vk.VkApi(token=settings.vk_token)
            vk_api = vk_session.get_api()
            longpoll = VkLongPoll(vk_session)
            logging.info(vk_bot_start_log_message)
            logger.info(vk_bot_start_log_message)
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    make_keyboard(event, vk_api, keyboard)
                    if event.text == "Новый вопрос":
                        handle_new_question_request(
                            event, vk_api, questions, redis_db
                        )
                    else:
                        handle_solution_attempt(
                            event, vk_api, questions, redis_db
                        )
        except TimeoutError as timeout_error:
            logging.error(
                f"Превышено время ожидания {timeout_error.with_traceback}"
            )
        except Exception:
            logger.error(f"Бот упал с ошибкой: {traceback.format_exc()}")


if __name__ == "__main__":
    main()
