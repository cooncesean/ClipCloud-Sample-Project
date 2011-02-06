import simplejson
import oauth.oauth as oauth

from django.db import models
from django.contrib.auth.models import User

from sample_project.sample_app.client import GET_USER_COPY_DATA_URL, \
    signature_method_plaintext, signature_method_hmac_sha1, consumer, sample_client

KEY_SIZE = 18
SECRET_SIZE = 32
VERIFIER_SIZE = 4

class Profile(models.Model):
    """
    1:1 User relation -> stores extra data for each user such as their
    oauth credentials and the status of their account.
    
    @key -> oauth_access_key
    @secret -> oauth_secret_key
    @is_approved -> True/False based on whether or not the user has requested access
                    from Clip Cloud.
    """
    user = models.ForeignKey(User, related_name='tokens', unique=True)
    key = models.CharField(max_length=KEY_SIZE, blank=True, null=True)
    secret = models.CharField(max_length=SECRET_SIZE, blank=True, null=True)
    verifier = models.CharField(max_length=VERIFIER_SIZE, blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    
    def __unicode__(self):
        return u"%s: %s" % (self.user.username, self.is_approved and 'approved' or 'un-approved')
        
    def get_recent_copies(self):
        " Get a list of X most recent copies for the profile. "
        # Only run requests for auth'd users w/ linked appropriate token values
        if not self.key or not self.secret or not self.verifier or not self.is_approved:
            return []
            
        # Create the OAuthRequest
        access_token = oauth.OAuthToken(self.key, self.secret)
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(
            consumer, 
            token=access_token, 
            http_method='GET', 
            http_url=GET_USER_COPY_DATA_URL
        )
        oauth_request.sign_request(signature_method_plaintext, consumer, access_token)
        response = sample_client.access_resource(oauth_request)
        
        # Dump the json response and return the list of copy_data
        try:
            json = simplejson.loads(response)
            return json['copy_data']
        except simplejson.JSONDecodeError:
            return []
            