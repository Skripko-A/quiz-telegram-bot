import json
from pathlib import Path

import chardet

from settings import settings


def build_question_answer_pairs(files: list[str]) -> dict[str, str]:
    """
    Creates a dictionary of questions and answers from a list of files.

    The function reads each file, splits its content into paragraphs, and
    then checks if each paragraph starts with "Вопрос" or "Ответ". If it
    does, the function adds the paragraph to the list of questions or
    answers, respectively. After all files have been processed, the function
    creates a dictionary where each key is a question and its value is the
    corresponding answer.

    Args:
        files: A list of paths to the files to be processed.

    Returns:
        A dictionary of questions and answers.
    """
    questions: list[str] = []
    answers: list[str] = []
    for filename in files:
        with open(f"{filename}", encoding="KOI8-R") as file:
            text: str = file.read()
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
    questions_and_answers: dict[str, str] = build_question_answer_pairs(files)
    with open("questions.json", "w", encoding="utf-8") as json_file:
        json.dump(
            questions_and_answers, json_file, ensure_ascii=False, indent=4
        )


if __name__ == "__main__":
    main()
