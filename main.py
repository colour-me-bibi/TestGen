
# tests as json
# tests need to be serializable
# generate tests to pdf


import json
from dataclasses import dataclass, field

from dataclasses_serialization.json import JSONSerializer


@dataclass
class Answer:
    text: str
    is_correct: bool = False

    @staticmethod
    def deserialize_answer(cls, answer):
        return Answer(text=answer["text"], is_correct=answer["is_correct"])


@dataclass
class Question:
    prompt: str
    answers: list[Answer] = field(default_factory=list)
    difficulty: int = 0
    is_required: bool = False

    @staticmethod
    def deserialize_question(question):
        return Question(
            prompt=question["prompt"],
            answers=[Answer.deserialize_answer(answer) for answer in question["answers"]],
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

def testbank_to_file(testbank: TestBank, filepath: str = None):
    # if filepath is None:
    #     if not os.path.exists('testbanks'):
    #         os.mkdir('testbanks')
    #     filepath = os.path.join('testbanks', f"{testbank.title}.json")

    with open(filepath, "w") as wf:
        json.dump(JSONSerializer.serialize(testbank), wf, indent=4)


def testbank_from_file(filepath: str) -> TestBank:
    with open(filepath, "r") as rf:
        data = json.load(rf)

    return TestBank.deserialize_testbank(data)
