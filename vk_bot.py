import random

from environs import Env
import vk_api as vk
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType


def echo(event, vk_api):
    vk_api.messages.send(
        user_id=event.user_id,
        message=event.text,
        random_id=random.randint(1, 1000),
    )


def make_keyboard(event, vk_api, keyboard):
    vk_api.messages.send(
        user_id=event.user_id,
        message="Напряги извилины",
        keyboard=keyboard.get_keyboard(),
        random_id=random.randint(1, 1000),
    )


if __name__ == "__main__":
    env = Env()
    env.read_env()
    vk_session = vk.VkApi(token=env.str("VK_TOKEN"))
    vk_api = vk_session.get_api()
    keyboard = VkKeyboard(one_time=True)

    keyboard.add_button("Новый вопрос", color=VkKeyboardColor.POSITIVE)
    keyboard.add_button("Сдаться", color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button("Мой счёт", color=VkKeyboardColor.PRIMARY)

    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            echo(event, vk_api)
            make_keyboard(event, vk_api, keyboard)
