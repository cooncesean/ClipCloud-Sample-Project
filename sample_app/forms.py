from django import forms
from django.contrib.auth.models import User

from sample_project.sample_app.models import VERIFIER_SIZE

class LoginForm(forms.Form):
    " This form allows a user to login. "
    email = forms.CharField(label='Email:')
    password = forms.CharField(widget=forms.PasswordInput(), label='Password:')

class SignUpForm(forms.Form):
    " This form allows a user to sign up. "
    email = forms.CharField(label='Email:')
    password = forms.CharField(widget=forms.PasswordInput(), label='Password:')
    
    def clean_email(self):
        " Assert that the email is unique. "
        try:
            u = User.objects.get(email=self.cleaned_data['email'])
            raise forms.ValidationError('This username already exists in our database.')
        except User.DoesNotExist:
            pass
        return self.cleaned_data['email']
        
class VerifierForm(forms.Form):
    " Allow a user to set their verifier key (sent from ClipCloud upon AccessToken grant). "
    verifier = forms.CharField(label='Verification Code:')
        
    def clean_verifier(self):
        if len(self.cleaned_data['verifier']) > VERIFIER_SIZE:
            raise forms.ValidationError('Your verification code cannot be more than %d characters.' % VERIFIER_SIZE)
        return self.cleaned_data['verifier']
        
class PostForm(forms.Form):
    " This form allows an approved user to post data to their ClipCloud account. "
    body = forms.CharField(widget=forms.Textarea())