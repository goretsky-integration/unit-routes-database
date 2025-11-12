import uuid

from django.db import models


class InventoryStocks(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
