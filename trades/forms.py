from django import forms
from .models import Achievement, Trade, Event
import csv
import io

class TradeForm(forms.ModelForm):
    class Meta:
        model = Trade
        fields = [
            'open_date', 'close_date', 'asset', 'trade_type', 'entry_price', 'exit_price',
            'position_size', 'stop_loss', 'take_profit', 'commission', 'swap', 'profit',
            'tags', 'screenshot', 'notes', 'emotion'
        ]
        widgets = {
            'open_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            ),
            'close_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            ),
            'asset': forms.Select(attrs={'class': 'form-select'}),
            'trade_type': forms.Select(attrs={'class': 'form-select'}),
            'entry_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.00001'}),
            'exit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.00001'}),
            'position_size': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stop_loss': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.00001'}),
            'take_profit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.00001'}),
            'commission': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'swap': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'profit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., news trade, breakout, scalping'}),
            'screenshot': forms.FileInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'emotion': forms.Select(attrs={'class': 'form-select'}),
        }

class TradeFilterForm(forms.Form):
    asset = forms.CharField(max_length=20, required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Asset'}))
    trade_type = forms.ChoiceField(choices=[('', 'All')] + Trade.TRADE_TYPES, required=False,
        widget=forms.Select(attrs={'class': 'form-select'}))
    date_from = forms.DateField(required=False, widget=forms.DateInput(
        attrs={'type': 'date', 'class': 'form-control'}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(
        attrs={'type': 'date', 'class': 'form-control'}))
    tags = forms.CharField(max_length=200, required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Tags'}))

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv',
            'id': 'csvFile'
        }),
        help_text='Upload a CSV file with trading data'
    )
    
    def clean_csv_file(self):
        csv_file = self.cleaned_data['csv_file']
        
        if not csv_file.name.endswith('.csv'):
            raise forms.ValidationError('File must be a CSV file.')
        
        if csv_file.size > 5 * 1024 * 1024:  # 5MB limit
            raise forms.ValidationError('File size must be under 5MB.')
        
        return csv_file

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'event_type', 'event_date', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Event title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Event description'}),
            'event_type': forms.Select(attrs={'class': 'form-select'}),
            'event_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class AchievementForm(forms.ModelForm):
    class Meta:
        model = Achievement
        fields = ['title', 'description', 'achievement_type', 'achieved_date', 'image', 'is_featured']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Achievement title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Achievement description'}),
            'achievement_type': forms.Select(attrs={'class': 'form-select'}),
            'achieved_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }