from django import forms

from units.models import Unit


class UnitWithIdForm(forms.ModelForm):
    id = forms.IntegerField()

    class Meta:
        model = Unit
        fields = '__all__'
