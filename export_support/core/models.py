from django.db import models


class FormTypeCounter(models.Model):

    form_type = models.CharField(max_length=5)
    load_or_sub = models.CharField(max_length=4)

    def __str__(self):
        return f"{self.form_type} - {self.load_or_sub}"
