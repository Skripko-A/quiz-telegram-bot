import json
import logging
from pathlib import Path

from environs import Env

from tg_logger import set_telegram_logger


def setup_settings() -> dict[str, str | int]:
    """
    Reads settings from a .env file in the same directory as this module and
    returns them as a dictionary with the following keys and types:
        - tg_bot_token: str (Telegram bot token)
        - tg_admin_chat_id: int (Telegram chat ID for logs)
        - vk_token: str (VK API token)
        - redis_url: str (URL of the Redis database)
        - questions_json: str (Path to the JSON file containing questions and answers)
        - raw_questions_path: str (Path to the directory containing raw question files)

    The .env file should be in the following format:
    TG_BOT_TOKEN=<token>
    TG_ADMIN_CHAT_ID=<chat_id>
    VK_TOKEN=<token>
    REDIS_URL=<url>
    """
    base_dir = Path(__file__).resolve().parent
    env = Env()
    env.read_env(str(base_dir / ".env"))
    return {
        "tg_bot_token": env("TG_BOT_TOKEN"),
        "tg_admin_chat_id": env.int("TG_ADMIN_CHAT_ID"),
        "vk_token": env("VK_TOKEN"),
        "redis_url": env("REDIS_URL"),
        "questions_json": str(base_dir / "questions.json"),
        "raw_questions_path": str(base_dir / "questions"),
    }


def setup_logging(settings: dict[str, str | int]) -> logging.Logger:
    """
    Configures and returns a logger instance for the application.

    This function sets up logging to output messages in a standard format
    with timestamps, logger names, and log levels. It integrates with a
    Telegram logger to send log records to a specified chat.

    Args:
        settings (dict[str, str | int]): A dictionary containing configuration settings,
                                         including Telegram bot token and admin chat ID.

    Returns:
        logging.Logger: A configured logger instance.
    """
    logger: logging.Logger = set_telegram_logger(
        bot_token=settings["tg_bot_token"],
        admin_chat_id=settings["tg_admin_chat_id"],
    )
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    return logger


def load_questions(settings: dict[str, str | int]) -> dict[str, str]:
    """
    Loads a dictionary of questions and answers from a JSON file.

    Args:
        settings (dict[str, str | int]): A dictionary containing configuration settings,
                                         including the path to the JSON file with questions and answers.

    Returns:
        dict[str, str]: A dictionary with questions as keys and their corresponding answers as values.
    """
    with open(settings["questions_json"], "r", encoding="utf-8") as json_file:
        return json.load(json_file)
