import oauth.oauth as oauth

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic.simple import direct_to_template

from sample_project.sample_app.client import sample_client, CALLBACK_URL, \
    consumer, signature_method_plaintext, signature_method_hmac_sha1, POST_COPY_DATA_URL
from sample_project.sample_app.forms import VerifierForm, PostForm
from sample_project.sample_app.models import Profile

@login_required
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
    profile = request.user.get_profile()
    
    # If the user is approved, use their API data to fetch the 5 most recent copy objects
    if profile.is_approved:
        vars['recent_copies'] = profile.get_recent_copies()
        vars['form'] = PostForm()
        vars['profile'] = profile
    
    vars['verification_form'] = VerifierForm()
    return direct_to_template(request, 'profile.html', vars)
    
@login_required
def get_and_authorize_request_token(request):
    """
    Fetch a RequestToken from ClipCloud.
      > The 'consumer' object is imported from sample_app.client and is used to sign the request.
      > Ping ClipCloud and ask for a RequestToken.
      > Once received, save it to the current user and redirect the user to ClipCloud to authorize
        this sample_app.
    """
    profile = request.user.get_profile()
    
    # Get a request token from ClipCloud
    oauth_request = oauth.OAuthRequest.from_consumer_and_token(
        consumer, 
        callback=CALLBACK_URL, 
        http_url=sample_client.request_token_url
    )
    oauth_request.sign_request(signature_method_plaintext, consumer, None)
    print 'parameters: %s' % str(oauth_request.parameters)
    token = sample_client.fetch_request_token(oauth_request)
    
    # Update the profile's token data
    profile.key = token.key
    profile.secret = token.secret
    profile.save()
    
    # Cool, we got a RequestToken for the current user.
    # Now redirect them to the Authorization page on ClipCloud to authorize this Token.
    oauth_request = oauth.OAuthRequest.from_token_and_callback(token=token, http_url=sample_client.authorization_url)
    return HttpResponseRedirect(oauth_request.to_url())
    
@login_required
def set_verifier(request):
    " Process a request from the user to set their verifier key (set and stored on ClipCloud). "
    vars = {}
    profile = request.user.get_profile()
    
    # Process a form submission
    if request.POST:
        
        # Bind and validate the form
        form = VerifierForm(data=request.POST)
        if not form.is_valid():
            vars['verification_form'] = form
            return direct_to_template(request, 'profile.html', vars)
        
        # If we have a valide verification code, bind it to the User and redirect
        profile.verifier = form.cleaned_data['verifier']
        profile.is_approved = True
        profile.save()
    
    # Redirect to the 'get_access_token' view, which exchanges the RequesToken for an AccessToken
    return HttpResponseRedirect(reverse('sample_project.sample_app.views.clipcloud.get_access_token'))
    
@login_required
def get_access_token(request):
    " Exchange the user's RequestToken for an AccessToken. "
    profile = request.user.get_profile()
    
    # Use the user's current token data to exchange their RequestToken for an AccessToken
    request_token = oauth.OAuthToken(profile.key, profile.secret)
    oauth_request = oauth.OAuthRequest.from_consumer_and_token(
        consumer, 
        token=request_token, 
        verifier=profile.verifier, 
        http_url=sample_client.access_token_url
    )
    
    # Sign and make the request to get an AccessToken for this user
    oauth_request.sign_request(signature_method_plaintext, consumer, request_token)
    token = sample_client.fetch_access_token(oauth_request)
    return HttpResponseRedirect(reverse('sample_project.sample_app.views.clipcloud.profile'))
    
@login_required
def post_copy_data(request):
    " Process 'copy' form and send 'copy' data data to clip cloud. "
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
    profile = request.user.get_profile()
    access_token = oauth.OAuthToken(profile.key, profile.secret)
    oauth_request = oauth.OAuthRequest.from_consumer_and_token(
        consumer, 
        token=access_token, 
        http_method='POST', 
        http_url=POST_COPY_DATA_URL, 
        parameters={
            'copy_body': form.cleaned_data['body']
        }
    )
    # TODO -> this needs to be sha4 signature
    oauth_request.sign_request(signature_method_plaintext, consumer, access_token)
    response = sample_client.access_resource(oauth_request)
    
    # TODO -> show the user that their copy data got sent and stored correctly
    
    # Redirect back to the profile page
    return HttpResponseRedirect(reverse('sample_project.sample_app.views.clipcloud.profile'))
    