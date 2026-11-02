import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from lessons.feedback import encouragement
from lessons.models import Assignment, Piece, Student


@pytest.fixture
def assignment(db):
    user = get_user_model().objects.create_user("s", password="x")
    student = Student.objects.create(user=user)
    piece = Piece.objects.create(student=student, title="C Major Scale")
    return Assignment.objects.create(
        piece=piece, title="Legato", technique="legato", target_count=3
    )


def test_check_off_increments_count(assignment):
    assignment.check_off()
    assert assignment.completed_count == 1
    assert not assignment.is_done


def test_assignment_done_at_target(assignment):
    for _ in range(3):
        assignment.check_off()
    assert assignment.is_done


def test_cannot_exceed_target(assignment):
    for _ in range(3):
        assignment.check_off()
    with pytest.raises(ValidationError):
        assignment.check_off()
    assert assignment.completed_count == 3


def test_encouragement_final_message():
    assert "done" in encouragement(5, 5).lower()
    assert encouragement(2, 5)
