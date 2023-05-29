from fastapi.testclient import TestClient

import pytest

from main import app
from students.schema import StudentCreateSchema, Student, Mark

client = TestClient(app)


@pytest.fixture(autouse=True)
def delete_all_students():
    for student in client.get("/students").json():
        client.delete(f"/students/{student['id']}")


def test_get_students():
    response = client.get("/students")
    assert response.status_code == 200
    assert response.json() == []


def test_create_student():
    new_student = StudentCreateSchema(first_name="John", last_name="Wick")
    response = client.post("/students", json=new_student.dict())
    assert response.status_code == 200

    raw_response = response.json()
    assert "id" in raw_response
    created_student = Student(**raw_response)
    assert created_student.first_name == new_student.first_name
    assert created_student.last_name == new_student.last_name


def test_create_student_incorrect():
    response = client.post("/students", json={"garbage": "Yes, please."})
    assert response.status_code == 422


def test_create_multiple_students():
    students = [{"first_name": f"Maciuś {i}", "last_name": "Król"} for i in range(1, 4)]
    for student in students:
        response = client.post("/students", json=student)
        assert response.status_code == 200

    response = client.get("/students")
    assert response.status_code == 200
    assert len(response.json()) == len(students)


def test_update_student():
    student = StudentCreateSchema(first_name="John", last_name="Wick")
    response = client.post("/students", json=student.dict()).json()

    student.last_name = "Wymoczek"
    new_response = client.patch(
        f"/students/{response['id']}", json=student.dict()
    ).json()

    assert response["first_name"] == new_response["first_name"]
    assert response["last_name"] != new_response["last_name"]
    assert response["id"] == new_response["id"]


def test_delete_nonexistend_student():
    response = client.delete("/students/44")
    assert response.status_code == 404


def test_mark_nonexistend_student():
    response = client.post("/students/44/marks/3.5")
    assert response.status_code == 404


def test_mark_incorrectly():
    new_student = StudentCreateSchema(first_name="John", last_name="Wick")
    student = client.post("/students", json=new_student.dict()).json()
    response = client.post(f"/students/{student['id']}/marks/3.4")
    assert response.status_code == 422

    response = client.post(f"/students/{student['id']}/marks/6.0")
    assert response.status_code == 422


def test_mark_correctly():
    marks = [Mark.BARDZO_DOBRY, Mark.DOBRY, Mark.NIEDOSTATECZNY]
    new_student = StudentCreateSchema(first_name="John", last_name="Wick")
    student = client.post("/students", json=new_student.dict()).json()

    for mark in marks:
        client.post(f"/students/{student['id']}/marks/{mark}")

    response = client.get(f"/students/{student['id']}/marks")
    assert response.status_code == 200
    assert [m.name for m in marks] == response.json()
