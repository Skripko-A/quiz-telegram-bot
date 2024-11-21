import json
import logging
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from tg_logger import set_telegram_logger


class Settings(BaseSettings):
    questions_json: str = str(
        Path(__file__).resolve().parent / "questions.json"
    )
    questions_json: str

    model_config = SettingsConfigDict(
        env_file=f"{Path(__file__).resolve().parent}/.env",
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
        with open(
            Path(self.questions_json), "r", encoding="utf-8"
        ) as json_file:
            return json.load(json_file)


settings = Settings()

logger = settings.setup_logging()

questions = settings.load_questions()

logger.info("Настройка завершена, вопросы загружены.")
