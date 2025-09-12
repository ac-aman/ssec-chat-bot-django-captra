# notice/models.py
from django.db import models


class College(models.Model):
    name = models.CharField(max_length=200)
    principal_name = models.CharField(max_length=150, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)  # NEW field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Department(models.Model):
    DEPT_CHOICES = [
        ("IT", "Information Technology"),
        ("EE", "Electrical Engineering"),
        ("CE", "Civil Engineering"),
        ("AM", "Applied Mechanics"),
        ("ME", "Mechanical Engineering"),
        ("HS", "Humanities and Science (General)"),
        ("ECE", "Electronics and Communication Engineering"),
        ("PE", "Production Engineering"),
        ("ICE", "Instrumentation and Control Engineering"),
    ]

    college = models.ForeignKey(
        College, on_delete=models.CASCADE, related_name="departments"
    )
    name = models.CharField(max_length=50, choices=DEPT_CHOICES)
    hod_name = models.CharField(max_length=150, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    num_seats = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)  # NEW field

    def __str__(self):
        return f"{self.get_name_display()} - {self.college.name}"
