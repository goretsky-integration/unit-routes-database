from django.db import models


class ReportType(models.Model):
    name = models.CharField(max_length=64, unique=True, db_index=True)
    verbose_name = models.CharField(max_length=64)
    parent = models.ForeignKey(
        to='ReportType',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.verbose_name
