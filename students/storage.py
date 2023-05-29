from functools import lru_cache

from .schema import Student, Mark

StudentStorageType = dict[int, Student]
MarkStorageType = dict[int, list[Mark]]

STUDENTS: StudentStorageType = {}
MARKS: MarkStorageType = {}


@lru_cache(maxsize=1)
def get_students_storage() -> StudentStorageType:
    return STUDENTS


@lru_cache(maxsize=1)
def get_marks_storage() -> MarkStorageType:
    return MARKS
