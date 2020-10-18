from django import forms
from django.forms.widgets import Input

from .models import Expenses, Groups, FinalTransaction, Friends


class ExpensesForm(forms.ModelForm):

    class Meta:
        model = Expenses
        fields = ['amount', 'exp_note', 'bill']
        widgets = {
            'amount': Input(attrs={'class': 'form-control', 'required': 'required', 'type': 'number'}),
            'exp_note': Input(attrs={'class': 'form-control', 'required': 'required'}),
            'bill': Input(attrs={'class': 'form-control', 'type': 'file', 'required': 'required'}),

        }

