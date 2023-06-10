from django import forms
from .models import Taxi


class TaxiForm(forms.ModelForm):
    class Meta:
        model = Taxi
        fields = ['id']


class OrderForm(forms.Form):
    pickup_location = forms.CharField(max_length=100)
    dropoff_location = forms.CharField(max_length=100)
    taxi = forms.IntegerField()