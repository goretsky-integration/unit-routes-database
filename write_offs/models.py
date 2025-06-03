from uuid import uuid4

from django.db import models

from units.models import Unit


class Ingredient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=True)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class IngredientWriteOff(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=True)
    ingredient = models.ForeignKey(
        to=Ingredient,
        on_delete=models.CASCADE,
        related_name='write_offs',
    )
    unit = models.ForeignKey(
        to=Unit,
        on_delete=models.CASCADE,
        related_name='ingredient_write_offs',
    )
    to_write_off_at = models.DateTimeField()
    written_off_at = models.DateTimeField(null=True, blank=True)
    is_notification_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(
        self,
        force_insert = False,
        force_update = False,
        using = None,
        update_fields = None,
    ):
        self.to_write_off_at = self.to_write_off_at.replace(
            second=0,
            microsecond=0,
        )
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )
