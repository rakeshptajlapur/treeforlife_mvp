from django import forms
from .models import VisitRequest
import re  

class VisitRequestForm(forms.ModelForm):
    """Form to handle visit requests for plantations"""
    
    plantation_name = forms.CharField(widget=forms.HiddenInput(), required=False)
    plantation_url = forms.URLField(widget=forms.HiddenInput(), required=False)  # ✅ RESTORED
    owner_name = forms.CharField(widget=forms.HiddenInput(), required=False)
    owner_email = forms.EmailField(widget=forms.HiddenInput(), required=False)

    phone_number = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your phone number', 'class': 'form-control'}),
    )

    check_in_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        required=True,
    )

    check_out_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        required=True,
    )

    visitors = forms.IntegerField(
        min_value=1,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
    )

    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any special request?'}),
        required=False,
    )

    class Meta:
        model = VisitRequest
        fields = ['phone_number', 'check_in_date', 'check_out_date', 'visitors', 'message']

    def clean_phone_number(self):
        """Validate phone number format"""
        phone = self.cleaned_data.get('phone_number')
        if not re.match(r'^\+?\d{10,15}$', phone):
            raise forms.ValidationError("Enter a valid phone number (10-15 digits).")
        return phone

    def clean(self):
        """Ensure check-in date is before check-out date"""
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in_date')
        check_out = cleaned_data.get('check_out_date')

        if check_in and check_out and check_in >= check_out:
            raise forms.ValidationError("Check-out date must be after check-in date.")

        return cleaned_data
