#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""TestGen.py: This program does things."""

__author__ = "Benjamin Foreman (bennyforeman1@gmail.com)"


# TODO test generation
# TODO tests to pdfs


import itertools as it
import json
import random
from dataclasses import dataclass, field
from enum import Enum, auto

# from dataclasses_serialization.json import JSONSerializer


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
            return QuestionType.BOOLEAN

        if "multiple" in label:
            return QuestionType.MULTIPLE_CHOICE

        if "select" in label:
            return QuestionType.SELECT_ALL

        if "short" in label:
            return QuestionType.SHORT_ANSWER

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
    boolean: bool = None
    answers: list[Answer] = field(default_factory=list)
    correct_response: str = None  # could be EEIs as a list of strings
    difficulty: Difficulty = Difficulty.MEDIUM
    is_required: bool = False

    @staticmethod
    def deserialize_question(question):
        kwargs = {
            "prompt": question["prompt"],
            "question_type": QuestionType.from_str(question["question_type"]),
            "is_required": question["is_required"],
        }

        if "boolean" in question:
            kwargs["boolean"] = question["boolean"]

        if "answers" in question:
            kwargs["answers"] = [Answer.deserialize_answer(answer) for answer in question["answers"]]

        if "difficulty" in question:
            kwargs["difficulty"] = Difficulty.from_str(question["difficulty"])

        if "is_required" in question:
            kwargs["is_required"] = question["is_required"]

        return Question(**kwargs)

    def shuffle_answers(self):
        random.shuffle(self.answers)


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


# def testbank_to_file(testbank: TestBank, filename: str = None):
#     filename = f"{filename}.json" if filename is not None else f"{testbank.title}.json"

#     with open(filename, "w") as wf:
#         json.dump(JSONSerializer.serialize(testbank), wf, indent=4)


def testbank_from_file(filepath: str) -> TestBank:
    with open(filepath, "r") as rf:
        data = json.load(rf)

    return TestBank.deserialize_testbank(data)

@dataclass
class Test:
    test_id: int
    questions: list[Question]

    def __post_init__(self):
        self.answer_key = None  # TODO

def generate_n_tests(testbank: TestBank, n: int, ratio: tuple[int, int, int]):
    required, nonrequired = it.groupby(testbank.questions, key=lambda question: question.is_required)
    easy, medium, hard = it.groupby(nonrequired, key=lambda question: question.difficulty)

    multiple = 1
    while len(easy) < (multiple + 1) * ratio[0] and len(medium) < (multiple + 1) * ratio[1] and len(hard) < (multiple + 1) * ratio[2]:
        multiple += 1

    tests = list()

    for i in range(1, n + 1):
        questions = required + random.sample(easy, ratio[0] * multiple) + random.sample(medium, ratio[1] * multiple) + random.sample(hard, ratio[2] * multiple)
        
        for question in questions:
            question.shuffle_answers()

        random.shuffle(questions)

        tests.append(Test(i, questions))

    return tests


def tests_to_doc(tests: list[Test], filename: str = None):
    pass



if __name__ == "__main__":
    test = testbank_from_file("example_test.json")

    print(test.title)
