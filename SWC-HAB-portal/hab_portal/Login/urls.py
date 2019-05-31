from django.conf.urls import url
from Login import views


app_name='Login'

urlpatterns = [
    # The home view ('/Login/')
    url(r'^$', views.home, name='home'),
    # Explicit home ('/Login/home/')
    url(r'^home/$', views.home, name='home'),
    # Redirect to get token ('/Login/gettoken/')
    url(r'^gettoken/$', views.gettoken, name='gettoken'),

]

