from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from main.models import *


class CreateUserForm(UserCreationForm):
	class Meta:
		model = User
		fields = ['username','email','password1','password2']

class UpdateUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields = ['username','email']

class UpdateProductForm(forms.ModelForm):
    class Meta:
        model=Product
        fields=['name','category','ingredients','deliverable','price','image']

class CreateProductForm(forms.ModelForm):
    class Meta:
        model=Product
        fields=['name','category','ingredients','deliverable','price','image']

class AddReviewForm(forms.ModelForm):
    class Meta:
        model=Reviews
        fields=['comment','speed_rating','service_rating','food_quality_rating','image']
 

class ContactForm(forms.Form):
    from_email = forms.EmailField(required=True)
    subject = forms.CharField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)
