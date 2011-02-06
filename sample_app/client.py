"""
Extended from Leah Culver's oauth example:
  > git+git://github.com/leah/python-oauth.git
"""
import httplib
import oauth.oauth as oauth

from django.conf import settings

# Settings for the local test consumer
SERVER = 'localhost'
PORT = 8000

# API Urls for ClipCloud
REQUEST_TOKEN_URL = '%sapi/oauth/request_token/' % settings.OAUTH_SERVER
ACCESS_TOKEN_URL = '%sapi/oauth/access_token/' % settings.OAUTH_SERVER
AUTHORIZATION_URL = '%sapi/oauth/authorize/' % settings.OAUTH_SERVER
POST_COPY_DATA_URL = '%scopy/post/' % settings.OAUTH_SERVER
GET_USER_COPY_DATA_URL = '%scopy/recent/' % settings.OAUTH_SERVER
CALLBACK_URL = '%sapi/oauth/request_token_ready/' % settings.OAUTH_SERVER # ???

# Set up global consumer and sig methods
consumer = oauth.OAuthConsumer(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
signature_method_plaintext = oauth.OAuthSignatureMethod_PLAINTEXT()
signature_method_hmac_sha1 = oauth.OAuthSignatureMethod_HMAC_SHA1()

class SampleOAuthClient(oauth.OAuthClient):
    " Sample client using httplib with headers. "
    def __init__(self, server, port=httplib.HTTP_PORT, request_token_url='', access_token_url='', authorization_url=''):
        self.server = server
        self.port = port
        self.request_token_url = request_token_url
        self.access_token_url = access_token_url
        self.authorization_url = authorization_url
        self.connection = httplib.HTTPConnection("%s:%d" % (self.server, self.port))
        
    def _normalize_url(self, url):
        " Hackey util method to munge the url if working locally. "
        if 'http://localhost:8000/' in url:
            return url.replace('http://localhost:8000', '')
        return url
        
    def fetch_request_token(self, oauth_request):
        """
        Send a request to ClipCloud to get a new RequestToken.
          > Send the request via GET params.
          > Should expect a valid RequestToken from the Service Provider.
          > Returns an OAuthToken
        """
        url = self._normalize_url(oauth_request.to_url())
        self.connection.request(oauth_request.http_method, url)
        response = self.connection.getresponse()
        return oauth.OAuthToken.from_string(response.read())
        
    def fetch_access_token(self, oauth_request):
        url = self._normalize_url(oauth_request.to_url())
        self.connection.request(oauth_request.http_method, url)
        response = self.connection.getresponse()
        return oauth.OAuthToken.from_string(response.read())
                
    def access_resource(self, oauth_request):
        headers = {'Content-Type' :'application/x-www-form-urlencoded'}
        url = self._normalize_url(oauth_request.to_url())
        self.connection.request(
            oauth_request.http_method, 
            url, 
            body=oauth_request.to_postdata(), 
            headers=headers
        )
        response = self.connection.getresponse()
        return response.read()
        
# Singleton which will be imported and used in your views
sample_client = SampleOAuthClient(SERVER, PORT, REQUEST_TOKEN_URL, ACCESS_TOKEN_URL, AUTHORIZATION_URL)