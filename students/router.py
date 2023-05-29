from fastapi import APIRouter, HTTPException, Query

from .storage import get_students_storage, get_marks_storage
from .schema import StudentCreateSchema, StudentUpdateSchema, Student, Mark

router = APIRouter()


STUDENTS_STORAGE = get_students_storage()
MARKS_STORAGE = get_marks_storage()


@router.get("/")
async def get_students() -> list[Student]:
    return list(get_students_storage().values())


@router.get("/{student_id}")
async def get_student(student_id: int) -> Student:
    try:
        return STUDENTS_STORAGE[student_id]
    except KeyError:
        raise HTTPException(
            status_code=404, detail=f"Student with ID={student_id} does not exist."
        )


@router.patch("/{student_id}")
async def update_student(
    student_id: int, updated_student: StudentUpdateSchema
) -> Student:
    existing_student = None
    try:
        existing_student = STUDENTS_STORAGE[student_id]
    except KeyError:
        raise HTTPException(
            status_code=404, detail=f"Student with ID={student_id} does not exist."
        )
    if not updated_student.first_name and not updated_student.last_name:
        raise HTTPException(
            status_code=422, detail="Must contain at least one non-empty field."
        )
    if updated_student.first_name:
        existing_student.first_name = updated_student.first_name

    if updated_student.last_name:
        existing_student.last_name = updated_student.last_name

    return existing_student


@router.delete("/{student_id}")
async def delete_student(student_id: int) -> None:
    try:
        del STUDENTS_STORAGE[student_id]
        del MARKS_STORAGE[student_id]
    except KeyError:
        raise HTTPException(
            status_code=404, detail=f"Student with ID={student_id} does not exist."
        )


@router.post("/")
async def create_student(student: StudentCreateSchema) -> Student:
    id = len(STUDENTS_STORAGE) + 1
    new_student = Student(**student.dict(), id=id)
    STUDENTS_STORAGE[id] = new_student
    MARKS_STORAGE[id] = []
    return new_student


@router.post("/{student_id}/marks/{mark:float}")
async def add_student_mark(student_id: int, mark: Mark) -> None:
    if student_id not in STUDENTS_STORAGE:
        raise HTTPException(
            status_code=404, detail=f"Student with ID={student_id} does not exist."
        )
    MARKS_STORAGE[student_id].append(mark)
    return mark


@router.get("/{student_id}/marks")
async def get_student_marks(student_id: int) -> list[str]:
    if student_id not in STUDENTS_STORAGE:
        raise HTTPException(
            status_code=404, detail=f"Student with ID={student_id} does not exist."
        )
    return [m.name for m in MARKS_STORAGE[student_id]]
