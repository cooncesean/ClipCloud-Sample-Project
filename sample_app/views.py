import urllib

from django.conf import settings
from django.contrib import auth
from django.contrib.auth import backends, models, decorators
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic.simple import direct_to_template

from sample_project.sample_app.helpers import OauthWrapper
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
        return HttpResponseRedirect(reverse('sample_project.sample_app.views.profile'))
        
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
        return HttpResponseRedirect(reverse('sample_project.sample_app.views.profile'))
    
    # If this is NOT a post, simple render the signup form and allow the user to sign up 
    vars['form'] = SignUpForm()
    return direct_to_template(request, 'signup.html', vars)
    
def logout(request):
    " Log the current user out and redirect to the frontdoor. "
    auth.logout(request)
    return HttpResponseRedirect(reverse('sample_project.sample_app.views.signup'))
    
@decorators.login_required
def profile(request):
    """
    The profile view should render a template for the currently logged in profile:
      1. If the user is not yet 'approved' - it has a link to allow the user to link this 
         account to their ClipCloud account.
      2. If the user is approved, this view shows them:
          - Their 5 most recent Copy objects that were sent to ClipCloud.
          - A form to allow them to post data to their ClipCloud account.
    """
    vars = {}
            
    # If the user is approved, use their API data to fetch the 5 most recent copy objects
    if request.user.get_profile().is_approved:
        vars['recent_copies'] = profile.get_recent_copies()
        vars['form'] = PostForm()
        vars['profile'] = request.user.get_profile()
    
    vars['verification_form'] = VerifierForm()
    return direct_to_template(request, 'profile.html', vars)

@decorators.login_required
def link_account(request):
    """
    This view allows the current user to link their account in this sample_project to ClipCloud.
      > If no GET: 
          - The request is made to ClipCloud (w/ the proper Consumer keys) to get a 
            RequestToken for the user.
      > If GET:
          - The callback points back to this view.
          - Once a RequesToken is granted from ClipCloud, we update the local user with the
            RequestToken key/secret.
    """    
    # If nothing is in the GET, the user is trying request access to link their account
    # Lets make a call to get a RequestToken from ClipCloud
    CLIPCLOUD_REQUEST_TOKEN_URL = "%s%s?oauth_consumer_key=%s&oauth_signature=%s" % (settings.OAUTH_SERVER, 'api/oauth/request_token/', settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
    if not request.GET:
        return HttpResponseRedirect("%s&%s" % (CLIPCLOUD_REQUEST_TOKEN_URL, urllib.urlencode({'callback_url':settings.LOCAL_CALLBACK_URL})))
    
    # Get the request token out of the GET and add them to the local Profile object
    if 'oauth_token' in request.GET and 'oauth_token_secret' in request.GET:
        profile = request.user.get_profile()
        profile.key = request.GET['oauth_token']
        profile.secret = request.GET['oauth_token_secret']
        profile.save()
    
        # Now that we have a valid RequestToken, make another request to get an AccessToken for the user
        CLIPCLOUD_AUTHORIZATION_URL = "%s%s" % (settings.OAUTH_SERVER, 'api/oauth/authorize/')
        auth_url = "%s?oauth_token=%s" % (CLIPCLOUD_AUTHORIZATION_URL, profile.key)
        return HttpResponseRedirect(auth_url)
        
    return HttpResponse('We could not link your account properly.')
    
@decorators.login_required
def set_verifier(request):
    " Process a request from the user to set their verifier key (set and stored on ClipCloud). "
    vars = {}
    
    # Process a form submission
    if request.POST:
        
        # Bind and validate the form
        form = VerifierForm(data=request.POST)
        if not form.is_valid():
            vars['verification_form'] = form
            return direct_to_template(request, 'profile.html', vars)
        
        # If we have a valide verification code, bind it to the User and redirect
        verifier = form.cleaned_data['verifier']
        profile = request.user.get_profile()
        profile.verifier = verifier
        profile.is_approved = True
        profile.save()
    
    return HttpResponseRedirect(reverse('sample_project.sample_app.views.profile'))
    
@decorators.login_required
def post_data_to_clipcloud(request):
    " View to post some data to clip cloud. "
    # Ignore non posts
    if not request.POST:
        return HttpResponseRedirect(reverse('sample_project.sample_app.views.profile'))
    
    # Bind the post data to the form and validate
    form = PostForm(data=request.POST)
    if not form.is_valid():
        vars = {}
        vars['profile'] = request.user.get_profile()
        vars['form'] = form
        vars['recent_copies'] = request.user.get_profile().get_recent_copies()
        return direct_to_template(request, 'profile.html', vars)
    
    # Send the copy data to ClipCloud
    oauth_wrapper = OauthWrapper(profile=request.user.get_profile())
    oauth_wrapper.send_copy_to_clipcloud(copy_body=form.cleaned_data['body'])
    
    # Redirect back to the profile page
    return HttpResponseRedirect(reverse('sample_project.sample_app.views.profile'))
    
    