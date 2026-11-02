from django.contrib import admin

from .models import Assignment, Completion, Lesson, Piece, Student


class AssignmentInline(admin.TabularInline):
    model = Assignment
    extra = 1


@admin.register(Piece)
class PieceAdmin(admin.ModelAdmin):
    list_display = ("title", "composer", "student")
    inlines = [AssignmentInline]


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("piece", "title", "technique", "target_count", "completed_count")


admin.site.register(Student)
admin.site.register(Lesson)
admin.site.register(Completion)
