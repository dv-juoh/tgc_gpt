from django.db import models

class Input(models.Model):
    promt = models.CharField(max_length=255)
    context = models.CharField(max_length=255)