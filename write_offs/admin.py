from django.contrib import admin

from write_offs.models import IngredientWriteOff, Ingredient


@admin.register(IngredientWriteOff)
class IngredientWriteOffAdmin(admin.ModelAdmin):
    list_display = ("unit", "ingredient", 'to_write_off_at')
    list_select_related = ("unit", "ingredient")
    ordering = ["-created_at"]


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name",)
