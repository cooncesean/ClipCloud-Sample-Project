from django.db import models
from django.contrib.auth.models import User

KEY_SIZE = 18
SECRET_SIZE = 32

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
    is_approved = models.BooleanField(default=False)
    
    def __unicode__(self):
        return u"%s: %s" % (self.user.username, self.is_approved and 'approved' or 'un-approved')
        