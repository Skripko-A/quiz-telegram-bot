import json
import logging
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

from tg_logger import set_telegram_logger


BASE_DIR = Path(__file__).resolve().parent

print(str(BASE_DIR / ".env"))


class Settings(BaseSettings):
    tg_bot_token: Optional[str] = None
    tg_admin_chat_id: Optional[str] = None
    questions_json: Optional[str] = None
    raw_questions_path: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="allow",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.questions_json = str(BASE_DIR / "questions.json")
        self.raw_questions_path = str(BASE_DIR / "questions")

    def setup_logging(self):
        logger = set_telegram_logger(
            bot_token=self.tg_bot_token,
            admin_chat_id=self.tg_admin_chat_id,
        )
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            level=logging.INFO,
        )
        return logger

    def load_questions(self):
        print(self.questions_json)
        print(self.raw_questions_path)
        with open(self.questions_json, "r", encoding="utf-8") as json_file:
            return json.load(json_file)


settings = Settings()
