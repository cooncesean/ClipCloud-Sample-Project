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
    (r'^signup/$', 'sample_project.sample_app.views.signup'),
    (r'^link-account/$', 'sample_project.sample_app.views.link_account'),
    (r'^post-data/$', 'sample_project.sample_app.views.post_data_to_clipcloud'),
    (r'^$', 'sample_project.sample_app.views.profile'),
)
