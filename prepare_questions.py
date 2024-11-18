import chardet


def open_qestions(filename: str) -> str:
    with open(f"{filename}", "rb") as raw:
        encode_type = chardet.detect(raw.read(1000))["encoding"]

    with open(f"{filename}", encoding=encode_type) as file:
        text = file.read()
    return text


def create_questions_answers(filename: str) -> dict:
    questions = []
    answers = []
    text = open_qestions(filename)
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
