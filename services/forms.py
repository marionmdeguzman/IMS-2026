from django import forms
from .models import Service, StaffMember, Resource


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'duration_minutes', 'price', 'category', 'is_active', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g. Personal Training'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Brief description of this service...'}),
            'duration_minutes': forms.NumberInput(attrs={'min': 15, 'step': 15}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'category': forms.TextInput(attrs={'placeholder': 'e.g. Fitness, Wellness'}),
            'color': forms.TextInput(attrs={'type': 'color'}),
        }


class StaffMemberForm(forms.ModelForm):
    class Meta:
        model = StaffMember
        fields = ['specialization', 'bio', 'services', 'is_available']
        widgets = {
            'specialization': forms.TextInput(attrs={'placeholder': 'e.g. Personal Trainer, Yoga Instructor'}),
            'bio': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Staff bio...'}),
            'services': forms.CheckboxSelectMultiple,
        }


class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['name', 'resource_type', 'capacity', 'is_available']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g. Boxing Ring A'}),
            'resource_type': forms.TextInput(attrs={'placeholder': 'e.g. Room, Equipment'}),
            'capacity': forms.NumberInput(attrs={'min': 1}),
        }
