#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""TestGen.py: This program does things."""

__author__ = "Benjamin Foreman (bennyforeman1@gmail.com)"


# TODO serialize enums
# TODO test generation
# TODO tests to pdfs


import json
from dataclasses import dataclass, field
from enum import Enum, auto

from dataclasses_serialization.json import JSONSerializer


class Difficulty(Enum):
    EASY = auto()
    MEDIUM = auto()
    HARD = auto()

    @staticmethod
    def from_str(label: str):  # TODO could maybe be better
        label = label.replace(" ", "").lower()

        if label == "easy":
            return Difficulty.EASY

        if label == "medium":
            return Difficulty.MEDIUM

        if label == "hard":
            return Difficulty.HARD

        raise NotImplementedError


class QuestionType(Enum):
    BOOLEAN = auto()
    MULTIPLE_CHOICE = auto()
    SELECT_ALL = auto()
    SHORT_ANSWER = auto()

    @staticmethod
    def from_str(label: str):  # TODO could maybe be better
        label = label.replace(" ", "").lower()

        if "bool" in label:
            return Difficulty.BOOLEAN

        if label == "multiplechoice":
            return Difficulty.MULTIPLE_CHOICE

        if label == "selectall":
            return Difficulty.SELECT_ALL

        if label == "shortanswer":
            return Difficulty.SHORT_ANSWER

        raise NotImplementedError


@dataclass
class Answer:
    text: str
    is_correct: bool = False

    @staticmethod
    def deserialize_answer(answer):
        return Answer(text=answer["text"], is_correct=answer["is_correct"])


@dataclass
class Question:
    prompt: str
    question_type: QuestionType
    answers: list[Answer] = field(default_factory=list)
    difficulty: Difficulty = Difficulty.MEDIUM
    is_required: bool = False

    @staticmethod
    def deserialize_question(question):
        return Question(
            prompt=question["prompt"],
            question_type=QuestionType.from_str(question["question_type"]),
            answers=[Answer.deserialize_answer(answer) for answer in question["answers"]],
            difficulty=Difficulty(question["difficulty"]),
            is_required=question["is_required"],
        )


@dataclass
class TestBank:
    title: str
    questions: list[Question] = field(default_factory=list)

    @staticmethod
    def deserialize_testbank(testbank):
        return TestBank(
            title=testbank["title"],
            questions=[Question.deserialize_question(question) for question in testbank["questions"]],
        )


def testbank_to_file(testbank: TestBank, filename: str = None):
    filename = f"{filename}.json" if filename is not None else f"{testbank.title}.json"

    with open(filename, "w") as wf:
        json.dump(JSONSerializer.serialize(testbank), wf, indent=4)


def testbank_from_file(filepath: str) -> TestBank:
    with open(filepath, "r") as rf:
        data = json.load(rf)

    return TestBank.deserialize_testbank(data)


if __name__ == "__main__":
    pass