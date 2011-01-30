from django import forms

class SignUpForm(forms.Form):
    " This form allows a user to sign up. "
    email = forms.CharField(label='Email:')
    password = forms.CharField(widget=forms.PasswordInput(), label='Password:')
    
class PostForm(forms.Form):
    " This form allows an approved user to post data to their ClipCloud account. "
    body = forms.CharField(widget=forms.TextInput())