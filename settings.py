import json
import logging
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from tg_logger import set_telegram_logger


BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    tg_bot_token: str
    tg_admin_chat_id: int
    questions_json: str = str(BASE_DIR / "questions.json")
    raw_questions_path: str = str(BASE_DIR / "questions")

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="allow",
    )

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
        with open(self.questions_json, "r", encoding="utf-8") as json_file:
            return json.load(json_file)


settings = Settings()
