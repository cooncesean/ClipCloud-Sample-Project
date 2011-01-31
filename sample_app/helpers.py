import httplib
from oauth.oauth import OAuthRequest, OAuthSignatureMethod_HMAC_SHA1, OAuthConsumer
from django.conf import settings

class OauthWrapper(object):
    " A thin wrapper used to faciliate Oauth Requests/Responses. "
    SERVER = settings.OAUTH_SERVER.split('http://')[1]
    
    def __init__(self, profile):
        self.profile = profile
        self.connection = httplib.HTTPConnection(self.SERVER, settings.OAUTH_PORT)
        self.consumer = OAuthConsumer(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
        self.access_token = self._build_access_token()
        self.POST_DATA_URL = "%spost-data/" % (settings.OAUTH_SERVER)
        
    def _fetch_response(self, oauth_request):
        " Util method to fetch responses. "
        url = oauth_request.to_url()
        import pdb
        pdb.set_trace()

        self.connection.request(oauth_request.http_method, url)
        response = self.connection.getresponse()
        s = response.read()
        return s
        
    def _build_access_token(self):
        class Token(object):
            """
            This seems hackey.... what am i missing here?
              > OAuthRequest.from_token_and_callback() takes an access_token,
                however only seems to use the token's key when constructing the
                request.... why not just pass the key?
            """
            def __init__(self, key, secret):
                self.key = key
                self.secret = secret
                self.callback = settings.BASE_URL
        return Token(self.profile.key, self.profile.secret)
                
    def _build_oauth_params(self, url):
        " Helper func to build a valid oauth signature to make requests on behalf of the user. "
        parameters = {
            'oauth_consumer_key': settings.CONSUMER_KEY,
            'oauth_token': self.profile.key,
            'oauth_signature_method': 'HMAC-SHA1',
        }
                
        oauth_request = OAuthRequest.from_token_and_callback(
            self.access_token, 
            http_url=url, 
            parameters=parameters
        )
        signature_method = OAuthSignatureMethod_HMAC_SHA1()
        signature = signature_method.build_signature(oauth_request, self.consumer, self.access_token)
        parameters['oauth_signature'] = signature
        return parameters
                
    def _build_oauth_request(self, url, parameters=None):
        " Returns a OAuthRequest object "
        oauth_request = OAuthRequest.from_consumer_and_token(
            self.consumer, token=self.access_token, http_url=url, parameters=parameters,
        )
        oauth_request.sign_request(OAuthSignatureMethod_HMAC_SHA1(), self.consumer, self.access_token)
        print 'oauth_request', oauth_request
        return oauth_request
        
    def send_copy_to_clipcloud(self, copy_body=None):
        " Sends 'Copy' data to ClipCloud. "
        # Assert that the profile in question has the appropriate keys.
        if not self.profile.is_approved:
            raise Exception('This profile must approve this application before we can send data on their behalf.')
        
        # Assert that we are sending valid data
        if not copy_body or copy_body == '':
            raise Exception('You cannot send empty data to ClipCloud.')
        
        # oauth_params = self._build_oauth_params()
        oauth_request = self._build_oauth_request(self.POST_DATA_URL, {'data':copy_body})
        return self._fetch_response(oauth_request)
        
    def fetch_recent_copies(self, number_returned=10):
        " Fetches the most recent for the given profile. "
        pass