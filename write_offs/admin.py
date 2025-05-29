from django.contrib import admin

from write_offs.models import IngredientWriteOff, Ingredient


@admin.register(IngredientWriteOff)
class IngredientWriteOffAdmin(admin.ModelAdmin):
    pass


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    pass
