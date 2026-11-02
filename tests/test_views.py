from datetime import timedelta

import re

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from lessons.models import Assignment, Lesson, Piece, Student


def make_student(username):
    user = get_user_model().objects.create_user(username, password="pw")
    return user, Student.objects.create(user=user)


@pytest.fixture
def setup(db):
    user, student = make_student("alice")
    Lesson.objects.create(
        student=student, scheduled_at=timezone.now() + timedelta(days=2)
    )
    piece = Piece.objects.create(student=student, title="C Major Scale")
    assignment = Assignment.objects.create(
        piece=piece, title="Legato", technique="legato", target_count=3
    )
    return user, student, assignment


def test_dashboard_requires_login(client, db):
    res = client.get(reverse("dashboard"))
    assert res.status_code == 302
    assert "/accounts/login/" in res.url


def test_dashboard_shows_lesson_and_circles(client, setup):
    user, _, _ = setup
    client.force_login(user)
    res = client.get(reverse("dashboard"))
    html = res.content.decode()
    assert res.status_code == 200
    assert "Next lesson" in html
    assert "C Major Scale" in html
    assert len(re.findall(r'<button[^>]*class="circle[ "]', html)) == 3


def test_check_endpoint_increments_and_returns_message(client, setup):
    user, _, assignment = setup
    client.force_login(user)
    res = client.post(reverse("check_assignment", args=[assignment.pk]))
    assert res.status_code == 200
    data = res.json()
    assert data["completed"] == 1 and data["target"] == 3 and not data["is_done"]
    assert data["message"]


def test_check_endpoint_rejects_over_target(client, setup):
    user, _, assignment = setup
    client.force_login(user)
    url = reverse("check_assignment", args=[assignment.pk])
    for _ in range(3):
        assert client.post(url).status_code == 200
    assert client.post(url).status_code == 409
    assert assignment.completed_count == 3


def test_check_endpoint_post_only(client, setup):
    user, _, assignment = setup
    client.force_login(user)
    assert (
        client.get(reverse("check_assignment", args=[assignment.pk])).status_code == 405
    )


def test_cannot_check_another_students_assignment(client, setup):
    _, _, assignment = setup
    other, _ = make_student("bob")
    client.force_login(other)
    res = client.post(reverse("check_assignment", args=[assignment.pk]))
    assert res.status_code == 404
    assert assignment.completed_count == 0
