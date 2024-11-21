# Quiz Telegram Bot

Телеграм-бот викторина. Получаете от бота вопрос и думаете над ответом.
Отправляете ответ, бот проверяет ваш ответ и если всё правильно, можете получить новый вопрос в награду. Нажимая кнопку ~~слабак~~ `Сдаться` получаете ответ бесплатно.

### Предварительные требования

- Python 3.7+
- [pip](https://pip.pypa.io/en/stable/) - менеджер пакетов для Python
- Токен бота Telegram (получить его можно у [BotFather](https://t.me/botfather))
- Ключ api сообщества [VK.com](https://vk.com/) с правами на сообщения сообщества
- [Redis](https://cloud.redis.io/#/)-сервер

### Установка

```bash
git clone https://github.com/Skripko-A/quiz-telegram-bot.git
cd quiz-telegram-bot
python -m venv venv
source venv/bin/activate  # На Windows используйте `venv\Scripts\activate`
pip install -r requirements.txt
```
Создайте файл .env в корневом каталоге для хранения конфигурационных настроек. Файл должен выглядеть следующим образом:
```
TG_BOT_TOKEN=ваш_токен_бота_telegram
TG_ADMIN_CHAT_ID=ваш_id_админа
REDIS_URL=ваш_url_redis
RAW_QUESTIONS_PATH=папка с файлами вопросов и ответов
QUESTIONS_JSON=файл json вопросов и ответов, собранный из файлов папки RAW_QUESTIONS
VK_TOKEN=ключ api VK вашего сообщества
```

### Запуск
Телеграм бот:
```bash
python3 tg_bot.py # Телеграм бот
python3 vk_bot.py # ВК бот
```

### Цель проекта
Учебный проект в рамках прохождения курса веб-разработчика [Devman](https://dvmn.org/)