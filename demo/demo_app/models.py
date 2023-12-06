from django.db import models
from djongo import models

# Create your models here.

class CivilResearch(models.Model):
    name = models.CharField(max_length=255)
    title_dept = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    office_location = models.URLField()
    office_hours = models.JSONField()
    research_interests = models.JSONField()

    class Meta:
        db_table = 'civilResearch'