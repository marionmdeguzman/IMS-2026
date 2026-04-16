from django import forms
from .models import Appointment, Waitlist
from members.models import Member
from services.models import Service, StaffMember, Resource


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['member', 'service', 'staff', 'resource', 'date', 'start_time', 'end_time', 'notes', 'status']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Optional notes...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['member'].queryset = Member.objects.filter(status='active').order_by('last_name', 'first_name')
        self.fields['service'].queryset = Service.objects.filter(is_active=True)
        self.fields['staff'].queryset = StaffMember.objects.filter(is_available=True).select_related('user')
        self.fields['staff'].required = False
        self.fields['resource'].required = False
        self.fields['notes'].required = False


class PublicBookingForm(forms.Form):
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'First name'}))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Last name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'your@email.com'}))
    phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'placeholder': '+639XXXXXXXXX'}))
    service = forms.ModelChoiceField(queryset=Service.objects.filter(is_active=True), empty_label='— Select service —')
    staff = forms.ModelChoiceField(
        queryset=StaffMember.objects.filter(is_available=True).select_related('user'),
        required=False,
        empty_label='— No preference —',
    )
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    start_time = forms.TimeField(widget=forms.HiddenInput())
    end_time = forms.TimeField(widget=forms.HiddenInput())
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Any special requests?'}))


class AppointmentStatusForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['status', 'cancellation_reason']
        widgets = {
            'cancellation_reason': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Reason for cancellation (if applicable)...'}),
        }


class WaitlistForm(forms.ModelForm):
    class Meta:
        model = Waitlist
        fields = ['member', 'service', 'preferred_date', 'preferred_staff', 'notes']
        widgets = {
            'preferred_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }
