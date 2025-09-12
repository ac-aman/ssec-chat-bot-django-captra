from django.db import models


class Faculty(models.Model):
    name = models.CharField(max_length=150)
    designation = models.CharField(
        max_length=100, blank=True, null=True
    )  # Prof., HoD, etc.
    department = models.CharField(max_length=100, blank=True, null=True)
    room_no = models.CharField(max_length=50, blank=True, null=True)
    expertise = models.TextField(blank=True, null=True)
    years_of_experience = models.IntegerField(blank=True, null=True)
    qualifications = models.TextField(blank=True, null=True)
    contact_email = models.EmailField(max_length=150, blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    extra_curriculum = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)  # NEW COLUMN for help/notes

    def __str__(self):
        return self.name
