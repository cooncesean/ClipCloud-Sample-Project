from django.contrib import auth
from django.contrib.auth import backends, models
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic.simple import direct_to_template

from sample_project.sample_app.forms import SignUpForm, LoginForm, VerifierForm, PostForm
from sample_project.sample_app.models import Profile

def login(request):
    " Process a login request. "
    vars = {}
    
    # If there is post data - process the form
    if request.POST:
        
        form = LoginForm(data=request.POST)
        if not form.is_valid():
            vars['form'] = form
            return direct_to_template(request, 'login.html', vars)
            
        username = form.cleaned_data['email']
        password = form.cleaned_data['password']
        
        # Try to auth the user
        user = auth.authenticate(username=username, password=password)
        if user is None:
            vars['form'] = form
            vars['error'] = 'Invalid Email and/or Password'
            return direct_to_template(request, 'auth/login.html', vars)
        
        # Log the user in to this session
        auth.login(request, user)
        return HttpResponseRedirect(reverse('sample_project.sample_app.views.clipcloud.profile'))
        
    vars['form'] = LoginForm()
    return direct_to_template(request, 'login.html', vars)
    
def signup(request):
    " Process a request for a user to create an account. "
    vars = {}
    
    # If a post, process a signup
    if request.POST:
                
        # Bind and validate the form
        form = SignUpForm(request.POST)
        if not form.is_valid():
            vars['form'] = form
            return direct_to_template(request, 'signup.html', vars)
        
        # Create a new user 
        user = models.User.objects.create_user(
            username=form.cleaned_data['email'], 
            email=form.cleaned_data['email'], 
            password=form.cleaned_data['password']
        )
        # Create a new profile bound to this user
        profile = Profile.objects.create(user=user)
        
        # Attempt to authenticate the user and log them in
        user.backend = "%s.%s" % (backends.ModelBackend.__module__, backends.ModelBackend.__name__)
        auth.login(request, user)
        
        # Redirect user to the profile page
        return HttpResponseRedirect(reverse('sample_project.sample_app.views.clipcloud.profile'))
    
    # If this is NOT a post, simple render the signup form and allow the user to sign up 
    vars['form'] = SignUpForm()
    return direct_to_template(request, 'signup.html', vars)
    
def logout(request):
    " Log the current user out and redirect to the frontdoor. "
    auth.logout(request)
    return HttpResponseRedirect(reverse('sample_project.sample_app.views.signup'))