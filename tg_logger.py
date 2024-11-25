import logging

import telegram


logger = logging.getLogger("bot_logger")


class TelegramLogsHandler(logging.Handler):
    def __init__(self, bot: telegram.Bot, chat_id: int) -> None:
        """
        Initializes a TelegramLogsHandler instance.

        Args:
            bot (telegram.Bot): Telegram Bot API object.
            chat_id (int): The Telegram chat ID where logs will be sent.

        Returns:
            None
        """
        super().__init__()
        self.bot = bot
        self.chat_id = chat_id

    def emit(self, record: logging.LogRecord) -> None:
        """
        Sends a log record to a Telegram chat.

        This method formats the specified log record and sends it as a message
        to the configured Telegram chat using the bot instance.

        Args:
            record (logging.LogRecord): The log record to be sent, containing
                                all the log information.
        Returns:
            None
        """
        log_entry = self.format(record)
        self.bot.send_message(text=log_entry, chat_id=self.chat_id)


def set_telegram_logger(bot_token: str, admin_chat_id: int) -> logging.Logger:
    """
    Configures a logger instance to send log records to a Telegram chat.

    Args:
        bot_token (str): The Telegram Bot API token.
        admin_chat_id (int): The Telegram chat ID where logs will be sent.

    Returns:
        logging.Logger: A logger instance configured to send logs to the specified Telegram chat.
    """
    bot = telegram.Bot(bot_token)
    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramLogsHandler(bot, admin_chat_id))
    return logger
