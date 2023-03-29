from django.db import models

from reports.models.report_types import ReportType
from units.models import Unit


class UserRole(models.Model):
    name = models.CharField(max_length=64)
    access_code = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
    )
    report_types = models.ManyToManyField(ReportType)
    units = models.ManyToManyField(Unit)

    def __str__(self):
        return self.name
