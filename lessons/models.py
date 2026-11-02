from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.utils import timezone


class Student(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
    )

    def __str__(self):
        return self.user.get_username()

    def next_lesson(self):
        return self.lessons.filter(scheduled_at__gte=timezone.now()).first()


class Lesson(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="lessons"
    )
    scheduled_at = models.DateTimeField()
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["scheduled_at"]

    def __str__(self):
        return f"{self.student} - {self.scheduled_at:%Y-%m-%d %H:%M}"


class Piece(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="pieces"
    )
    title = models.CharField(max_length=200)
    composer = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.title


class Assignment(models.Model):
    class Technique(models.TextChoices):
        NONE = "", "—"
        LEGATO = "legato", "Legato"
        STACCATO = "staccato", "Staccato"
        DOTTED = "dotted", "Dotted rhythm"
        HANDS_SEPARATE = "hands_separate", "Hands separate"
        SLOW = "slow", "Slow practice"

    piece = models.ForeignKey(
        Piece, on_delete=models.CASCADE, related_name="assignments"
    )
    title = models.CharField(max_length=200, help_text="e.g. 'Left hand, mm. 1-8'")
    technique = models.CharField(max_length=20, choices=Technique.choices, blank=True)
    target_count = models.PositiveSmallIntegerField(
        default=5, validators=[MinValueValidator(1)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.piece} - {self.title}"

    @property
    def completed_count(self):
        return self.completions.count()

    @property
    def is_done(self):
        return self.completed_count >= self.target_count

    def check_off(self):
        """Record one practice repetition. Cannot exceed target_count."""
        with transaction.atomic():
            locked = Assignment.objects.select_for_update().get(pk=self.pk)
            if locked.is_done:
                raise ValidationError("This assignment is already complete.")
            return Completion.objects.create(assignment=self)


class Completion(models.Model):
    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name="completions"
    )
    completed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["completed_at"]
