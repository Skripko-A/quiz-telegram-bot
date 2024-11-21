import json
from pathlib import Path

import chardet
from environs import Env

from settings import settings


def open_questions(filename: str) -> str:
    with open(f"{filename}", "rb") as raw:
        encode_type = chardet.detect(raw.read(1000))["encoding"]

    with open(f"{filename}", encoding=encode_type) as file:
        text = file.read()
    return text


def create_questions_answers(files: list[str]) -> dict[str:str]:
    questions = []
    answers = []
    for filename in files:
        text = open_questions(filename)
        text_splitted = [
            paragraph.strip()
            for paragraph in text.split("\n\n")
            if paragraph.strip()
        ]
        for line in text_splitted:
            if line.startswith("Вопрос"):
                questions.append(line)
            if line.startswith("Ответ"):
                answers.append(line)
    questions_and_answers = {
        question: answer for question, answer in zip(questions, answers)
    }
    return questions_and_answers


def main():
    directory_path = Path(settings.raw_questions_path)
    files = [file for file in directory_path.iterdir() if file.is_file()]
    questions_and_answers = create_questions_answers(files)
    with open("questions.json", "w", encoding="utf-8") as json_file:
        json.dump(
            questions_and_answers, json_file, ensure_ascii=False, indent=4
        )


if __name__ == "__main__":
    main()
