from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
#from django.core.urlresolvers import reverse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from hab_app.models import *
from datetime import *
from django.apps import apps
from hab_app.forms import *


def metadata_processor(request):
    hostels = AllHostelMetaData.objects.all()
    permission = 0
    permission2 = 0
    gensec = 0
    gh = 0
    if 'hostel_view' in request.session:
        if request.session['hostel_view'] == "a1x":
            permission = 1
        else:
            permission = 0
    if 'username' in request.session:
        if request.session['username'] == "chr_hab":
            permission2 = 1
        else:
            permission2 = 0
    if 'username' in request.session:
        if AllHostelMetaData.objects.filter(hostelGensec=request.session['username']).exists():
            gensec = 1
    if 'username' in request.session:
        if request.session['username'] == "gensec_hostel":
            gh = 1
    dict_11 = {'hostels': hostels, 'permission': permission, 'permission2': permission2, 'gensec': gensec, 'gh': gh}
    return {'hostels': hostels, 'permission': permission, 'permission2': permission2, 'gensec': gensec, 'gh': gh}
