import sys

from abc import ABC
from typing import Dict, List, Optional, Tuple, TypedDict, TypeVar

T = TypeVar("T")


class DbObject(ABC):
    def __init__(self, **kwargs: object):
        assert type(self) is not DbObject, "Do not instantiate a DbObject directly"

        for name, value in kwargs.items():
            setattr(self, name, value)

    def __getitem__(self, name: str) -> T:
        assert hasattr(self, name), f"Attribute {name} does not exist"
        return getattr(self, name)

    def __setitem__(self, name: str, value: object):
        assert hasattr(self, name), f"Attribute {name} does not exist"
        setattr(self, name, value)


class Student(DbObject):
    def __init__(self, student_id: str, student_name: str, tutor_group: str):
        super().__init__(
            student_id=student_id, student_name=student_name, tutor_group=tutor_group
        )


class StudentDict(TypedDict):
    student_id: str
    student_name: str
    tutor_group: str


class StudentScore(DbObject):
    def __init__(self, student_id: str, test_id: str, score_obtained: int):
        super().__init__(
            student_id=student_id, test_id=test_id, score_obtained=score_obtained
        )


class StudentScoreDict(TypedDict):
    student_id: str
    test_id: str
    score_obtained: int


class Subject(DbObject):
    # TODO: add subject codes/ids
    def __init__(self, subject_name: str, teacher_name: str):
        super().__init__(subject_name=subject_name, teacher_name=teacher_name)


class SubjectDict(TypedDict):
    subject_name: str
    teacher_name: str


class Test(DbObject):
    def __init__(self, test_id: str, subject_name: str, test_date: str, max_score: int):
        super().__init__(
            test_id=test_id,
            subject_name=subject_name,
            test_date=test_date,
            max_score=max_score,
        )


class TestDict(TypedDict):
    test_id: str
    subject_name: str
    test_date: str
    max_score: int


def mk_student(student_id: str, student_name: str, tutor_group: str) -> StudentDict:
    return {
        "student_id": student_id,
        "student_name": student_name,
        "tutor_group": tutor_group,
    }


def mk_student_score(
    student_id: str, test_id: str, score_obtained: int
) -> StudentScoreDict:
    return {
        "student_id": student_id,
        "test_id": test_id,
        "score_obtained": score_obtained,
    }


def mk_subject(subject_name: str, teacher_name: str):
    return {
        "subject_name": subject_name,
        "teacher_name": teacher_name,
    }


def mk_test(test_id: str, subject_name: str, test_date: str, max_score: int):
    return {
        "test_id": test_id,
        "subject_name": subject_name,
        "test_date": test_date,
        "max_score": max_score,
    }


students = [
    Student("S101", "Alex Chen", "12A"),
    Student("S102", "Sam Taylor", "12B"),
    Student("S103", "Maya Patel", "12A"),
]

student_scores = [
    StudentScore("S101", "T01", 42),
    StudentScore("S101", "T02", 85),
    StudentScore("S101", "T03", 54),
    StudentScore("S102", "T01", 38),
    StudentScore("S102", "T02", 72),
    StudentScore("S103", "T03", 58),
    StudentScore("S103", "T04", 31),
]

subjects = [
    Subject("Computer Science", "Mr. Smith"),
    Subject("Mathematics", "Mrs. Jones"),
    Subject("Physics", "Dr. Vance"),
]

tests = [
    Test("T01", "Computer Science", "15/10/2025", 50),
    Test("T02", "Mathematics", "20/10/2025", 100),
    Test("T03", "Computer Science", "05/11/2025", 60),
    Test("T04", "Physics", "12/11/2025", 40),
]

TestResult = Tuple[str, int, int, str]

StudentTranscript = Tuple[
    Optional[str],
    Optional[str],
    List[TestResult],
]


def get_student_transcript(student_id: str) -> StudentTranscript:
    name: Optional[str] = None
    tutor_group: Optional[str] = None

    for student in students:
        if student["student_id"] == student_id:
            name = student["student_name"]
            tutor_group = student["tutor_group"]
            break

    student_tests: List[TestResult] = []

    for student_score in student_scores:
        if student_score["student_id"] != student_id:
            continue

        test_id = student_score["test_id"]

        for test in tests:
            if test["test_id"] == test_id:
                break

        else:
            print(
                f"test_id {test_id} does not exist in the tests table", file=sys.stderr
            )
            continue

        score_obtained = student_score["score_obtained"]
        max_score = test["max_score"]

        student_tests.append(
            (
                test["subject_name"],
                score_obtained,
                max_score,
                f"{round(score_obtained / max_score * 100, 1)}%",
            )
        )

    return name, tutor_group, student_tests


def get_test_average(test_id: str) -> Optional[float]:
    num_taken = 0
    total_score_obtained = 0

    for test in tests:
        if test["test_id"] == test_id:
            max_score = test["max_score"]
            break
    else:
        print("Test was not found in the test table", file=sys.stderr)
        return

    for student_score in student_scores:
        if student_score["test_id"] == test_id:
            num_taken += 1
            total_score_obtained += student_score["score_obtained"]

    # No dividing by 0
    if num_taken == 0:
        print("No students took this test", file=sys.stderr)
        return

    return round(total_score_obtained / num_taken / max_score * 100, 1)


def get_student_id_from_name(student_name: str) -> Optional[str]:
    for student in students:
        if student["student_name"] == student_name:
            return student["student_id"]


# FIXME: There is currently no subject id, so it is the name of the subject
def get_top_performer(subject_id):
    subject_test_max_scores: Dict[str, int] = {}

    for test in tests:
        if test["subject_name"] == subject_id:
            subject_test_max_scores[test["test_id"]] = test["max_score"]

    if len(subject_test_max_scores) == 0:
        print("There are no tests for {subject_id} currently", file=sys.stderr)
        return

    student_totals = {}

    # Currently if there are multiple students with the same total score,
    # the first student seen will be the top performer
    candidate: Optional[str] = None

    for student_score in student_scores:
        if (
            test_max_score := subject_test_max_scores.get(student_score["test_id"])
        ) is None:
            continue

        student_id = student_score["student_id"]
        score_obtained = student_score["score_obtained"]

        if student_id in student_totals:
            current = student_totals[student_id]
            new_total = (current[0] + score_obtained, current[1] + 1)
        else:
            new_total = (score_obtained, 1)

        student_totals[student_id] = new_total

        if candidate is None:
            candidate = student_id
            continue

        if candidate == student_id:
            continue

        if new_total[0] > student_totals[candidate][0]:
            candidate = student_id

    return candidate


def get_students_below_threshold(pass_percentage):
    student_test_ratios = {}

    # Since we expect to see results for all tests, might as well
    # just iterate over all of the tests now instead of doing it lazily
    test_max_scores = {}

    for test in tests:
        test_max_scores[test["test_id"]] = test["max_score"]

    for student_score in student_scores:
        student_id = student_score["student_id"]
        score = student_score["score_obtained"]
        test_ratio = score / test_max_scores[student_score["test_id"]]

        if student_id in student_test_ratios:
            student_test_ratios[student_id].append(test_ratio)
        else:
            student_test_ratios[student_id] = [test_ratio]

    students_below_threshold = []

    for student_id, test_ratios in student_test_ratios.items():
        # Only multiply by 100 once for efficiency
        avg_percentage = (sum(test_ratios) / len(test_ratios)) * 100

        if avg_percentage < pass_percentage:
            students_below_threshold.append(student_id)

    return students_below_threshold


transcript = get_student_transcript(get_student_id_from_name("Alex Chen"))

print(f"Student transcript for Alex Chen: {transcript}")

print(f"Test average for T01: {get_test_average('T01')}")

print(f"Top performer for Mathematics: {get_top_performer('Mathematics')}")

print(f"Students below 80% threshold: {get_students_below_threshold(80)}")
