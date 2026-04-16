from django import forms
from .models import Member, MemberMembership, MembershipPlan, Tag
import pandas as pd
import io


class MemberForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Member
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'date_of_birth', 'photo', 'tags', 'notes',
            'status', 'emergency_contact_name', 'emergency_contact_phone',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'member@email.com'}),
            'phone': forms.TextInput(attrs={'placeholder': '+639XXXXXXXXX'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Internal notes about this member...'}),
            'emergency_contact_name': forms.TextInput(attrs={'placeholder': 'Emergency contact name'}),
            'emergency_contact_phone': forms.TextInput(attrs={'placeholder': '+639XXXXXXXXX'}),
        }


class MemberMembershipForm(forms.ModelForm):
    class Meta:
        model = MemberMembership
        fields = ['plan', 'start_date', 'status']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['plan'].queryset = MembershipPlan.objects.filter(is_active=True)

    def save(self, commit=True):
        membership = super().save(commit=False)
        from datetime import timedelta
        membership.end_date = membership.start_date + timedelta(days=membership.plan.duration_days)
        if commit:
            membership.save()
        return membership


class CSVImportForm(forms.Form):
    csv_file = forms.FileField(
        label='CSV File',
        help_text='Upload a CSV with columns: first_name, last_name, email, phone (optional: date_of_birth, notes)',
    )

    def clean_csv_file(self):
        f = self.cleaned_data['csv_file']
        if not f.name.endswith('.csv'):
            raise forms.ValidationError('Only CSV files are accepted.')
        try:
            content = f.read().decode('utf-8-sig')
            df = pd.read_csv(io.StringIO(content))
            required_cols = {'first_name', 'last_name', 'email'}
            missing = required_cols - set(df.columns.str.strip().str.lower())
            if missing:
                raise forms.ValidationError(f'Missing required columns: {", ".join(missing)}')
            return df
        except Exception as e:
            raise forms.ValidationError(f'Could not parse CSV: {e}')
