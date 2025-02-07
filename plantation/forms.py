from django import forms
from .models import VisitRequest

class VisitRequestForm(forms.ModelForm):
    """Form to handle visit requests for plantations"""
    
    plantation_name = forms.CharField(widget=forms.HiddenInput(), required=False)
    plantation_url = forms.URLField(widget=forms.HiddenInput(), required=False)
    owner_name = forms.CharField(widget=forms.HiddenInput(), required=False)
    owner_email = forms.EmailField(widget=forms.HiddenInput(), required=False)
    
    phone_number = forms.CharField(max_length=15, required=True)
    check_in_date = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    check_out_date = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    visitors = forms.IntegerField(min_value=1, required=True)
    message = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = VisitRequest
        fields = ['phone_number', 'check_in_date', 'check_out_date', 'visitors', 'message']

    def __init__(self, *args, **kwargs):
        """Initialize form with prefilled values"""
        plantation = kwargs.pop('plantation', None)
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if plantation and user:
            self.fields['plantation_name'].initial = plantation.name
            self.fields['plantation_url'].initial = f"https://treeforlife.net/plantation-details/{plantation.id}/"
            self.fields['owner_name'].initial = user.username
            self.fields['owner_email'].initial = user.email
