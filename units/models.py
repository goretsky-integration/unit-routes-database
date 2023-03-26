from django.db import models


class Region(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name


class Unit(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=64, unique=True)
    uuid = models.UUIDField(unique=True)
    office_manager_account_name = models.CharField(max_length=64)
    dodo_is_api_account_name = models.CharField(max_length=64)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
