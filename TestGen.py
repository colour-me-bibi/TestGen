#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""TestGen.py: This program does things."""

__author__ = "Benjamin Foreman (bennyforeman1@gmail.com)"


import json
import random
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto
from string import ascii_uppercase

from docx import Document  # pip install python-docx


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
        }

        if "boolean" in question:
            kwargs["boolean"] = question["boolean"]

        if "answers" in question:
            kwargs["answers"] = [Answer.deserialize_answer(answer) for answer in question["answers"]]

        if "correct_response" in question:
            kwargs["correct_response"] = question["correct_response"]

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


def testbank_from_file(filepath: str) -> TestBank:
    with open(filepath, "r") as rf:
        data = json.load(rf)

    return TestBank.deserialize_testbank(data)


@dataclass
class Test:
    test_id: int
    questions: list[Question]
    answer_key: list[str] = field(default_factory=list)

    def __post_init__(self):
        for question in self.questions:
            if question.question_type == QuestionType.BOOLEAN:
                self.answer_key.append(str(question.boolean))
            elif question.question_type == QuestionType.MULTIPLE_CHOICE:
                self.answer_key.append(
                    " or ".join(ascii_uppercase[i] for i, answer in enumerate(question.answers) if answer.is_correct)
                )
            elif question.question_type == QuestionType.SELECT_ALL:
                self.answer_key.append(
                    " and ".join(ascii_uppercase[i] for i, answer in enumerate(question.answers) if answer.is_correct)
                )
            elif question.question_type == QuestionType.SHORT_ANSWER:
                self.answer_key.append(question.correct_response)
            else:
                raise NotImplementedError


def generate_n_tests(testbank: TestBank, n: int, ratio: tuple[int, int, int]):
    grouped_is_required = defaultdict(list)
    for question in testbank.questions:
        grouped_is_required[question.is_required].append(question)

    required, nonrequired = grouped_is_required[True], grouped_is_required[False]

    grouped_difficulty = defaultdict(list)
    for question in nonrequired:
        grouped_difficulty[question.difficulty].append(question)

    easy, medium, hard = grouped_difficulty[Difficulty.EASY], grouped_difficulty[Difficulty.MEDIUM], grouped_difficulty[Difficulty.HARD]

    multiple = 1
    while (
        len(easy) >= (multiple + 1) * ratio[0]
        and len(medium) >= (multiple + 1) * ratio[1]
        and len(hard) >= (multiple + 1) * ratio[2]
    ):
        multiple += 1

    tests = list()
    for i in range(1, n + 1):
        questions = (
            required
            + random.sample(easy, ratio[0] * multiple)
            + random.sample(medium, ratio[1] * multiple)
            + random.sample(hard, ratio[2] * multiple)
        )

        for question in questions:
            question.shuffle_answers()

        random.shuffle(questions)

        tests.append(Test(i, questions))

    return tests


def tests_to_doc(tests: list[Test], title: str):
    document = Document()

    for test_idx, test in enumerate(tests, 1):
        document.add_heading(f"{title} (ID: {test_idx})", 0)

        for question_idx, question in enumerate(test.questions, 1):
            document.add_heading(f"{question_idx} - {question.prompt}", level=1)

            if question.question_type == QuestionType.BOOLEAN:
                document.add_paragraph("\tTrue or False")
            elif question.question_type in (QuestionType.MULTIPLE_CHOICE, QuestionType.SELECT_ALL):
                for answer_idx, answer in enumerate(question.answers):
                    document.add_paragraph(f"\t{ascii_uppercase[answer_idx]} - {answer.text}")
            elif question.question_type == QuestionType.SHORT_ANSWER:
                for _ in range(2):
                    document.add_paragraph()
            else:
                raise NotImplementedError

        document.add_page_break()

    for test_idx, test in enumerate(tests, 1):
        document.add_heading(f"{title} (ID: {test_idx})", 0)

        for answer_idx, answer in enumerate(test.answer_key):
            document.add_paragraph(f"{answer_idx} - {answer}")

        document.add_paragraph()
        document.add_page_break()

    document.save(f"{title}-{len(tests)}.docx")


if __name__ == "__main__":
    testbank = testbank_from_file("example_test.json")

    tests = generate_n_tests(testbank, 5, (1, 1, 1))

    tests_to_doc(tests, testbank.title)
