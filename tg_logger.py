import logging

import telegram


logger = logging.getLogger("bot_logger")


class TelegramLogsHandler(logging.Handler):
    def __init__(self, bot, chat_id):
        super().__init__()
        self.bot = bot
        self.chat_id = chat_id

    def emit(self, record):
        log_entry = self.format(record)
        self.bot.send_message(text=log_entry, chat_id=self.chat_id)


def set_telegram_logger(bot_token, admin_chat_id):
    bot = telegram.Bot(bot_token)
    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramLogsHandler(bot, admin_chat_id))
    return logger
