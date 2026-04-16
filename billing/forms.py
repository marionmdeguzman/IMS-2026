from django import forms
from .models import Payment
from members.models import Member, MembershipPlan, MemberMembership
from bookings.models import Appointment


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['member', 'appointment', 'membership', 'amount', 'method', 'reference_number', 'description', 'status']
        widgets = {
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'placeholder': '0.00'}),
            'reference_number': forms.TextInput(attrs={'placeholder': 'GCash ref, card last 4, etc.'}),
            'description': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Payment description...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['member'].queryset = Member.objects.filter(status='active').order_by('last_name', 'first_name')
        self.fields['appointment'].queryset = Appointment.objects.select_related('member', 'service').order_by('-date')
        self.fields['appointment'].required = False
        self.fields['membership'].required = False
        self.fields['membership'].queryset = MemberMembership.objects.select_related('member', 'plan').order_by('-created_at')


class MembershipPlanForm(forms.ModelForm):
    class Meta:
        model = MembershipPlan
        fields = ['name', 'duration_days', 'price', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g. Monthly, Annual'}),
            'duration_days': forms.NumberInput(attrs={'min': 1}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'description': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Plan description...'}),
        }
