from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Order, PAYMENT_METHOD_CHOICES


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class CheckoutForm(forms.ModelForm):
    payment_method = forms.ChoiceField(choices=PAYMENT_METHOD_CHOICES, widget=forms.RadioSelect)

    class Meta:
        model = Order
        fields = ['full_name', 'email', 'phone', 'address', 'city', 'payment_method']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
