from django.shortcuts import render
from django.contrib import auth
from django.contrib.auth import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import FormView
from django.utils.http import is_safe_url
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.apps import apps
from datetime import datetime
from dateutil.relativedelta import relativedelta
# from iitgauth.views import WebmailLoginView
from .models import *
from datetime import datetime

# from celery.task.schedules import crontab
# from celery.decorators import periodic_task

from django.contrib.auth.models import User
from .forms import *
from poplib import *
from .resources import *
from hab_app.models import *
#from django.core.urlresolvers import reverse
from django.urls import reverse
from decimal import Decimal


curr_year = datetime.now().year
curr_month = datetime.now().month
m1 = curr_month
y1 = curr_year
m1 = m1 - 1
m1_y1 = ""
if m1 < 1:
    m1 = 12
    y1 = y1 - 1
m1_y1 = str(m1) + '_' + str(y1)

y2 = curr_year
m2 = curr_month
m2 = m2 + 1
m2_y2 = ""
if m2 > 12:
    m2 = 1
    y2 = y2 + 1
m2_y2 = str(m2) + '_' + str(y2)


def manual_login(request):
    if request.method == 'POST':
        print(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        login_server = request.POST.get('login_server')
        
        print('\nlogin server = ' + str(login_server))
        
        em = '%s@iitg.ernet.in' % (username)
        
        print('\nemail = ' + str(em))
        
        mail = POP3_SSL(login_server)
        
        print('\nmail = ' + str(mail))
        
        mail.user(username)
        try:
            mail.pass_(password)
            mail.quit()
        except:
            form = LoginForm()
            return render(request, 'student_portal/login.html', {'message': 1, 'form': form})
        user, created = User.objects.get_or_create(username=username, email=em)
        
        print('user found !!\n')

        user.set_password(password)  # This line will hash the password
        user.save()  # DO NOT FORGET THIS LINE
        
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                print('authenticated !\n')
                login(request, user)
                request.session['username'] = username
                request.session['password'] = password
                request.session['server'] = login_server
                return redirect('home')
            else:
                return HttpResponse("account not active")
        else:
            return HttpResponse("Invalid Login Credentials")
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'student_portal/login.html', {'form': form})

def manual_login2(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        login_server = request.POST.get('login_server')
        em = '%s@iitg.ernet.in' % (username)
        mail = POP3_SSL(login_server)
        mail.user(username)
        try:
            mail.pass_(password)
            mail.quit()
        except:
            return HttpResponse("Invalid Webmail Credentials")
        user, created = User.objects.get_or_create(username=username, email=em)
        if created:
            user.set_password(password)  # This line will hash the password
            user.save()  # DO NOT FORGET THIS LINE
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                request.session['username'] = username
                request.session['password'] = password
                request.session['server'] = login_server
                return redirect('home')
            else:
                return HttpResponse("account not active")
        else:
            return HttpResponse("Invalid Login Credentials")
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'student_portal/temp_login.html', {'form': form})


@login_required
def manual_logout(request):
    logout(request)
    return redirect('student_portal/login')
    # end of Views for Webmail Login


def opi_history(request):
    if request.method == "GET":
        mess_list = Opi_calculated.objects.filter(month=m1, year=y1)
        month = calendar.month_name[m1]
        year = y1
        return render(request, 'student_portal/mess_opi_history.html',
                      {'mess_list': mess_list, 'month': month, 'year': year})
    if request.method == "POST" and 'btn1' in request.POST:
        mess_list = Opi_calculated.objects.filter(month=request.POST.get('month_val'), year=request.POST.get('year_val'))
        month = calendar.month_name[int(request.POST.get('month_val'))]
        year = request.POST.get('year_val')
        return render(request, 'student_portal/mess_opi_history.html',
                      {'mess_list': mess_list, 'month': month, 'year': year})


@login_required
def get_initial(request, month, year):
    initial = {'baseHostel': '', 'subscribedHostel': '', 'roomNo': '', 'student_name': '', 'student_id': ''}
    ocupant_user_id_dict = OccupantDetails.objects.filter(webmail=request.user).values_list('idNo')
    ocupant_user_name = OccupantDetails.objects.filter(webmail=request.user).values_list('name')
    # ocupant_user_id = ocupant_user_id_dict['idNo']
    if len(ocupant_user_id_dict) == 1:
        value_id = list(map(str, ocupant_user_id_dict.first()))[
            0]  # use map(str, ocupant_user_id_dict.first()) in case of python2
        value_name = list(map(str, ocupant_user_name.first()))[0]
        initial['student_id'] = value_id
        initial['student_name'] = value_name
        # print(value_id)
        occupant_hostel = []
        base_hostel_room_number = []
        if not BarakRORelation.objects.filter(occupantId=value_id).values_list('hostelName').first() is None:
            occupant_hostel.append(
                BarakRORelation.objects.filter(occupantId=value_id).values_list('hostelName').first())
            base_hostel_room_number.append(
                BarakRORelation.objects.filter(occupantId=value_id).values_list('roomNo').first())

        if not BramhaputraRORelation.objects.filter(occupantId=value_id).values_list('hostelName').first() is None:
            occupant_hostel.append(
                BramhaputraRORelation.objects.filter(occupantId=value_id).values_list('hostelName').first())
            base_hostel_room_number.append(
                BramhaputraRORelation.objects.filter(occupantId=value_id).values_list('roomNo').first())

        if not DhansiriRORelation.objects.filter(occupantId=value_id).values_list('hostelName').first() is None:
            occupant_hostel.append(
                DhansiriRORelation.objects.filter(occupantId=value_id).values_list('hostelName').first())
            base_hostel_room_number.append(
                DhansiriRORelation.objects.filter(occupantId=value_id).values_list('roomNo').first())

        if not DibangRORelation.objects.filter(occupantId=value_id).values_list('hostelName').first() is None:
            occupant_hostel.append(
                DibangRORelation.objects.filter(occupantId=value_id).values_list('hostelName').first())
            base_hostel_room_number.append(
                DibangRORelation.objects.filter(occupantId=value_id).values_list('roomNo').first())

        if not DihingRORelation.objects.filter(occupantId=value_id).values_list('hostelName').first() is None:
            occupant_hostel.append(
                DihingRORelation.objects.filter(occupantId=value_id).values_list('hostelName').first())
            base_hostel_room_number.append(
                DihingRORelation.objects.filter(occupantId=value_id).values_list('roomNo').first())

        if not KamengRORelation.objects.filter(occupantId=value_id).values_list('hostelName').first() is None:
            occupant_hostel.append(
                KamengRORelation.objects.filter(occupantId=value_id).values_list('hostelName').first())
            base_hostel_room_number.append(
                KamengRORelation.objects.filter(occupantId=value_id).values_list('roomNo').first())

        if not KapiliRORelation.objects.filter(occupantId=value_id).values_list('hostelName').first() is None:
            occupant_hostel.append(
                KapiliRORelation.objects.filter(occupantId=value_id).values_list('hostelName').first())
            base_hostel_room_number.append(
                KapiliRORelation.objects.filter(occupantId=value_id).values_list('roomNo').first())

        if not LohitRORelation.objects.filter(occupantId=value_id).values_list('hostelName').first() is None:
            occupant_hostel.append(
                LohitRORelation.objects.filter(occupantId=value_id).values_list('hostelName').first())
            base_hostel_room_number.append(
                LohitRORelation.objects.filter(occupantId=value_id).values_list('roomNo').first())

        if not ManasRORelation.objects.filter(occupantId=value_id).values_list('hostelName').first() is None:
            occupant_hostel.append(
                ManasRORelation.objects.filter(occupantId=value_id).values_list('hostelName').first())
            base_hostel_room_number.append(
                ManasRORelation.objects.filter(occupantId=value_id).values_list('roomNo').first())

        if not SiangRORelation.objects.filter(occupantId=value_id).values_list('hostelName').first() is None:
            occupant_hostel.append(
                SiangRORelation.objects.filter(occupantId=value_id).values_list('hostelName').first())
            base_hostel_room_number.append(
                SiangRORelation.objects.filter(occupantId=value_id).values_list('roomNo').first())

        if not SubansiriRORelation.objects.filter(occupantId=value_id).values_list('hostelName').first() is None:
            occupant_hostel.append(
                SubansiriRORelation.objects.filter(occupantId=value_id).values_list('hostelName').first())
            base_hostel_room_number.append(
                SubansiriRORelation.objects.filter(occupantId=value_id).values_list('roomNo').first())

        if not UmiamRORelation.objects.filter(occupantId=value_id).values_list('hostelName').first() is None:
            occupant_hostel.append(
                UmiamRORelation.objects.filter(occupantId=value_id).values_list('hostelName').first())
            base_hostel_room_number.append(
                UmiamRORelation.objects.filter(occupantId=value_id).values_list('roomNo').first())
        # print(SiangRORelation.objects.filter(occupantId=value_id).values_list('hostelName').first()[0])
        # occupant_hostel += KapiliRORelation.objects.filter(occupantId=value_id).values_list('hostelName')
        # print(SiangRORelation.objects.all())

        if len(occupant_hostel) == 1:
            occupant_hostel_name = occupant_hostel[0]
            initial['baseHostel'] = occupant_hostel[0][0]

        if len(base_hostel_room_number) == 1:
            base_hostel_room_number = base_hostel_room_number[0]
            initial['roomNo'] = base_hostel_room_number[0]

        assigned_mess = ""
        if FinalPreference.objects.filter(username=request.user, month=month, year=year):
            assigned_mess = FinalPreference.objects.filter(username=request.user, month=month, year=year)[0]
        # print(assigned_mess.hostelName)
        if assigned_mess:
            initial['subscribedHostel'] = assigned_mess.final_hostel
        else:
            initial['subscribedHostel'] = initial['baseHostel']
    # ocupant_user = OccupantDetails.objects.filter(webmail=self.request.user)

    return initial


class NewFeedback(FormView):
    template_name = "student_portal/messfeedback_form.html"
    form_class = NewFeedbackForm
    monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                  "November", "December"]

    def get(self, *args, **kwargs):
        uname = self.request.user
        print('Clicked on Mess Feedback:', uname)
        # print(MessFeedback.objects.filter(username=uname,month=m1,year=y1).count())
        # print(self.request.user)
        automation_objects = Automation.objects.filter(feed_start_date__lte=datetime.today(),
                                                       feed_off_date__gte=datetime.today(), feed_on_off=True)
        print(automation_objects)
        if len(automation_objects) == 0 or len(automation_objects) > 1:
            feedback_ON_OFF = False
            # print('Executing line 249')
            form = self.form_class()
            return render(self.request, self.template_name, {'form': form, 'feedback_ON_OFF': feedback_ON_OFF})

        automation_object = automation_objects[0]
        # automation_month_year = str(automation_object.month) + '_' + str(automation_object.year)
        if MessFeedback.objects.filter(username=uname, month=automation_object.month,
                                       year=automation_object.year).count() == 1:
            return HttpResponseRedirect('update')
        else:
            initial = get_initial(self.request, month=automation_object.month, year=automation_object.year)
            # print (initial)
            feed_initial = {'subscribedHostelName': initial['subscribedHostel'], 'month': automation_object.month,
                            'year': automation_object.year, 'roomNo': initial['roomNo'],
                            'baseHostelName': initial['baseHostel'], 'filled': True}
            print('feedback_initial:', feed_initial)
            # feed_initial = { 'baseHostel' : initial['baseHostel'], 'hostelName' : initial['subscribedHostel'] , 'month': automation_object.month, 'year' : automation_object.year, 'base_hostel_room_number' :initial['roomNo']}
            # feed_initial = { 'hostelName' : initial['subscribedHostel'] , 'month': automation_object.month, 'year' : automation_object.year }
            # feed_initial['hostelName'] = initial['subscribedHostel']
            automation_objects = Automation.objects.filter(feed_start_date__lte=datetime.today(),
                                                           feed_off_date__gte=datetime.today(), feed_on_off=True)
            form = self.form_class(initial=feed_initial)

            feedback_ON_OFF = True
            if len(automation_objects) == 1:
                automation_object = automation_objects[0]
                # print(automation_object.feed_start_date)

                feed_on_off = automation_object.feed_on_off
                if feed_on_off == True:
                    feed_start_date = automation_object.feed_start_date
                    feed_off_date = automation_object.feed_off_date
                    if feed_start_date <= datetime.now().date() and feed_off_date >= datetime.now().date():
                        feedback_ON_OFF = True
                    else:
                        feedback_ON_OFF = False
                else:
                    feedback_ON_OFF = False
            else:
                feedback_ON_OFF = False
            print('feed_on_off :', feedback_ON_OFF)
            return render(self.request, self.template_name,
                          {'form': form, 'feedback_ON_OFF': feedback_ON_OFF, 'mth': automation_object.month,
                           'yr': automation_object.year})

    # def dispach(self, request):
    #     uname = self.request.user
    #     if MessFeedback.objects.filter(username=uname,month=m1,year=y1).count() == 1:
    #         return HttpResponseRedirect('update')

    def form_valid(self, form):
        print(' Checking form valid ', self.request.user)
        form.save(self.request.user)
        return super(NewFeedback, self).form_valid(form)

    def get_success_url(self, *args, **kargs):
        print('Executing success url!')
        messages.success(self.request, 'Your feedback is submitted successfully !')
        return reverse_lazy('update_feedback')


class UpdateFeedback(UpdateView):
    model = MessFeedback
    form_class = NewFeedbackForm
    template_name = "student_portal/messfeedback_form.html"

    def get_object(self, *args, **kwargs):
        automation_objects = Automation.objects.filter(feed_start_date__lte=datetime.today(),
                                                       feed_off_date__gte=datetime.today(), feed_on_off=True)
        automation_object = automation_objects[0]
        # automation_month_year = str(automation_object.month) + '_' + str(automation_object.year)
        user_feedback = get_object_or_404(MessFeedback, username=self.request.user, month=automation_object.month,
                                          year=automation_object.year)
        initial = get_initial(self.request, month=automation_object.month, year=automation_object.year)
        feed_initial = {'subscribedHostelName': initial['subscribedHostel'], 'month': automation_object.month,
                        'year': automation_object.year, 'roomNo': initial['roomNo'],
                        'baseHostelName': initial['baseHostel'], 'filled': True}
        user_feedback.__dict__.update(feed_initial)
        return user_feedback

    def get_context_data(self, **kwargs):

        automation_objects = Automation.objects.filter(feed_start_date__lte=datetime.today(),
                                                       feed_off_date__gte=datetime.today(), feed_on_off=True)
        automation_object = automation_objects[0]
        # automation_month_year = str(automation_object.month) + '_' + str(automation_object.year)
        feedback_ON_OFF = True
        if get_object_or_404(MessFeedback, username=self.request.user, month=automation_object.month,
                             year=automation_object.year):
            feedback_ON_OFF = True
        else:
            feedback_ON_OFF = False

        context = super().get_context_data(**kwargs)
        context['feedback_ON_OFF'] = feedback_ON_OFF
        context['mth'] = automation_object.month
        context['yr'] = automation_object.year
        return context

    def get_success_url(self, *args, **kwargs):
        messages.success(self.request, 'Your feedback is updated successfully !')
        return reverse_lazy('update_feedback')


# @periodic_task(
#     run_every=(crontab(minute='*/1')),
#     name="check_filled_feedback",
#     ignore_result=True
# )

# def checker(request):
#     uname = request.user
#     if MessFeedback.objects.filter(username=uname,month=m1,year=y1).count() == 0:
#         return HttpResponseRedirect(reverse('student_portal:new_feedback',kwargs={'user': request.user}))
#     if MessFeedback.objects.filter(username=uname,month=m1,year=y1).count() == 1:
#         return HttpResponseRedirect(reverse('student_portal:update_feedback',kwargs={'user': request.user}))

def check_filled_feedback(request):
    # use m1, y1, uname to check distinct
    uname = request.user
    # print ('line 370 checking for MESS feedback ::',uname)
    # request.POST['user']
    # fbform = MessFeedback.objects.get(username=uname) #,month=curr_month,year=curr_year
    if MessFeedback.objects.filter(username=uname).count() == 0:
        # how to pass parameters...
        return redirect('new_feedback')
    if MessFeedback.objects.filter(username=uname).count() > 0:
        # how to pass parameters...

        automation_objects = Automation.objects.filter(feed_start_date__lte=datetime.today(),
                                                       feed_off_date__gte=datetime.today(), feed_on_off=True)
        if len(automation_objects) == 0 or len(automation_objects) > 1:
            return redirect('new_feedback')
        automation_object = automation_objects[0]
        if MessFeedback.objects.filter(username=uname, month=automation_object.month,
                                       year=automation_object.year).count() == 1:
            return redirect('update_feedback')
        else:
            return redirect('new_feedback')

    # ideally this should not happen
    return redirect('home')


Month_dict = {1: 'january', 2: 'feburary', 3: 'march', 4: 'april', 5: 'may', 6: 'june', 7: 'july', 8: 'august',
              9: 'september', 10: 'october', 11: 'novermber', 12: 'december'}
preference_month = (curr_month + 1)
preference_year = (curr_year)
if preference_month > 12:
    preference_month = 1
    preference_year += 1


class NewPreference(FormView):
    form_class = NewPreferenceForm
    template_name = "student_portal/preference_form.html"

    automation_objects = Automation.objects.filter(pref_start_date__lte=datetime.today(),
                                                   pref_off_date__gte=datetime.today(), pref_on_off=True)

    # print(automation_objects)

    def get(self, request):
        uname = self.request.user
        automation_objects = Automation.objects.filter(pref_start_date__lte=datetime.today(),
                                                       pref_off_date__gte=datetime.today(), pref_on_off=True)
        if len(automation_objects) == 0 or len(automation_objects) > 1:
            preference_ON_OFF = False
            form = self.form_class()
            return render(self.request, self.template_name, {'form': form, 'preference_ON_OFF': preference_ON_OFF})

        automation_object = automation_objects[0]
        # automation_month_year = str(automation_object.month) + '_' + str(automation_object.year)

        # month=automation_object_month, year = automation_object_year) :
        if Preference.objects.filter(username=uname, month=automation_object.month,
                                     year=automation_object.year).count() == 1:
            return HttpResponseRedirect('update')
        else:
            automation_objects = Automation.objects.filter(pref_start_date__lte=datetime.today(),
                                                           pref_off_date__gte=datetime.today(), pref_on_off=True)
            # pref_month = automation_object.month
            # preference_year = automation_object.year
            #
            # FinalPreference.
            initial = get_initial(self.request, month=automation_object.month, year=automation_object.year)

            pref_dict = {'hostelName': initial['baseHostel'], 'month': automation_object.month,
                         'year': automation_object.year, 'roomNo': initial['roomNo'],
                         'student_id': initial['student_id'], 'student_name': initial['student_name']}
            # pref_dict = {'hostelName' :initial['baseHostel'] , 'month': automation_object.month , 'year':automation_object.year, 'base_hostel_room_number' :initial['roomNo']}
            # pref_dict = {'hostelName' :initial['baseHostel'] , 'month': automation_object.month , 'year':automation_object.year }

            form = self.form_class(initial=pref_dict)
            preference_ON_OFF = True
            if len(automation_objects) == 1:
                automation_object = automation_objects[0]
                print(automation_object.pref_start_date)

                pref_on_off = automation_object.pref_on_off
                if pref_on_off == True:
                    pref_start_date = automation_object.pref_start_date
                    pref_off_date = automation_object.pref_off_date
                    if pref_start_date < datetime.now().date() and pref_off_date > datetime.now().date():
                        preference_ON_OFF = True
                    else:
                        preference_ON_OFF = False
                else:
                    preference_ON_OFF = False
            else:
                preference_ON_OFF = False
            return render(self.request, self.template_name,
                          {'form': form, 'preference_ON_OFF': preference_ON_OFF, 'mth': automation_object.month,
                           'yr': automation_object.year})

    """
    def form_valid(self, form):
        automation_objects = Automation.objects.filter(pref_start_date__lte=datetime.today(), pref_off_date__gte=datetime.today(), pref_on_off=True)
        automation_object = automation_objects[0]
        # print(automation_object.month)
        form.cleaned_data['month'] = automation_object.month
        form.cleaned_data['year'] = automation_object.year

        print(form.cleaned_data['month'])

        form.cleaned_data['month_year'] = str(form.cleaned_data['month']) + '_' + str(form.cleaned_data['year'])
        # form.save(self.request.user)
        pref_obj = Preference(month_year = form.cleaned_data['month_year'])
        pref_obj.month = form.cleaned_data['month']
        pref_obj.year = form.cleaned_data['year']
        pref_obj.username = self.request.user
        # pref_obj.hostelName =
        pref_obj.h1 = form.cleaned_data['h1']
        pref_obj.h2 = form.cleaned_data['h2']
        pref_obj.h3 = form.cleaned_data['h3']
        pref_obj.save()
        # return super(NewPreference, self).form_valid(form)
        return HttpResponseRedirect('update')
    """

    def form_valid(self, form):
        print('Executing Form Valid!')
        form.save(self.request.user)
        mess_allot(self.request)
        return super(NewPreference, self).form_valid(form)

    def get_success_url(self, *args, **kargs):
        return reverse_lazy('final_preference')

    # Find out which variable would be storing the fields value


def mess_allot(request):
    month_no = datetime.now().month

    if month_no == 12:
        month_1 = calendar.month_name[1]
    else:
        month_1 = calendar.month_name[month_no + 1]

    h1 = HostelMessVacancies.objects.get(hostelName=request.POST.get('h1'), month=month_1)
    h2 = HostelMessVacancies.objects.get(hostelName=request.POST.get('h2'), month=month_1)
    h3 = HostelMessVacancies.objects.get(hostelName=request.POST.get('h3'), month=month_1)

    automation_objects = Automation.objects.filter(pref_start_date__lte=datetime.today(),
                                                   pref_off_date__gte=datetime.today(), pref_on_off=True)
    automation_object = automation_objects[0]

    student1 = OccupantDetails.objects.get(webmail=request.user.username)

    for i in AllHostelMetaData.objects.all():
        temp = i.hostelRoomOccupant
        temp2 = i.hostelRoom
        mymodel = apps.get_model(app_label='hab_app', model_name=temp)
        mymodel2 = apps.get_model(app_label='hab_app', model_name=temp2)
        if mymodel.objects.filter(occupantId=student1.idNo).exists():
            rorelation = mymodel.objects.get(occupantId=student1.idNo)
            if mymodel2.objects.filter(roomNo=rorelation.roomNo).exists():
                rohostel = mymodel2.objects.get(roomNo=rorelation.roomNo)
            break

    h_self = HostelMessVacancies.objects.get(hostelName=rorelation.hostelName, month=month_1)

    final_pref = FinalPreference.objects.create(hostelName=rorelation.hostelName, roomNo=rohostel.roomNo, username=request.user.username, month=automation_object.month, year=automation_object.year)

    pref = Preference.objects.get(username=request.user.username, month=automation_object.month, year=automation_object.year)
    final_pref.student_id = pref.student_id
    final_pref.student_name = pref.student_name

    one_month = datetime.today().date() + relativedelta(months=+1)
    temp = DebarredStudents.objects.filter(webmail=request.user.username, debarred_hostel="All Hostels", start_date__lte=one_month, end_date__gte=one_month).count()

    if temp != 0:
        final_pref.final_hostel = "Debarred"
    else:
        if h1.occupied < h1.upper_limit and DebarredStudents.objects.filter(
                webmail=request.user.username, debarred_hostel=h1.hostelName,
                start_date__lte=one_month, end_date__gte=one_month).count() == 0:
            final_pref.final_hostel = h1.hostelName
            h1.occupied = h1.occupied + 1
            h_self.occupied = h_self.occupied - 1
            h_self.save()
            h1.save()
        else:
            if h2.occupied < h2.upper_limit and DebarredStudents.objects.filter(
                    webmail=request.user.username, debarred_hostel=h2.hostelName,
                    start_date__lte=one_month, end_date__gte=one_month).count() == 0:
                final_pref.final_hostel = h2.hostelName
                h2.occupied = h2.occupied + 1
                h_self.occupied = h_self.occupied - 1
                h_self.save()
                h2.save()
            else:
                if h3.occupied < h3.upper_limit and DebarredStudents.objects.filter(
                        webmail=request.user.username, debarred_hostel=h3.hostelName,
                        start_date__lte=one_month, end_date__gte=one_month).count() == 0:
                    final_pref.final_hostel = h3.hostelName
                    h3.occupied = h3.occupied + 1
                    h_self.occupied = h_self.occupied - 1
                    h_self.save()
                    h3.save()
                else:
                    if DebarredStudents.objects.filter(
                            webmail=request.user.username, debarred_hostel=rorelation.hostelName,
                            start_date__lte=one_month, end_date__gte=one_month).count() == 0:
                        final_pref.final_hostel = rorelation.hostelName
                    else:
                        final_pref.final_hostel = "Debarred"

    final_pref.save()


def final_preference(request):
    automation_objects = Automation.objects.filter(pref_start_date__lte=datetime.today(),
                                                   pref_off_date__gte=datetime.today(), pref_on_off=True)
    if len(automation_objects) == 1:
        obj = automation_objects[0]
        month = obj.month
        year = obj.year
        obj1 = FinalPreference.objects.get(month=month, year=year, username=request.user.username)
        if obj1.final_hostel == "Debarred":
            debarred_msg = True
            context = {'obj1': obj1, 'month': month, 'year': year, 'debarred_msg': debarred_msg}
            return render(request, 'student_portal/final_preference.html', context)

        else:
            context = {'obj1': obj1, 'month': month, 'year': year}
            return render(request, 'student_portal/final_preference.html', context)
    else:
        return redirect('new_preference')


def check_filled_preference(request):
    # use m2, y2, uname to check distinct
    # Extract current mess subscription from HAB database

    if Preference.objects.filter(username=request.user.username).count() == 0:
        # how to pass parameters...
        return redirect('new_preference')
    if Preference.objects.filter(username=request.user.username).count() > 0:
        # how to pass parameters...
        automation_objects = Automation.objects.filter(pref_start_date__lte=datetime.today(),
                                                       pref_off_date__gte=datetime.today(), pref_on_off=True)
        if len(automation_objects) == 0:
            print('helll1')
            return redirect('new_preference')

        if len(automation_objects) == 1:
            automation_object = automation_objects[0]
            if Preference.objects.filter(username=request.user.username, month=automation_object.month,
                                         year=automation_object.year).count() == 1:
                print('helll2')
                return redirect('final_preference')
            else:
                return redirect('new_preference')

        if len(automation_objects) > 1:
            return redirect('new_preference')

    return redirect('home')


@login_required
def gensec_feedback(request):
    automation_objects = Automation.objects.filter(feed_start_date__lte=datetime.today(),
                                                   feed_off_date__gte=datetime.today(), feed_on_off=True)
    if request.method == 'GET':
        if len(automation_objects) == 0 or len(automation_objects) > 1:
            feedback_ON_OFF = False
            form = GenSecFeedbackForm()
            return render(request, 'student_portal/gensec_feedback.html',
                          {'form': form, 'feedback_ON_OFF': feedback_ON_OFF})

        automation_object = automation_objects[0]

        feed_on_off = automation_object.feed_on_off
        # global feedback_ON_OFF = False
        if feed_on_off == True:
            feed_start_date = automation_object.feed_start_date
            feed_off_date = automation_object.feed_off_date
            if feed_start_date <= datetime.now().date() <= feed_off_date:
                feedback_ON_OFF = True
            else:
                feedback_ON_OFF = False
        else:
            feedback_ON_OFF = False

        hostelgensec = request.user
        hostelgss = AllHostelMetaData.objects.filter(hostelGensec=hostelgensec)
        if not len(hostelgss) == 1:
            return HttpResponse('your data not found !!!')
        else:
            hostelgs = hostelgss[0]
            messfeedback_objs = MessFeedback.objects.filter(subscribedHostelName=hostelgs.hostelName,
                                                            month=automation_object.month, year=automation_object.year)
            messfeedback_count = len(messfeedback_objs)
            mess_subscribed_external = len(
                FinalPreference.objects.filter(month=automation_object.month, year=automation_object.year,
                                               final_hostel=hostelgs.hostelName))
            mess_unsubscribed_internal = len(
                FinalPreference.objects.filter(month=automation_object.month, year=automation_object.year,
                                               hostelName=hostelgs.hostelName))
            # net_alloted =
            # here i m making an assumption that finalpreference contail onlythose who are allotted hostelmess of another hostel

            if Opi_calculated.objects.filter(hostelName=hostelgs.hostelName, month=automation_object.month,
                                             year=automation_object.year).count() == 0:
                form = GenSecFeedbackForm()
            else:
                opi_obj = Opi_calculated.objects.filter(hostelName=hostelgs.hostelName, month=automation_object.month,
                                                        year=automation_object.year)[0]
                print(opi_obj)
                initialData = {'raw_materials_quality': opi_obj.raw_materials_quality}
                form = GenSecFeedbackForm(initial=initialData)
            return render(request, 'student_portal/gensec_feedback.html', {
                'form': form,
                'feedback_ON_OFF': feedback_ON_OFF,
                'messfeedback_count': messfeedback_count,
                'mess_subscribed_external': mess_subscribed_external,
                'mess_unsubscribed_internal': mess_unsubscribed_internal,
                'mth': automation_object.month, 'yr': automation_object.year})

    if request.method == 'POST' and 'btn1' in request.POST:
        automation_objects = Automation.objects.filter(feed_start_date__lte=datetime.today(),
                                                       feed_off_date__gte=datetime.today(), feed_on_off=True)
        if len(automation_objects) == 0 or len(automation_objects) > 1:
            feedback_ON_OFF = False
            form = GenSecFeedbackForm()
            return render(request, 'student_portal/gensec_feedback.html',
                          {'form': form, 'feedback_ON_OFF': feedback_ON_OFF, 'mth': automation_object.month,
                           'yr': automation_object.year})

        automation_object = automation_objects[0]
        hostelgensec = request.user
        hostelgss = AllHostelMetaData.objects.filter(hostelGensec=hostelgensec)

        if not len(hostelgss) == 1:
            return HttpResponse('your data not found !!!')
        else:
            gensec_hostelname = (hostelgss[0]).hostelName
            # print(gensec_hostelname)
            if Opi_calculated.objects.filter(hostelName=gensec_hostelname, month=automation_object.month,
                                             year=automation_object.year).count() == 0:
                opi_object = Opi_calculated(hostelName=gensec_hostelname, month=automation_object.month,
                                            year=automation_object.year)
                opi_object.opi_value = 0.0
                opi_object.numberOfSubscriptions = 0

            else:
                opi_object = Opi_calculated.objects.filter(hostelName=gensec_hostelname, month=automation_object.month,
                                                           year=automation_object.year)[0]
                opi_object.raw_materials_quality = Decimal(request.POST['raw_materials_quality'])
                opi_object.numberOfSubscriptions = opi_object.numberOfSubscriptions
                print(' type of variable : ', type(opi_object.raw_materials_quality),
                      request.POST['raw_materials_quality'])
                opi_object.opi_value = (
                                                   2 * opi_object.cleanliness_av + 1 * opi_object.catering_av + 3 * opi_object.breakfast_quality_av + 3 * opi_object.lunch_quality_av + 3 * opi_object.dinner_quality_av + 2 * opi_object.raw_materials_quality) / 14

            opi_object.save()
            messages.success(request, 'Your feedback is submitted successfully !')
            return HttpResponseRedirect(reverse('gensec_feedback'))

    queryDict = request.POST
    print(queryDict)
    hostelgensec = request.user
    hostelgss = AllHostelMetaData.objects.filter(hostelGensec=hostelgensec)
    if not len(hostelgss) == 1:
        return HttpResponse('your data not found !!!')
    else:
        hostelgs = hostelgss[0]
        if request.method == 'POST' and 'btn2' in request.POST:
            queryset = MessFeedback.objects.filter(subscribedHostelName=hostelgs.hostelName,
                                                   month=queryDict['month_val'], year=queryDict['year_val'])
            messfeedback_resource = MessFeedbackResource()
            dataset = messfeedback_resource.export(queryset)
            response = HttpResponse(dataset.csv, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="mess_feedbacks.csv"'
            return response

        if request.method == 'POST' and 'btn3' in request.POST:
            queryset = MessFeedback.objects.filter(subscribedHostelName=hostelgs.hostelName,
                                                   month=queryDict['month_val'], year=queryDict['year_val'])
            messfeedback_resource = MessFeedbackResource()
            dataset = messfeedback_resource.export(queryset)
            response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="mess_feedbacks.xls"'
            return response

    if request.method == 'POST' and 'btn_opi' in request.POST:
        hostelgs = hostelgss[0]
        queryset = Opi_calculated.objects.filter(hostelName=hostelgs.hostelName, month=queryDict['month2_val'],
                                                 year=queryDict['year2_val'])
        opi_dict = {}
        if (len(queryset) == 1):
            print(queryset[0].opi_value)
            feedback_ON_OFF = True
            form = GenSecFeedbackForm()
            return render(request, 'student_portal/gensec_feedback.html',
                          {'form': form, 'feedback_ON_OFF': feedback_ON_OFF, 'opi_hostel': queryset[0]})
        return HttpResponseRedirect(reverse('gensec_feedback'))


@login_required
def updateinfo(request):
    student1 = None
    roomoccupantrelation = None
    student1 = OccupantDetails.objects.get(webmail=request.user.username)
    if student1 is None:
        print('Student id = %s' % (student1))
        return HttpResponse(' Webmail Id  : %s Not found in Occupant table !' % (webmail))
    if TemporaryDetails.objects.filter(webmail=request.user.username).count() == 0:
        tobeAlloted = OccupantDetails.objects.get(webmail=request.user.username)
    else:
        tobeAlloted = TemporaryDetails.objects.filter(webmail=request.user.username).order_by('-created')[0]

    for i in AllHostelMetaData.objects.all():
        temp = i.hostelRoomOccupant
        # RORelation
        mymodel = apps.get_model(app_label='hab_app', model_name=temp)
        if mymodel.objects.filter(occupantId=student1.idNo).exists():
            roomoccupantrelation = mymodel.objects.get(occupantId=student1.idNo)
            break
    if roomoccupantrelation is None:
        print('Not Found in Room Occupant relation Table')
        return HttpResponse('ID No : %s Not found in any Room relation table !' % (student1))
    print(' Roomoocupantrelation = %s' % (roomoccupantrelation))
    hostelname = roomoccupantrelation.hostelName
    roomNo = roomoccupantrelation.roomNo
    if request.method == 'GET':
        # if TemporaryDetails.objects.filter(webmail=request.user.username,ct_approval="Pending").exists():
        #     return HttpResponse("You already have a Pending Request!!!")
        # student,created = TemporaryDetails.objects.get_or_create(webmail=request.user.username,ct_approval="Pending")
        initialData = {
            'name': tobeAlloted.name, 'idType': tobeAlloted.idType,
            'gender': tobeAlloted.gender, 'saORda': tobeAlloted.saORda,
            'altEmail': tobeAlloted.altEmail, 'idNo': tobeAlloted.idNo,
            'mobNo': tobeAlloted.mobNo, 'emgercencyNo': tobeAlloted.emgercencyNo,
            'Address': tobeAlloted.Address, 'Pincode': tobeAlloted.Pincode,
            'bankName': tobeAlloted.bankName, 'bankAccount': tobeAlloted.bankAccount,
            'IFSCCode': tobeAlloted.IFSCCode, 'accHolderName': tobeAlloted.accHolderName,
            'photo': tobeAlloted.photo, 'idPhoto': tobeAlloted.idPhoto,
        }
        form = updateinfoform(initial=initialData)
        return render(request, 'student_portal/edit_details.html',
                      {'form': form, 'student': student1, 'hostelname': hostelname, 'roomNo': roomNo})
    # return HttpResponse(student.name)
    if request.method == 'POST':
        if TemporaryDetails.objects.filter(webmail=request.user.username, ct_approval="Pending").exists():
            instance = TemporaryDetails.objects.filter(webmail=request.user.username, ct_approval="Pending")[0]
            form = updateinfoform(request.POST, request.FILES, instance=instance)
            if form.is_valid():
                form.save()
                return redirect('track')
            else:
                return HttpResponse("Invalid Form")

        form = updateinfoform(request.POST, request.FILES)
        if form.is_valid():
            temporary_data = form.save(commit=False)
            if not temporary_data.photo:
                temporary_data.photo = student1.photo
            if not temporary_data.idPhoto:
                temporary_data.idPhoto = student1.idPhoto
            temporary_data.webmail = request.user.username
            temporary_data.ct_approval = "Pending"
            temporary_data.flag = 1
            temporary_data.save()
            # messages.success(request, 'Changes are saved!!')
            return redirect('track')
        else:
            return HttpResponse(form.errors)
    # return HttpResponse(404)


@login_required
def track(request):
    student_requests = TemporaryDetails.objects.filter(webmail=request.user.username).order_by('-created')
    return render(request, 'student_portal/student_track.html', {'req': student_requests})