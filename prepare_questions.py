import json
from pathlib import Path

import chardet

from settings import settings


def open_questions(filename: str) -> str:
    """
    Opens a file and reads it as text, detecting the encoding type of the file.

    Args:
        filename (str): The name of the file to open.

    Returns:
        str: The text from the file.
    """
    with open(f"{filename}", "rb") as raw:
        encode_type: str = chardet.detect(raw.read(1000))["encoding"]

    with open(f"{filename}", encoding=encode_type) as file:
        text: str = file.read()
    return text


def create_questions_answers(files: list[str]) -> dict[str, str]:
    """
    Extracts questions and answers from a list of text files and returns them as a dictionary.

    This function reads each file in the provided list, detects its encoding, and extracts
    paragraphs of text. It identifies and separates questions and answers based on specific
    keywords ("Вопрос" and "Ответ") at the beginning of each paragraph. The function then
    pairs each question with its corresponding answer in a dictionary.

    Args:
        files (list[str]): A list of filenames containing questions and answers.

    Returns:
        dict[str, str]: A dictionary where each key is a question (str) and its value is the corresponding answer (str).
    """
    questions: list[str] = []
    answers: list[str] = []
    for filename in files:
        text: str = open_questions(filename)
        text_splitted: list[str] = [
            paragraph.strip()
            for paragraph in text.split("\n\n")
            if paragraph.strip()
        ]
        for line in text_splitted:
            if line.startswith("Вопрос"):
                questions.append(line)
            if line.startswith("Ответ"):
                answers.append(line)
    questions_and_answers: dict[str, str] = {
        question: answer for question, answer in zip(questions, answers)
    }
    return questions_and_answers


def main() -> None:
    """
    Main function for preparing questions and answers for the quiz bot.

    This function reads all files in the directory specified by the
    RAW_QUESTIONS_PATH setting, extracts questions and answers from them,
    and writes the data to a JSON file named "questions.json".

    The JSON file is formatted as a dictionary with questions as keys and
    their corresponding answers as values.

    It assumes that the questions and answers are separated by
    empty lines and that the questions start with the keyword "Вопрос"
    and the answers start with the keyword "Ответ".

    The function does not perform any error checking, so it will crash if
    the files are not in the correct format.

    Args:
        None

    Returns:
        None
    """
    directory_path: Path = Path(settings.raw_questions_path)
    files: list[Path] = [
        file for file in directory_path.iterdir() if file.is_file()
    ]
    questions_and_answers: dict[str, str] = create_questions_answers(files)
    with open("questions.json", "w", encoding="utf-8") as json_file:
        json.dump(
            questions_and_answers, json_file, ensure_ascii=False, indent=4
        )


if __name__ == "__main__":
    main()
