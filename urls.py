"""
Note:
  > This sample app is only used to verify that the oauth handlers in ClipCloud work
    as expected. It also shows the expected workflow/interface for developers who want
    access to the ClipCloud API
  > Thus, we have a very bare bones url/view structure.
     - We only allow a user to sign up.
     - We don't necessarily need to provide login/logout hooks.    
"""
from django.conf.urls.defaults import *

urlpatterns = patterns('',

    # Local Auth
    (r'^logout/$', 'sample_project.sample_app.views.local_auth.logout'),
    (r'^login/$', 'sample_project.sample_app.views.local_auth.login'),
    (r'^signup/$', 'sample_project.sample_app.views.local_auth.signup'),
    
    # API Calls to ClipCloud
    (r'^get-request-token/$', 'sample_project.sample_app.views.clipcloud.get_and_authorize_request_token'),
    (r'^set-verifier/$', 'sample_project.sample_app.views.clipcloud.set_verifier'),
    (r'^get-access-token/$', 'sample_project.sample_app.views.clipcloud.get_access_token'),
    (r'^post-copy-data/$', 'sample_project.sample_app.views.clipcloud.post_copy_data'),
    
    (r'^post-data/$', 'sample_project.sample_app.views.clipcloud.post_copy_data'),
    (r'^$', 'sample_project.sample_app.views.clipcloud.profile'),
)
