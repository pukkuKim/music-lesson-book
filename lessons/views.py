from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Count, Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from .feedback import encouragement
from .models import Assignment


@login_required
def dashboard(request):
    student = getattr(request.user, "student_profile", None)
    if student is None:
        return render(request, "lessons/no_student.html")

    assignments = Assignment.objects.annotate(done=Count("completions"))
    pieces = list(
        student.pieces.prefetch_related(Prefetch("assignments", queryset=assignments))
    )
    for piece in pieces:
        piece.done = piece.target = 0
        for a in piece.assignments.all():
            a.circles = [i < a.done for i in range(a.target_count)]
            piece.done += a.done
            piece.target += a.target_count

    return render(
        request,
        "lessons/dashboard.html",
        {"next_lesson": student.next_lesson(), "pieces": pieces},
    )


@login_required
@require_POST
def check_assignment(request, pk):
    # Only the owner of the assignment can check it off.
    assignment = get_object_or_404(Assignment, pk=pk, piece__student__user=request.user)
    try:
        assignment.check_off()
    except ValidationError:
        return JsonResponse({"error": "already_complete"}, status=409)

    done = assignment.completed_count
    return JsonResponse(
        {
            "completed": done,
            "target": assignment.target_count,
            "is_done": assignment.is_done,
            "message": encouragement(done, assignment.target_count),
        }
    )
