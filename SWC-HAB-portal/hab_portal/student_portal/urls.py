from django.conf.urls import url
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'student_portal'

urlpatterns = [
    path('login/', views.manual_login, name='login'),
    path('login2/', views.manual_login2, name='login2'),
    path('logout/', views.manual_logout, name='logout'),
    path('messfeedback/', login_required(views.check_filled_feedback), name='feedback'),
    path('messfeedback/new', login_required(views.NewFeedback.as_view()), name='new_feedback'),
    path('messfeedback/update', login_required(views.UpdateFeedback.as_view()), name='update_feedback'),
    path('preference/', login_required(views.check_filled_preference), name='preference'),
    path('preference/new', login_required(views.NewPreference.as_view()), name='new_preference'),
    path('preference/final', login_required(views.final_preference), name='final_preference'),
    path('updateinfo', login_required(views.updateinfo), name='updateinfo'),
    path('track', views.track, name='track'),
    path('gensecfeedback', login_required(views.gensec_feedback), name='gensec_feedback'),
]
