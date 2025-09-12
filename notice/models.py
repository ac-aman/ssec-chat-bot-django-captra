# notice/models.py
from django.db import models

DEPARTMENTS = [
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


class Notice(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    department = models.CharField(max_length=50, choices=DEPARTMENTS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} ({self.department})"
