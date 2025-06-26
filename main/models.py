from django.db import models

# Create your models here.
class Job(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    posted_date = models.DateTimeField(auto_now_add=True)
    apply_link = models.URLField(max_length=200, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    category = models.CharField(max_length=100, null=True, blank=True)
    