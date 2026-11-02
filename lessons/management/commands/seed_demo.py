from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from lessons.models import Assignment, Lesson, Piece, Student


class Command(BaseCommand):
    help = "Create a demo student with a lesson and a few assignments."

    def handle(self, *args, **options):
        User = get_user_model()
        user, _ = User.objects.get_or_create(username="demo_student")
        user.set_password("demo1234")
        user.save()
        student, _ = Student.objects.get_or_create(user=user)

        Lesson.objects.get_or_create(
            student=student,
            scheduled_at=(timezone.now() + timedelta(days=3)).replace(
                minute=0, second=0, microsecond=0
            ),
        )

        scale, _ = Piece.objects.get_or_create(student=student, title="C Major Scale")
        for technique, title in [
            ("legato", "Legato"),
            ("staccato", "Staccato"),
            ("dotted", "Dotted rhythm"),
        ]:
            Assignment.objects.get_or_create(
                piece=scale,
                title=title,
                technique=technique,
                defaults={"target_count": 5},
            )

        self.stdout.write(self.style.SUCCESS("Seeded demo_student / demo1234"))
