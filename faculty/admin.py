from django.contrib import admin
from .models import Faculty


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "designation",
        "department",
        "room_no",
        "years_of_experience",
        "contact_email",
    )
    search_fields = ("name", "designation", "department", "expertise")
    list_filter = ("department", "designation", "years_of_experience")
