from __future__ import annotations

import dataclasses
import json
from typing import IO


class QuestionError(Exception):
    pass


@dataclasses.dataclass(slots=True, frozen=True)
class Question:
    question: str
    question_test: str
    single_type: bool
    answers: list[str]


def load_questions(file: IO) -> list[Question]:
    try:
        data = json.load(file)
    except json.JSONDecodeError as err:
        raise QuestionError(f"Could not decode file: {err}")

    # TODO json schema validation

    try:
        return [
            Question(
                question["question"],
                question["question_test"],
                question["single_type"],
                question["answers"]
            )
            for question in data
        ]
    except Exception as err:
        raise QuestionError(f"Could not parse questions: {err}")
