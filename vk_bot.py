import logging
import random
import traceback

import redis
import vk_api as vk
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType

from settings import setup_settings, setup_logging, load_questions


def make_keyboard(
    event: VkEventType, vk_api: vk.vk_api.VkApiMethod, keyboard: VkKeyboard
) -> None:
    """
    Sends a message with a keyboard to the user.

    Args:
        event: The event object containing the user's data.
        vk_api: The VK API object.
        keyboard: The keyboard to be sent.
    """
    vk_api.messages.send(
        user_id=event.user_id,
        message="Напряги извилины",
        keyboard=keyboard.get_keyboard(),
        random_id=random.randint(1, 1000),
    )


def handle_new_question_request(
    event: VkEventType,
    vk_api: vk.vk_api.VkApiMethod,
    questions: dict[str, str],
    redis_db: redis.Redis,
) -> None:
    """
    Handles a user's request to receive a new question.

    This function is triggered when the user sends a message containing the
    text "Новый вопрос" or presses the corresponding button on the keyboard.

    Args:
        event (VkEventType): The event object containing the user's data.
        vk_api (VkApiMethod): The VK API object.
        questions (dict[str, str]): A dictionary containing questions as keys and their
            corresponding answers as values.
        redis_db (Redis): A Redis database client object.

    Returns:
        None
    """
    random_question = random.choice(list(questions.keys()))
    vk_api.messages.send(
        message=random_question,
        user_id=event.user_id,
        random_id=random.randint(1, 1000),
    )
    redis_db.set(event.user_id, str(random_question))


def handle_solution_attempt(
    event: VkEventType,
    vk_api: vk.vk_api.VkApiMethod,
    questions: dict[str, str],
    redis_db: redis.Redis,
) -> None:
    """
    Handles a user's attempt to answer the current question.

    This function is triggered when the user sends a message containing their
    answer to the current question. The function checks if the answer is correct,
    and if so, sends a congratulatory message. If the answer is incorrect, sends
    a message with the correct answer or prompts to try again.

    Args:
        event (VkEventType): The event object containing the user's data.
        vk_api (VkApiMethod): The VK API object.
        questions (dict[str, str]): A dictionary containing questions as keys and their
            corresponding answers as values.
        redis_db (Redis): A Redis database client object.

    Returns:
        None
    """
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


def set_keyboard() -> VkKeyboard:
    """
    Sets the keyboard layout for the VK bot.

    Returns:
        VkKeyboard: A VkKeyboard object with the keyboard layout.
    """
    keyboard: VkKeyboard = VkKeyboard(one_time=True)
    keyboard.add_button("Новый вопрос", color=VkKeyboardColor.POSITIVE)
    keyboard.add_button("Сдаться", color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button("Мой счёт", color=VkKeyboardColor.PRIMARY)
    return keyboard


def main() -> None:
    """
    Main function for the VK bot.

    This function runs an infinite loop listening for MESSAGE_NEW events in the
    VK bot's chat. If the event is a message from the user to the bot, it checks
    the message text and either sends a new question or checks the user's answer
    to the current question.

    Logs any errors that occur during the loop.

    Args:
        None

    Returns:
        None
    """

    settings = setup_settings()
    redis_db: redis.Redis = redis.from_url(settings["redis_url"])
    logger: logging.Logger = setup_logging(settings)
    questions: dict[str, str] = load_questions(settings)
    keyboard: VkKeyboard = set_keyboard()

    vk_bot_start_log_message: str = "vk_bot started"
    while True:
        try:
            vk_session: vk.VkApi = vk.VkApi(token=settings["vk_token"])
            vk_api: vk.vk_api.VkApiMethod = vk_session.get_api()
            longpoll: VkLongPoll = VkLongPoll(vk_session)
            logging.info(vk_bot_start_log_message)
            logger.info(vk_bot_start_log_message)
            for event in longpoll.listen():
                if event.type != VkEventType.MESSAGE_NEW or not event.to_me:
                    continue
                make_keyboard(event, vk_api, keyboard)
                if event.text != "Новый вопрос":
                    handle_solution_attempt(event, vk_api, questions, redis_db)
                handle_new_question_request(event, vk_api, questions, redis_db)
        except TimeoutError as timeout_error:
            logging.error(
                f"Превышено время ожидания {timeout_error.with_traceback}"
            )
        except Exception:
            logger.error(f"Бот упал с ошибкой: {traceback.format_exc()}")


if __name__ == "__main__":
    main()
