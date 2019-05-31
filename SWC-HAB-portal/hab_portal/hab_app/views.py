from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
#from django.core.urlresolvers import reverse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import redirect
import decimal
from time import strptime
from datetime import *
from django.apps import apps
from hab_app.forms import *
from hab_app.initialise import *
from dateutil.relativedelta import relativedelta

from student_portal.models import *
from student_portal.forms import *

from django.views.decorators.cache import cache_page
from hab_app.models import *

from .resources import *
from tablib import Dataset
import calendar
from difflib import SequenceMatcher


def main_page(request):
    print('Inside main_page function of hab app')
    return HttpResponse("<h1> Welcome to Hab Portal IITG </h1>")

def home(request):
    request.session['hostel_view'] = "a1x"
    request.session['student'] = "no"
    flag = 0
    for i in AllHostelMetaData.objects.all():
        temp = i.hostelViewPermission
        view_model = apps.get_model(app_label='hab_app', model_name=temp)
        if view_model.objects.filter(webmail=request.session['username']).exists():
            flag = 1
            request.session['hostel_view'] = i.hostelName
            break
    if request.session['username'] == "chr_hab":
        hostels = AllHostelMetaData.objects.all().order_by('hostelName')
        return render(request, 'hab_app/chrView.html', {'hostels': hostels})
    elif request.session['username'] == "some_faculty":
        return render(request, 'hab_app/generalView.html')
    elif AllHostelMetaData.objects.filter(hostelCTid=request.session['username']).exists():
        ROtable = AllHostelMetaData.objects.get(hostelCTid=request.session['username'])
        return render(request, 'hab_app/caretakerView.html', {'ROtable': ROtable})
    elif ChrViewAccess.objects.filter(webmail=request.session['username']).exists():
        return render(request, 'hab_app/chrView.html')
    elif flag == 1:
        ROtable = AllHostelMetaData.objects.get(hostelName__iexact=request.session['hostel_view'])
        return render(request, 'hab_app/caretakerView.html', {'ROtable': ROtable})
    elif 'server' in request.session and request.session['server'] == "202.141.80.12":
        return render(request, 'hab_app/generalView.html')
    else:
        request.session['student'] = "yes"
        if OccupantDetails.objects.filter(webmail=request.session['username']).exists():
            # return render(request,'student_portal/home.html')
            return redirect('/hab_portal/student_portal/updateinfo')
        else:
            if request.method == 'GET':
                return render(request, 'hab_app/addReqdetails.html')
            if request.method == 'POST':
                if OccupantDetails.objects.filter(idNo=request.POST.get('OccupantId')).exists():
                    student = OccupantDetails.objects.get(idNo=request.POST.get('OccupantId'))
                    if student.webmail:
                        return render(request, 'hab_app/addReqdetails.html', {'message': 1})
                    student.webmail = request.session['username']
                    student.save()
                    return redirect('/hab_portal/student_portal/updateinfo')
                else:
                    return render(request, 'hab_app/addReqdetails.html', {'message': 2})


def login_page(request):
    return render(request, 'hab_app/login.html', {})


@login_required(login_url='/hab_portal/temp_login/')
def logout1(request):
    logout(request)
    return HttpResponseRedirect(reverse('user_login'))

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                request.session['username'] = username
                request.session['password'] = password
                return HttpResponseRedirect(reverse('home'))
            else:
                return HttpResponse("account not active")
        else:
            return HttpResponse("Invalid Login Credentials")

    else:
        return render(request, 'hab_app/login.html')


@login_required(login_url='/hab_portal/temp_login/')
def vacate(request):
    if request.session['student'] == "no":
        if request.session['hostel_view'] != "a1x":
            ROtable = AllHostelMetaData.objects.get(hostelName__iexact=request.session['hostel_view'])

        else:
            ROtable = AllHostelMetaData.objects.get(hostelCTid=request.session['username'])

        temp = ROtable.hostelRoomOccupant
        parameter = request.GET.get('param')
        mymodel = apps.get_model(app_label='hab_app', model_name=temp)
        now = datetime.now()
        start = now - timedelta(days=365)
        end = now + timedelta(days=5)
        tobeVacatedShortly = mymodel.objects.filter(toRoomStay__range=(start.date(), end.date()))
        tobeVacatedAll = mymodel.objects.all()
        for i in tobeVacatedShortly:
            if OccupantDetails.objects.filter(idNo=i.occupantId).exists():
                temp1 = OccupantDetails.objects.get(idNo=i.occupantId)
                i.name = temp1.name
                i.contact = temp1.mobNo
        for i in tobeVacatedAll:
            if OccupantDetails.objects.filter(idNo=i.occupantId).exists():
                temp1 = OccupantDetails.objects.get(idNo=i.occupantId)
                i.name = temp1.name
                i.contact = temp1.mobNo
        if parameter == "2":
            return render(request, 'hab_app/vacate.html', {'ROtable': ROtable, 'tobeVacated': tobeVacatedAll})
        else:
            return render(request, 'hab_app/vacate.html', {'ROtable': ROtable, 'tobeVacated': tobeVacatedShortly})
    else:
        form = LoginForm()
        return render(request, 'student_portal/login.html', {'message': 5, 'form': form})


@login_required(login_url='/hab_portal/temp_login/')
def deleteDetails(request):
    if request.session['student'] == "no":
        ROtable = AllHostelMetaData.objects.get(hostelCTid=request.session['username'])
        temp = ROtable.hostelRoomOccupant
        mymodel = apps.get_model(app_label='hab_app', model_name=temp)
        if request.method == 'POST':
            if request.POST.get('vacate_opt') == "1" or request.POST.get('vacate_opt') == "4":

                occupantId = request.GET.get('param')
                occupant = mymodel.objects.get(occupantId=occupantId)
                p = Log_Table(occupantId=occupantId)
                p.hostelName = ROtable.hostelName
                p.roomNo = str(occupant.roomNo)
                p.messStatus = occupant.messStatus
                # p.toMess = occupant.toMess
                # p.fromMess = occupant.fromMess
                p.toRoomStay = occupant.toRoomStay
                p.fromRoomStay = occupant.fromRoomStay
                p.comment = occupant.comment
                p.save()
                occupant = mymodel.objects.get(occupantId=occupantId).delete()
                initial = OccupantDetails.objects.filter(idNo=occupantId).values()[0]
                log_occ = Occupant_Log_Table(**initial)
                log_occ.save()
                log = OccupantDetails.objects.filter(idNo=occupantId).delete()
                log_temp = TemporaryDetails.objects.filter(idNo=occupantId).delete()
                return redirect('hab_app:vacate')

            elif request.POST.get('vacate_opt') == "2" or request.POST.get('vacate_opt') == "3":
                return redirect(reverse('hab_app:editRODetails', kwargs={'occ_id': request.GET.get('param')}))
            else:
                return HttpResponse("Under Construction")

        else:
            return HttpResponse("go back")

    else:
        form = LoginForm()
        return render(request, 'student_portal/login.html', {'message': 5, 'form': form})


@login_required(login_url='/hab_portal/temp_login/')
def showDetails(request):
    if request.session['student'] == "no":
        if request.session['hostel_view'] != "a1x":
            ROtable = AllHostelMetaData.objects.get(hostelName__iexact=request.session['hostel_view'])

        else:
            ROtable = AllHostelMetaData.objects.get(hostelCTid=request.session['username'])
        if request.method == 'GET':
            parameter = request.GET.get('param')
            details = OccupantDetails.objects.get(idNo=parameter)
            temp = ROtable.hostelRoomOccupant
            mymodel = apps.get_model(app_label='hab_app', model_name=temp)
            roDetails = mymodel.objects.get(occupantId=parameter)
            return render(request, 'hab_app/showDetails.html',
                          {'ROtable': ROtable, 'details': details, 'roDetails': roDetails})

    else:
        form = LoginForm()
        return render(request, 'student_portal/login.html', {'message': 5, 'form': form})

    
@login_required(login_url='/hab_portal/temp_login/')
def showDetails2(request):
    if request.session['student'] == "no":
        if request.method == 'GET':
            parameter = request.GET.get('param')
            pobj = OccupantDetails.models.get(idNo=parameter)
            details = OccupantDetails.objects.get(idNo=parameter)
            ROtable = AllHostelMetaData.objects.get(hostelCTid=request.session['username'])
            temp = ROtable.hostelRoomOccupant
            mymodel = apps.get_model(app_label='hab_app', model_name=temp)
            roDetails = mymodel.objects.get(occupantId=parameter)
            return render(request, 'hab_app/showDetails2.html', {'details': details, 'roDetails': roDetails})
    else:
        form = LoginForm()
        return render(request, 'student_portal/login.html', {'message': 5, 'form': form})


    
@login_required(login_url='/hab_portal/temp_login/')
def editRODetails(request, occ_id):
    if request.session['student'] == "no":
        if request.session['hostel_view'] != "a1x":
            ROtable = AllHostelMetaData.objects.get(hostelName__iexact=request.session['hostel_view'])

        else:
            ROtable = AllHostelMetaData.objects.get(hostelCTid=request.session['username'])

        temp = ROtable.hostelRoomOccupant
        mymodel = apps.get_model(app_label='hab_app', model_name=temp)
        room_model = apps.get_model(app_label='hab_app', model_name=ROtable.hostelRoom)
        if request.method == 'GET':
            occupant_id = occ_id
            RO_data = mymodel.objects.get(occupantId=occupant_id)
            ROedit_form = HostelRoomOccupantRelationForm(instance=RO_data)
            return render(request, 'hab_app/editRODetails.html', {'ROtable': ROtable, 'ROedit_form': ROedit_form})
        if request.method == 'POST':

            form = HostelRoomOccupantRelationForm(request.POST)
            p = mymodel.objects.get(occupantId=request.POST.get('occupantId'))
            if form.is_valid():
                occupant = form.save(commit=False)
                p.hostelName = ROtable.hostelName
                p.roomNo = room_model.objects.get(roomNo=request.POST.get('roomNo'))
                p.messStatus = occupant.messStatus
                # p.toMess = occupant.toMess
                # p.fromMess = occupant.fromMess
                p.toRoomStay = occupant.toRoomStay
                p.fromRoomStay = occupant.fromRoomStay
                p.comment = occupant.comment
                p.save()

                return redirect('home')
            else:
                return HttpResponse("Form Invalid")
    else:
        form = LoginForm()
        return render(request, 'student_portal/login.html', {'message': 5, 'form': form})


@login_required(login_url='/hab_portal/temp_login/')
def editOccupantDetails(request):
    if request.session['student'] == "no":
        if request.session['hostel_view'] == "a1x":

            ROtable = AllHostelMetaData.objects.get(hostelCTid=request.session['username'])
            temp = ROtable.hostelRoomOccupant
            mymodel = apps.get_model(app_label='hab_app', model_name=temp)
            room_model = apps.get_model(app_label='hab_app', model_name=ROtable.hostelRoom)
            if request.method == 'POST':
                # instance1 = get_object_or_404(mymodel,occupantId=request.POST.get('occupantId'))
                instance2 = get_object_or_404(OccupantDetails, idNo=request.POST.get('occupantId'))
                form1 = HostelRoomOccupantRelationForm(request.POST)
                form2 = OccupantDetailsForm(request.POST, request.FILES, instance=instance2)

                if form2.is_valid():
                    occupant = form2.save(commit=False)
                    if form2.data['New_OccupantId']:
                        occupant.idNo = request.POST.get('New_OccupantId')
                        if OccupantDetails.objects.filter(idNo=request.POST.get('occupantId')).exists():
                            OccupantDetails.objects.filter(idNo=request.POST.get('occupantId')).delete()
                    occupant.save()

                else:
                    return HttpResponse("Form Invalid 2")

                if form1.is_valid():
                    occupant = form1.save(commit=False)
                    if form2.data['New_OccupantId']:

                        p = mymodel(occupantId=OccupantDetails.objects.get(idNo=request.POST.get('New_OccupantId')))
                        p.hostelName = ROtable.hostelName
                        p.roomNo = get_object_or_404(room_model, roomNo=request.POST.get('roomNo'))
                        p.messStatus = occupant.messStatus
                        # p.toMess = occupant.toMess
                        # p.fromMess = occupant.fromMess
                        p.toRoomStay = occupant.toRoomStay
                        p.fromRoomStay = occupant.fromRoomStay
                        p.comment = occupant.comment
                        p.save()
                    else:
                        p = mymodel.objects.get(occupantId=request.POST.get('occupantId'))
                        p.hostelName = ROtable.hostelName
                        p.roomNo = get_object_or_404(room_model, roomNo=request.POST.get('roomNo'))
                        p.messStatus = occupant.messStatus
                        # p.toMess = occupant.toMess
                        # p.fromMess = occupant.fromMess
                        p.toRoomStay = occupant.toRoomStay
                        p.fromRoomStay = occupant.fromRoomStay
                        p.comment = occupant.comment
                        p.save()
                else:
                    return HttpResponse("Form Invalid")
                return redirect('hab_app:existingOccupants')

            if request.method == 'GET':
                occupantId = request.GET.get('param')
                form1 = HostelRoomOccupantRelationForm(instance=mymodel.objects.get(occupantId=occupantId))
                form2 = OccupantDetailsEditForm(instance=OccupantDetails.objects.get(idNo=occupantId))
                return render(request, 'hab_app/temp2.html', {'ROtable': ROtable, 'form1': form1, 'form2': form2})
    else:
        form = LoginForm()
        return render(request, 'student_portal/login.html', {'message': 5, 'form': form})


@login_required(login_url='/hab_portal/temp_login/')
def allot(request):
    if request.session['student'] == "no":
        if request.session['hostel_view'] != "a1x":
            ROtable = AllHostelMetaData.objects.get(hostelName__iexact=request.session['hostel_view'])
            tobeAlloted = UpcomingOccupant.objects.filter(hostelName__iexact=request.session['hostel_view'])
            tobeAlloted2 = UpcomingOccupantRequest.objects.filter(hostelName__iexact=request.session['hostel_view'],
                                                                  isApprovedChr="Approved")

        else:
            ROtable = AllHostelMetaData.objects.get(hostelCTid=request.session['username'])
            tobeAlloted = UpcomingOccupant.objects.filter(hostelName__iexact=ROtable.hostelName)
            tobeAlloted2 = UpcomingOccupantRequest.objects.filter(hostelName__iexact=ROtable.hostelName,
                                                                  isApprovedChr="Approved")
            # logger.error('Something went wrong!')
        return render(request, 'hab_app/allot.html',
                      {'ROtable': ROtable, 'tobeAlloted': tobeAlloted, 'tobeAlloted2': tobeAlloted2})

    else:
        form = LoginForm()
        return render(request, 'student_portal/login.html', {'message': 5, 'form': form})


@login_required(login_url='/hab_portal/temp_login/')
def addDetails(request):
    if request.session['student'] == "no":

        if request.session['hostel_view'] == "a1x":

            ROtable = AllHostelMetaData.objects.get(hostelCTid=request.session['username'])
            temp = ROtable.hostelRoomOccupant
            mymodel = apps.get_model(app_label='hab_app', model_name=temp)
            room_model = apps.get_model(app_label='hab_app', model_name=ROtable.hostelRoom)
            if request.method == 'POST':

                form1 = HostelRoomOccupantRelationForm(data=request.POST)
                form2 = OccupantDetailsForm(request.POST, request.FILES)
                if form2.is_valid():
                    instance = form2.save(commit=False)
                    instance.idNo = request.POST.get('occupantId')
                    instance.save()
                    print("tes")
                    if form1.is_valid():
                        occupant = form1.save(commit=False)
                        p = mymodel(occupantId=OccupantDetails.objects.get(idNo=form1.cleaned_data['occupantId']))
                        p.hostelName = ROtable.hostelName
                        p.roomNo = room_model.objects.get(roomNo=request.POST.get('roomNo'))
                        p.messStatus = occupant.messStatus
                        p.toRoomStay = occupant.toRoomStay
                        p.fromRoomStay = occupant.fromRoomStay
                        p.comment = occupant.comment
                        p.save()

                    else:
                        return HttpResponse("Form Invalid!!!")
                else:
                    return HttpResponse("Form Invalid!!!")
                log = UpcomingOccupant.objects.get(occupantId=request.POST.get('occupantId')).delete()
                tobeAlloted = UpcomingOccupant.objects.filter(hostelName__iexact=ROtable.hostelName)
                return redirect('hab_app:allot')

            if request.method == 'GET':
                occupantId = request.GET.get('param')
                tobeAlloted = UpcomingOccupant.objects.get(occupantId=occupantId)
                initialData1 = {'occupantId': tobeAlloted.occupantId, 'hostelName': tobeAlloted.hostelName,
                                'roomNo': tobeAlloted.roomNo, 'fromRoomStay': tobeAlloted.fromStay,
                                'toRoomStay': tobeAlloted.toStay}
                initialData2 = {'name': tobeAlloted.occupantName, 'idType': tobeAlloted.idType}
                form1 = HostelRoomOccupantRelationForm(initial=initialData1)
                form2 = OccupantDetailsForm(initial=initialData2)
                return render(request, 'hab_app/temp.html', {'form1': form1, 'form2': form2})

    else:
        form = LoginForm()
        return render(request, 'student_portal/login.html', {'message': 5, 'form': form})


@login_required(login_url='/hab_portal/temp_login/')
def ct_add_occupant(request):
    if request.session['student'] == "no":
        if request.session['hostel_view'] == "a1x":

            ROtable = AllHostelMetaData.objects.get(hostelCTid=request.session['username'])
            temp = ROtable.hostelRoomOccupant
            mymodel = apps.get_model(app_label='hab_app', model_name=temp)
            room_model = apps.get_model(app_label='hab_app', model_name=ROtable.hostelRoom)
            if request.method == 'POST':

                form1 = HostelRoomOccupantRelationForm(data=request.POST)
                form2 = OccupantDetailsForm(request.POST, request.FILES)
                if mymodel.objects.filter(occupantId=request.POST.get('occupantId')).exists():
                    return HttpResponse("Occupant already exists.change the details in existing occupants list!!!")
                if form2.is_valid():
                    instance = form2.save(commit=False)
                    instance.idNo = request.POST.get('occupantId')
                    instance.save()
                    if form1.is_valid():
                        occupant = form1.save(commit=False)
                        p = mymodel(occupantId=OccupantDetails.objects.get(idNo=form1.cleaned_data['occupantId']))
                        p.hostelName = ROtable.hostelName
                        p.roomNo = room_model.objects.get(roomNo=request.POST.get('roomNo'))
                        p.messStatus = occupant.messStatus
                        p.toRoomStay = occupant.toRoomStay
                        p.fromRoomStay = occupant.fromRoomStay
                        p.comment = occupant.comment
                        p.save()

                    else:
                        return HttpResponse("Form Invalid!!!")
                else:
                    return HttpResponse("Form Invalid!!!")

                return redirect('home')

            if request.method == 'GET':
                form1 = HostelRoomOccupantRelationForm(initial={'hostelName': ROtable.hostelName})
                form2 = OccupantDetailsForm()
                return render(request, 'hab_app/ct_add_occupant.html',
                              {'form1': form1, 'form2': form2, 'ROtable': ROtable})
    else:
        form = LoginForm()
        return render(request, 'student_portal/login.html', {'message': 5, 'form': form})


@login_required(login_url='/hab_portal/temp_login/')
def addDetails2(request):
    if request.session['student'] == "no":
        if request.session['hostel_view'] == "a1x":

            ROtable = AllHostelMetaData.objects.get(hostelCTid=request.session['username'])
            temp = ROtable.hostelRoomOccupant
            mymodel = apps.get_model(app_label='hab_app', model_name=temp)
            room_model = apps.get_model(app_label='hab_app', model_name=ROtable.hostelRoom)
            if request.method == 'POST':

                form1 = HostelRoomOccupantRelationForm(data=request.POST)
                form2 = OccupantDetailsForm(request.POST, request.FILES)
                if form2.is_valid():
                    instance = form2.save(commit=False)
                    instance.idNo = request.POST.get('occupantId')
                    instance.save()
                    if form1.is_valid():
                        occupant = form1.save(commit=False)
                        p = mymodel(occupantId=OccupantDetails.objects.get(idNo=form1.cleaned_data['occupantId']))
                        p.hostelName = ROtable.hostelName
                        p.roomNo = room_model.objects.get(roomNo=request.POST.get('roomNo'))
                        p.messStatus = occupant.messStatus
                        p.toRoomStay = occupant.toRoomStay
                        p.fromRoomStay = occupant.fromRoomStay
                        p.comment = occupant.comment
                        p.save()

                    else:
                        print(form1.errors)
                else:
                    print(form2.errors)
                log = UpcomingOccupantRequest.objects.get(id_no=request.POST.get('occupantId'),
                                                          isApprovedChr="Approved").delete()
                return redirect('hab_app:allot')

            if request.method == 'GET':
                occupantId = request.GET.get('param')
                tobeAlloted = UpcomingOccupantRequest.objects.get(id_no=occupantId, isApprovedChr="Approved")
                initialData1 = {
                    'occupantId': tobeAlloted.id_no, 'hostelName': tobeAlloted.hostelName,
                    'fromRoomStay': tobeAlloted.From_Date, 'toRoomStay': tobeAlloted.To_Date,

                }
                initialData2 = {
                    'name': tobeAlloted.guestname, 'idType': tobeAlloted.id_type,
                    'gender': tobeAlloted.Gender, 'saORda': tobeAlloted.saORda,
                    'webmail': tobeAlloted.Webmail_id, 'altEmail': tobeAlloted.Alternate_email_id,
                    'mobNo': tobeAlloted.Mobile_No, 'emgercencyNo': tobeAlloted.Emergency_Mobile_No,
                    'Address': tobeAlloted.Address, 'Pincode': tobeAlloted.Pincode,
                    'bankName': tobeAlloted.Bank_Name, 'bankAccount': tobeAlloted.Bank_Account_No,
                    'IFSCCode': tobeAlloted.IFSCCode, 'accHolderName': tobeAlloted.Account_Holder_Name,
                    'photo': tobeAlloted.photo, 'idPhoto': tobeAlloted.idPhoto,
                }

                form1 = HostelRoomOccupantRelationForm(initial=initialData1)
                form2 = OccupantDetailsForm(initial=initialData2)
                return render(request, 'hab_app/temp.html', {'ROtable': ROtable, 'form1': form1, 'form2': form2})

    else:
        form = LoginForm()
        return render(request, 'student_portal/login.html', {'message': 5, 'form': form})


@login_required(login_url='/hab_portal/temp_login/')
def existingOccupants(request):
    if request.session['student'] == "no":
        print(request.session['hostel_view'])
        if request.session['hostel_view'] != "a1x":
            ROtable = AllHostelMetaData.objects.get(hostelName__iexact=request.session['hostel_view'])

        else:
            ROtable = AllHostelMetaData.objects.get(hostelCTid=request.session['username'])
        temp = ROtable.hostelRoomOccupant
        mymodel = apps.get_model(app_label='hab_app', model_name=temp)
        relation = mymodel.objects.all()
        occupants = list()
        relation_list = list()
        for i in relation:
            if OccupantDetails.objects.filter(idNo=i.occupantId).exists():
                occupants.append(OccupantDetails.objects.get(idNo=i.occupantId))
                relation_list.append(i)
        zipped = zip(relation_list, occupants)

        if AllHostelMetaData.objects.filter(hostelCTid=request.user.username).exists():
            query_dict = list()
            query_dict_2 = list()
            obj = AllHostelMetaData.objects.get(hostelCTid=request.user.username)
            model_1 = apps.get_model(app_label='hab_app', model_name=obj.hostelRoomOccupant)

            for i in OccupantDetails.objects.all():
                if model_1.objects.filter(occupantId=i.idNo).exists():
                    query_dict.append(i)
                    query_dict_2.append(model_1.objects.get(occupantId=i.idNo))

            if request.method == 'POST' and 'btn_details_xls' in request.POST:
                aa = OccupantDetailsResource()
                dataset = aa.export(query_dict)
                response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = 'attachment; filename="Occupant Details.xls"'
                return response

            if request.method == 'POST' and 'btn_room_details_xls' in request.POST:
                aa = RORelationResource()
                dataset = aa.export(query_dict_2)
                response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = 'attachment; filename="Occupant Details.xls"'
                return response

        return render(request, 'hab_app/existingOccupants.html', {'ROtable': ROtable, 'zipped': zipped})

    else:
        form = LoginForm()
        return render(request, 'student_portal/login.html', {'message': 5, 'form': form})


@login_required(login_url='/hab_portal/temp_login/')
def roomDetails(request):
    if request.session['student'] == "no":
        if request.method == 'GET':
            index = request.GET.get('param')
            # occupied rooms
            # get the relation table name and room table name

            if request.session['hostel_view'] != "a1x":
                ROtable = AllHostelMetaData.objects.get(hostelName__iexact=request.session['hostel_view'])

            else:

                ROtable = AllHostelMetaData.objects.get(hostelCTid=request.session['username'])
            relation_table = ROtable.hostelRoomOccupant
            room_table = ROtable.hostelRoom
            # print('room_table' , room_table)
            # get the model names for query
            relation_model = apps.get_model(app_label='hab_app', model_name=relation_table)
            room_model = apps.get_model(app_label='hab_app', model_name=room_table)
            relation = relation_model.objects.all()
            occupants = list()
            room_list = list()

            # return HttpResponse(relation)
            for i in relation:
                if datetime.now().date() <= i.toRoomStay and datetime.now().date() >= i.fromRoomStay:
                    occupants.append(OccupantDetails.objects.get(idNo=i.occupantId))
                    room_list.append(room_model.objects.get(roomNo=i.roomNo))

            zipped = zip(room_list, occupants)
            # for empty rooms
            room_no_list = list()
            for i in room_list:
                room_no_list.append(i.roomNo)

            empty_rooms = room_model.objects.all().exclude(roomNo__in=room_no_list)

            # all_rooms = room_model.objects.all()
            # # return HttpResponse(room_list)
            # for i in all_rooms:
            #     flag = 0
            #     for j in room_list:
            #         if i.roomNo == j.roomNo:
            #             flag = 1
            #             break
            #     if flag == 0:
            #         empty_rooms.append(i)
            if index == "1":
                return render(request, 'hab_app/occupiedRooms.html', {'ROtable': ROtable, 'zipped': zipped})

            elif index == "2":
                # empty rooms
                return render(request, 'hab_app/emptyRooms.html', {'ROtable': ROtable, 'empty_rooms': empty_rooms})

            else:
                return render(request, 'hab_app/totalRooms.html',
                              {'ROtable': ROtable, 'zipped': zipped, 'empty_rooms': empty_rooms})
    else:
        form = LoginForm()
        return render(request, 'student_portal/login.html', {'message': 5, 'form': form})


@login_required(login_url='/hab_portal/temp_login/')
def generalAllot(request):
    if request.session['student'] == "no":
        if request.method == 'POST':
            form = UpcomingOccupantRequestForm(request.POST, request.FILES)
            if form.is_valid():
                occupant = form.save(commit=False)
                occupant.save()
                return redirect('hab_app:trackApplication')
            else:
                print(form.errors)

        if request.method == 'GET':
            obj = User.objects.get(username=request.session['username'])
            initialData = {'Host_Name': obj.first_name, 'Host_Webmail_Id': obj.username}
            form = UpcomingOccupantRequestForm(initial=initialData)
            return render(request, "hab_app/generalAllot.html", {'form': form})

    else:
        form = LoginForm()
        return render(request, 'student_portal/login.html', {'message': 5, 'form': form})


# @login_required(login_url='/hab_portal/cms_login/')
@login_required(login_url='/hab_portal/temp_login/')
def trackApplication(request):
    if request.session['student'] == "no":
        applicants = UpcomingOccupantRequest.objects.filter(Host_Webmail_Id=request.session['username'])
        return render(request, "hab_app/generalTrack.html", {'applicants': applicants})
    else:
        form = LoginForm()
        return render(request, 'student_portal/login.html', {'message': 5, 'form': form})


# def approveApplication(request):
#     if request.method == 'GET':
#         if request.GET.get('param') :
#             idNo = request.GET.get('param')
#             guest = UpcomingOccupantRequest.objects.get(id_no = idNo)
#             guest.isApprovedFirst = "Approved"
#             guest.save()
#     applicants = UpcomingOccupantRequest.objects.filter(To_be_approved_by__iexact = request.session['username'] , isApprovedFirst = "Pending" )
#     return render(request,"hab_app/approveApplication.html",{'applicants':applicants})
#
#
# def disapproveApplication(request):
#     if request.method == 'GET':
#         if request.GET.get('param') :
#             idNo = request.GET.get('param')
#             guest = UpcomingOccupantRequest.objects.get(id_no = idNo)
#             guest.isApprovedFirst = "Disapproved"
#             guest.save()
#     applicants = UpcomingOccupantRequest.objects.filter(To_be_approved_by__iexact = request.session['username'] , isApprovedFirst = "Pending" )
#     return render(request,"hab_app/approveApplication.html",{'applicants':applicants})
# @login_required(login_url='/hab_portal/cms_login/')
@login_required(login_url='/hab_portal/temp_login/')
def chrAllot(request):
    if request.session['student'] == "no":
        if request.session['username'] == "chr_hab":
            hostels = AllHostelMetaData.objects.all()
            if request.method == 'POST':
                form = UpcomingOccupantForm(data=request.POST)
                if form.is_valid():
                    occupant = form.save()
                    occupant.save()
                    form = UpcomingOccupantForm()
                    return render(request, 'hab_app/addOccupant.html', {'form': form})
                else:
                    print(form.errors)

            else:
                form = UpcomingOccupantForm()
                return render(request, 'hab_app/addOccupant.html', {'form': form})
        else:
            return HttpResponse("You are not Authorized to access this page!!!")
    else:
        form = LoginForm()
        return render(request, 'student_portal/login.html', {'message': 5, 'form': form})


@login_required(login_url='/hab_portal/temp_login/')
def chrApproveApplication(request):
    if request.session['student'] == "no":
        hostels = AllHostelMetaData.objects.all()
        if request.method == 'GET':
            if request.GET.get('param'):
                idNo = request.GET.get('param')
                guest = UpcomingOccupantRequest.objects.get(id_no=idNo, isApprovedChr="Pending")
                form = UpcomingOccupantRequestChrForm(instance=guest)
                return render(request, "hab_app/chrApproveEdit.html", {'form': form, 'guest': guest})
        if request.method == 'POST':
            form = UpcomingOccupantRequestChrForm(request.POST, request.FILES)
            guest = UpcomingOccupantRequest.objects.get(id_no=request.POST.get('id_no'),
                                                        isApprovedChr="Pending").delete()
            if form.is_valid():
                upcoming_occupant = form.save(commit=False)
                if 'ap' in request.POST:
                    upcoming_occupant.isApprovedChr = "Approved"
                    upcoming_occupant.save()
                elif 'dp' in request.POST:
                    upcoming_occupant.isApprovedChr = "Disapproved"
                    upcoming_occupant.save()
            else:
                print(form.errors)
        applicants = UpcomingOccupantRequest.objects.filter(isApprovedChr="Pending")
        return render(request, "hab_app/chrApproveApplication.html", {'applicants': applicants})

    else:
        form = LoginForm()
        return render(request, 'student_portal/login.html', {'message': 5, 'form': form})


# def chrDisapproveApplication(request):
#
#     if request.method == 'GET':
#         if request.GET.get('param') :
#             idNo = request.GET.get('param')
#             # guest = UpcomingOccupantRequest.objects.get(id_no = idNo,isApprovedChr="Pending")
#             # guest.isApprovedChr = "Disapproved"
#             # guest.save()
#
#     applicants = UpcomingOccupantRequest.objects.filter(isApprovedChr = "Pending" )
#     return render(request,"hab_app/chrApproveApplication.html",{'applicants':applicants})

# @login_required(login_url='/hab_portal/cms_login/')
@login_required(login_url='/hab_portal/temp_login/')
def chrViewRoom(request):
    if request.session['student'] == "no":
        if request.method == 'GET':
            if request.GET.get('param'):
                hostel = request.GET.get('param')
                ROtable = AllHostelMetaData.objects.get(hostelName__iexact=hostel)
                relation_table = ROtable.hostelRoomOccupant
                room_table = ROtable.hostelRoom
                # get the model names for query
                relation_model = apps.get_model(app_label='hab_app', model_name=relation_table)
                room_model = apps.get_model(app_label='hab_app', model_name=room_table)
                relation = relation_model.objects.all()
                occupants = list()
                room_list = list()

                for i in relation:
                    if datetime.now().date() <= i.toRoomStay and datetime.now().date() >= i.fromRoomStay:
                        occupants.append(OccupantDetails.objects.get(idNo=i.occupantId))
                        room_list.append(room_model.objects.get(roomNo=i.roomNo))

                zipped = zip(room_list, occupants)
                # for empty rooms
                room_no_list = list()
                for i in room_list:
                    room_no_list.append(i.roomNo)

                empty_rooms = room_model.objects.all().exclude(roomNo__in=room_no_list)
                # empty_rooms = list()
                # all_rooms = room_model.objects.all()
                # for i in all_rooms:
                #     flag = 0
                #     for j in room_list:
                #         if i.roomNo == j.roomNo:
                #             flag = 1
                #             break
                #     if flag == 0:
                #         empty_rooms.append(i)
                hostels = AllHostelMetaData.objects.all()
                return render(request, 'hab_app/chrViewRoom.html',
                              {'ROtable': ROtable, 'zipped': zipped, 'empty_rooms': empty_rooms, 'hostel': hostel})
    else:
        form = LoginForm()
        return render(request, 'student_portal/login.html', {'message': 5, 'form': form})


@cache_page(10 * 60)
def chrViewSpecialRooms(request):
    if request.session['student'] == "no":
        if request.method == 'GET':
            if request.GET.get('param'):
                hostel = request.GET.get('param')
                ROtable = AllHostelMetaData.objects.get(hostelName__iexact=hostel)
                relation_table = ROtable.hostelRoomOccupant
                room_table = ROtable.hostelRoom
                # get the model names for query
                relation_model = apps.get_model(app_label='hab_app', model_name=relation_table)
                room_model = apps.get_model(app_label='hab_app', model_name=room_table)
                relation = relation_model.objects.all()
                occupants = list()
                room_list = list()

                for i in relation:

                    if OccupantDetails.objects.filter(idNo=i.occupantId).exists():
                        if room_model.objects.filter(roomNo=i.roomNo).exists():
                            if room_model.objects.filter(roomNo=i.roomNo, special_category__in=[1, 2]).exists():
                                occupants.append(OccupantDetails.objects.get(idNo=i.occupantId))
                                room_list.append(room_model.objects.get(roomNo=i.roomNo))

                zipped = zip(room_list, occupants)
                # for empty rooms
                empty_rooms = list()
                all_rooms = room_model.objects.all()
                for i in all_rooms:
                    flag = 0
                    for j in room_list:
                        if i.roomNo == j.roomNo:
                            flag = 1
                            break
                    if flag == 0:
                        if i.special_category != 0:
                            empty_rooms.append(i)
                hostels = AllHostelMetaData.objects.all()
                return render(request, 'hab_app/chrViewSpecialRooms.html',
                              {'ROtable': ROtable, 'zipped': zipped, 'empty_rooms': empty_rooms, 'hostel': hostel})
    else:
        form = LoginForm()
        return render(request, 'student_portal/login.html', {'message': 5, 'form': form})


@login_required(login_url='/hab_portal/temp_login/')
def chrHostelSummary(request):
    if request.session['student'] == "no":
        hostels = AllHostelMetaData.objects.all()
        hostelSummary = list()
        for i in hostels.iterator():
            curr_hostel = list()
            hostel = i.hostelName
            ROtable = AllHostelMetaData.objects.get(hostelName__iexact=hostel)
            relation_table = ROtable.hostelRoomOccupant
            room_table = ROtable.hostelRoom
            # get the model names for query
            relation_model = apps.get_model(app_label='hab_app', model_name=relation_table)
            room_model = apps.get_model(app_label='hab_app', model_name=room_table)
            relation = relation_model.objects.all()
            room_list = list()

            for i in relation:
                if i.toRoomStay >= datetime.now().date() >= i.fromRoomStay:
                    room_list.append(room_model.objects.get(roomNo=i.roomNo))

            # for empty rooms
            # empty_rooms = list()
            # all_rooms = room_model.objects.all()
            # total rooms
            room_no_list = list()
            for i in room_list:
                room_no_list.append(i.roomNo)
            curr_hostel.append(room_model.objects.all().count())
            # occupied rooms
            curr_hostel.append(len(room_list))
            abandoned = 0
            usable = 0
            partial = 0
            first = 0
            second = 0
            third = 0
            ground = 0
            # usable_list=list()

            abandoned = room_model.objects.filter(roomStatus="Abandoned").count()
            usable = room_model.objects.filter(roomStatus="Usable").count()
            partial = room_model.objects.filter(roomStatus="Partially Damaged").count()
            # for i in all_rooms.iterator():
            #     if i.roomStatus == "Abandoned":
            #         abandoned= abandoned+1
            #     if i.roomStatus == "Usable":
            #         usable=usable+1
            #         usable_list.append(i)
            #
            #     if i.roomStatus == "Partially Damaged":
            #         partial=partial+1

            # flag = 0
            # for j in room_list:
            #     if i.roomNo == j.roomNo:
            #         flag = 1
            #         break
            # if flag == 0:
            #     empty_rooms.append(i)
            occupancy_list = ["Single Occupancy", "Double Occupancy"]
            temp = room_model.objects.filter(roomOccupancyType__in=occupancy_list, roomStatus="Usable").exclude(
                roomNo__in=room_no_list)
            first = temp.filter(floorInfo="First Floor").count()
            second = temp.filter(floorInfo="Second Floor").count()
            third = temp.filter(floorInfo="Third Floor").count()
            ground = temp.filter(floorInfo="Ground Floor").count()

            # for i in usable_list:
            #     flag=0
            #     for j in room_list:
            #         if i.roomNo == j.roomNo:
            #             flag=1
            #             break
            #     if flag==0 :
            #         if str(i.roomOccupancyType) == "Single Occupancy" or str(i.roomOccupancyType) == "Double Occupancy":
            #             if i.floorInfo == "First Floor" :
            #                 first=first+1
            #             if i.floorInfo == "Second Floor":
            #                 second=second+1
            #             if i.floorInfo == "Third Floor":
            #                 third=third+1
            #             if i.floorInfo == "Ground Floor":
            #                 ground=ground+1
            # ready to be alloted
            curr_hostel.append(ground)
            curr_hostel.append(first)
            curr_hostel.append(second)
            curr_hostel.append(third)
            curr_hostel.append(first + second + third + ground)
            curr_hostel.append(abandoned)
            hostelSummary.append(curr_hostel)
        total = [0] * 8

        for i in hostelSummary:
            for j in range(8):
                total[j] = total[j] + i[j]
        # return HttpResponse(total)
        zipped_summary = zip(hostelSummary, hostels)
        return render(request, 'hab_app/chrHostelSummary.html', {'zipped_summary': zipped_summary, 'total': total})
    else:
        form = LoginForm()
        return render(request, 'student_portal/login.html', {'message': 5, 'form': form})


@login_required(login_url='/hab_portal/temp_login/')
def chrCaretakerView(request):
    if request.session['student'] == "no":
        if request.method == 'GET':
            request.session['hostel_view'] = request.GET.get('param')
            username = request.session['hostel_view']
            ROtable = AllHostelMetaData.objects.get(hostelName__iexact=username)
            return render(request, 'hab_app/caretakerView.html', {'ROtable': ROtable})
    else:
        form = LoginForm()
        return render(request, 'student_portal/login.html', {'message': 5, 'form': form})


# chairman uploading csv file for bulk allottment
@login_required(login_url='/hab_portal/temp_login/')
def chrFreshersBulkAllot(request):
    if request.session['student'] == "no":
        if request.method == 'GET':
            return render(request, 'hab_app/FreshersBulkAllotUpload.html')

        if request.method == "POST":
            csv_file = request.FILES['csv_file']
            # return HttpResponse(csv_file)
            freshers_bulkallot_resource = FreshersBulkAllotResource()
            dataset = Dataset()
            imported_data = dataset.load(csv_file.read().decode('utf-8'))
            print(imported_data)
            result = freshers_bulkallot_resource.import_data(dataset, dry_run=True)
            if not result.has_errors():
                freshers_bulkallot_resource.import_data(dataset, dry_run=False)
            return render(request, 'hab_app/chrView.html')

    else:
        form = LoginForm()
        return render(request, 'student_portal/login.html', {'message': 5, 'form': form})


# delete room
@login_required(login_url='/hab_portal/temp_login/')
def chrRoomDelete(request, hostel_name):
    if request.session['student'] == "no":
        hostelRoomstring = hostel_name + "Room"
        hostelRoomModel = apps.get_model(app_label='hab_app', model_name=hostelRoomstring)
        if request.method == 'GET':
            if request.GET.get('param3'):
                roomNo = request.GET.get('param3')
                hostelRoomModel.objects.filter(roomNo=roomNo).delete()
                roomdetailslist = hostelRoomModel.objects.all()
                return render(request, 'hab_app/chrRoomDetailsPage.html',
                              {'roomdetailslist': roomdetailslist, 'hostelname': hostel_name})
    else:
        form = LoginForm()
        return render(request, 'student_portal/login.html', {'message': 5, 'form': form})


@login_required(login_url='/hab_portal/temp_login/')
def chrRoomDetailsEdit(request):
    if request.session['student'] == "no":
        if request.method == 'GET':
            if request.GET.get('param'):
                hostelname = request.GET.get('param')
                hostelRoomstring = hostelname + "Room"
                hostelRoomModel = apps.get_model(app_label='hab_app', model_name=hostelRoomstring)
                roomdetailslist = hostelRoomModel.objects.all()
                return render(request, 'hab_app/chrRoomDetailsPage.html',
                              {'roomdetailslist': roomdetailslist, 'hostelname': hostelname})
    else:
        form = LoginForm()
        return render(request, 'student_portal/login.html', {'message': 5, 'form': form})


@login_required(login_url='/hab_portal/temp_login/')
def chrRoomDetailsEdit2(request, hostel_name):
    if request.session['student'] == "no":
        hostelRoomstring = hostel_name + "Room"
        hostelRoomModel = apps.get_model(app_label='hab_app', model_name=hostelRoomstring)
        if request.method == 'GET':
            if request.GET.get('param2'):
                roomNo = request.GET.get('param2')
                RoomObject = hostelRoomModel.objects.get(roomNo=roomNo)
                initialData = {

                    'roomNo': RoomObject.roomNo,  # should not be changed
                    'roomOccupancyType': RoomObject.roomOccupancyType,
                    'floorInfo': RoomObject.floorInfo,
                    'roomStatus': RoomObject.roomStatus,
                    'roomOccupancyGender': RoomObject.roomOccupancyGender,
                    'comments': RoomObject.comments,

                }
                form = chrRoomDetailsEditForm(initial=initialData)
                return render(request, 'hab_app/RoomEditingForm.html', {'form': form, })

        if request.method == 'POST':
            form = chrRoomDetailsEditForm(request.POST)
            if form.is_valid():
                if 'upd' in request.POST:
                    roomNo = form.cleaned_data.get('roomNo')
                    hostel_room = hostelRoomModel.objects.get(roomNo=roomNo)
                    # return HttpResponse(hostelRoomModel)
                    hostel_room.roomOccupancyType = form.cleaned_data.get('roomOccupancyType')
                    hostel_room.floorInfo = form.cleaned_data.get('floorInfo')
                    hostel_room.roomStatus = form.cleaned_data.get('roomStatus')
                    hostel_room.roomOccupancyGender = form.cleaned_data.get('roomOccupancyGender')
                    hostel_room.comments = form.cleaned_data.get('comments')
                    hostel_room.save()

                if 'del' in request.POST:
                    roomNo = form.cleaned_data.get('roomNo')
                    hostelRoomModel.objects.filter(roomNo=roomNo).delete()


            else:
                print(form.errors)
                return HttpResponse("error")
            roomdetailslist = hostelRoomModel.objects.all()
            return render(request, 'hab_app/chrRoomDetailsPage.html',
                          {'roomdetailslist': roomdetailslist, 'hostelname': hostel_name})
    else:
        form = LoginForm()
        return render(request, 'student_portal/login.html', {'message': 5, 'form': form})


# add a room
# @login_required(login_url='/hab_portal/cms_login/')
@login_required(login_url='/hab_portal/temp_login/')
def chrRoomAdd(request, hostel_name):
    if request.session['student'] == "no":
        if request.method == 'GET':
            form = chrRoomDetailsEditForm(initial=None)
            return render(request, 'hab_app/RoomAddForm.html', {'form': form, })
        if request.method == 'POST':
            form = chrRoomDetailsEditForm(request.POST)
            if form.is_valid():
                hostelRoomstring = hostel_name + "Room"
                hostelRoomModel = apps.get_model(app_label='hab_app', model_name=hostelRoomstring)
                roomNo = form.cleaned_data.get('roomNo')
                if hostelRoomModel.objects.filter(roomNo=roomNo).count() > 0:
                    return HttpResponse("Room with same room number already exists")
                else:
                    roomOccupancyType = form.cleaned_data.get('roomOccupancyType')
                    floorInfo = form.cleaned_data.get('floorInfo')
                    roomStatus = form.cleaned_data.get('roomStatus')
                    roomOccupancyGender = form.cleaned_data.get('roomOccupancyGender')
                    comments = form.cleaned_data.get('comments')
                    hostelRoomModel.objects.create(roomNo=roomNo, roomOccupancyType=roomOccupancyType,
                                                   floorInfo=floorInfo, roomStatus=roomStatus,
                                                   roomOccupancyGender=roomOccupancyGender,
                                                   comments=comments)



            else:
                print(form.errors)
                return HttpResponse("error")

            roomdetailslist = hostelRoomModel.objects.all()
            return render(request, 'hab_app/chrRoomDetailsPage.html',
                          {'roomdetailslist': roomdetailslist, 'hostelname': hostel_name})
    else:
        form = LoginForm()
        return render(request, 'student_portal/login.html', {'message': 5, 'form': form})


# @login_required(login_url='/hab_portal/cms_login/')
@login_required(login_url='/hab_portal/temp_login/')
def caretakerapproveinfo(request):
    if request.session['student'] == "no":
        if request.session['hostel_view'] != "a1x":
            temp = AllHostelMetaData.objects.get(hostelName__iexact=request.session['hostel_view'])
        else:
            temp = AllHostelMetaData.objects.get(hostelCTid=request.session['username'])
        hostelname = temp.hostelName
        hostelROstring = hostelname + "RORelation"
        hostelROModel = apps.get_model(app_label='hab_app', model_name=hostelROstring)
        room_model = apps.get_model(app_label='hab_app', model_name=temp.hostelRoom)
        students_info_update = []
        students_ro = []
        toapprove_info_list_total = TemporaryDetails.objects.filter(ct_approval="Pending")
        for student in toapprove_info_list_total:
            if hostelROModel.objects.filter(occupantId=student.idNo).exists():
                students_info_update.append(student)
                students_ro.append(hostelROModel.objects.get(occupantId=student.idNo))
        zipped = zip(students_info_update, students_ro)

        if request.method == 'GET':
            if request.GET.get('param'):
                idNo = request.GET.get('param')
                student1 = TemporaryDetails.objects.filter(idNo=idNo, ct_approval="Pending")[0]
                initialData = {
                    'name': student1.name, 'idType': student1.idType,
                    'gender': student1.gender, 'saORda': student1.saORda,
                    'altEmail': student1.altEmail, 'idNo': student1.idNo,
                    'mobNo': student1.mobNo, 'emgercencyNo': student1.emgercencyNo,
                    'Address': student1.Address, 'Pincode': student1.Pincode,
                    'bankName': student1.bankName, 'bankAccount': student1.bankAccount,
                    'IFSCCode': student1.IFSCCode, 'accHolderName': student1.accHolderName,
                    'photo': student1.photo, 'idPhoto': student1.idPhoto, 'webmail': student1.webmail,
                }
                form = CtApproveStudentEditForm(initial=initialData)
                return render(request, "hab_app/CTapproveEdit.html", {'form': form, 'ROtable': temp})

        if request.method == 'POST':

            instance = TemporaryDetails.objects.filter(idNo=request.POST.get('idNo'), ct_approval="Pending")[0]
            occupant_instance = OccupantDetails.objects.get(idNo=request.POST.get('idNo'))
            form = CtApproveStudentEditForm(request.POST, request.FILES, instance=instance)

            if form.is_valid():
                # return HttpResponse(request.FILES.get('photo'))
                temporary_data = form.save(commit=False)
                # log_stud = TemporaryDetails.objects.get(idNo = request.POST.get('idNo'),ct_approval="Pending")
                if 'd' in request.POST:
                    temporary_data.ct_approval = "Disapproved"
                    temporary_data.save()
                    occupant_instance.flag = 0
                    occupant_instance.save()
                    students_info_update = []
                    students_ro = []
                    toapprove_info_list_total = TemporaryDetails.objects.filter(ct_approval="Pending")
                    # To be Optimized here ... for loop not required
                    for student in toapprove_info_list_total:
                        if hostelROModel.objects.filter(occupantId=student.idNo).count() == 1:
                            students_info_update.append(student)
                            students_ro.append(hostelROModel.objects.get(occupantId=student.idNo))
                    zipped = zip(students_info_update, students_ro)
                    return render(request, "hab_app/caretaker_student_info_tobeupdated.html",
                                  {'zipped': zipped, 'ROtable': temp})
                elif 'a' in request.POST:
                    # return HttpResponse(temporary_data.photo)
                    # print(temporary_data)
                    temporary_data.ct_approval = "Approved"
                    temporary_data.save()
                    log_ro = hostelROModel.objects.filter(occupantId=temporary_data.idNo).values()[0]
                    log = OccupantDetails.objects.get(idNo=temporary_data.idNo).delete()
                    p = OccupantDetails()
                    p.name = temporary_data.name
                    # id type - roll no/aadhar no/project id etc
                    p.idType = temporary_data.idType
                    # rollno/aadhar no etc
                    # primary_key removed temp
                    p.idNo = temporary_data.idNo
                    # vgv
                    p.gender = temporary_data.gender
                    # specially abled/differently abled
                    p.saORda = temporary_data.saORda
                    p.webmail = temporary_data.webmail
                    p.altEmail = temporary_data.altEmail
                    p.mobNo = temporary_data.mobNo
                    p.emgercencyNo = temporary_data.emgercencyNo
                    p.photo = temporary_data.photo
                    p.idPhoto = temporary_data.idPhoto
                    p.Address = temporary_data.Address
                    p.Pincode = temporary_data.Pincode
                    p.bankName = temporary_data.bankName
                    p.bankAccount = temporary_data.bankAccount
                    p.IFSCCode = temporary_data.IFSCCode
                    # account holder name
                    p.accHolderName = temporary_data.accHolderName
                    p.flag = 1
                    p.save()
                    occupant = hostelROModel(occupantId=OccupantDetails.objects.get(idNo=temporary_data.idNo))
                    occupant.hostelName = log_ro['hostelName']
                    occupant.roomNo = room_model.objects.get(roomNo=log_ro['roomNo_id'])
                    occupant.messStatus = log_ro['messStatus']
                    occupant.toRoomStay = log_ro['toRoomStay']
                    occupant.fromRoomStay = log_ro['fromRoomStay']
                    occupant.comment = log_ro['comment']
                    occupant.save()
                    students_info_update = []
                    students_ro = []
                    toapprove_info_list_total = TemporaryDetails.objects.filter(ct_approval="Pending")
                    for student in toapprove_info_list_total:
                        if hostelROModel.objects.filter(occupantId=student.idNo).count() == 1:
                            students_info_update.append(student)
                            students_ro.append(hostelROModel.objects.get(occupantId=student.idNo))
                    zipped = zip(students_info_update, students_ro)
                    return render(request, "hab_app/caretaker_student_info_tobeupdated.html",
                                  {'zipped': zipped, 'ROtable': temp})
            else:
                print(form.errors)

        return render(request, "hab_app/caretaker_student_info_tobeupdated.html", {'zipped': zipped, 'ROtable': temp})

    else:
        form = LoginForm()
        return render(request, 'student_portal/login.html', {'message': 5, 'form': form})


# Mess OPI Related views
# month and year calculations for the display of last month graph
curr_month = datetime.now().month
curr_year = datetime.now().year
m1 = curr_month
y1 = curr_year
m1 = m1 - 1
m1_y1 = ""
if m1 < 1:
    m1 = 12
    y1 = y1 - 1
m11 = m1 - 1
y11 = y1
if m11 < 1:
    m11 = 12
    y11 = y11 - 1
m111 = m11 - 1
y111 = y11
if m111 < 1:
    m111 = 12
    y111 = y111 - 1


# @login_required(login_url='/hab_portal/cms_login/')
@login_required(login_url='/hab_portal/temp_login/')
def mess_opi(request):
    if request.session['student'] == "no":
        if request.method == 'GET':
            data = Opi_calculated.objects.filter(month=m1, year=y1)
            data1 = Opi_calculated.objects.filter(month=m11, year=y11)
            # print(data1)
            # data.append(data1)
            # print(data)
            return render(request, 'hab_app/mess_opi.html', {'data': data, 'data1': data1})

        if request.method == 'POST':
            opi_month = request.POST.get('month_val')
            opi_year = request.POST.get('year_val')
            feedbacks = MessFeedback.objects.filter(month=opi_month, year=opi_year)
            # print(feedbacks)
            hostelss = {}
            noh = 0  # number of hostels
            freq_hostelss = {}  # hostel wise freq of the feedback
            for fb in feedbacks:
                #   count No. of feedbacks hostelwise
                if fb.subscribedHostelName not in hostelss:
                    hostelss[fb.subscribedHostelName] = fb.subscribedHostelName
                    freq_hostelss[fb.subscribedHostelName] = 1
                    noh = noh + 1

                else:  # print(feedbacks)
                    freq_hostelss[fb.subscribedHostelName] += 1

            # one loop to calculate sum of 5 fields hostelwise and then take their average
            opis = {}  # [0.00] * len(hostelss)
            cleanliness_av = {}  # [0.00] * len(hostelss)
            breakfast_quality_av = {}  # [0.00] * len(hostelss)
            lunch_quality_av = {}  # [0.00] * len(hostelss)
            dinner_quality_av = {}  # [0.00] * len(hostelss)
            catering_av = {}  # [0.00] * len(hostelss)
            raw_materials_quality = {}  # [0.00] * len(hostelss)

            for hostel in hostelss:
                cleanliness_av[hostel] = 0.0
                breakfast_quality_av[hostel] = 0.0
                lunch_quality_av[hostel] = 0.0
                dinner_quality_av[hostel] = 0.0
                catering_av[hostel] = 0.0
                raw_materials_quality[hostel] = 0.0

            # Calculating sum of feedback
            for fb in feedbacks:
                cleanliness_av[fb.subscribedHostelName] += fb.cleanliness_hygiene
                print(cleanliness_av)
                breakfast_quality_av[fb.subscribedHostelName] += fb.qual_breakfast
                lunch_quality_av[fb.subscribedHostelName] += fb.qual_lunch
                dinner_quality_av[fb.subscribedHostelName] += fb.qual_dinner
                catering_av[fb.subscribedHostelName] += fb.catering_punctuality

            # Calculating average of Feedback
            for hostel in hostelss:
                cleanliness_av[hostel] = cleanliness_av[hostel] / freq_hostelss[hostel]
                breakfast_quality_av[hostel] = breakfast_quality_av[hostel] / freq_hostelss[hostel]
                lunch_quality_av[hostel] = lunch_quality_av[hostel] / freq_hostelss[hostel]
                dinner_quality_av[hostel] = dinner_quality_av[hostel] / freq_hostelss[hostel]
                catering_av[hostel] = catering_av[hostel] / freq_hostelss[hostel]
                opis[hostel] = (2 * cleanliness_av[hostel] + 1 * catering_av[hostel] + 3 * breakfast_quality_av[
                    hostel] + 3 * lunch_quality_av[hostel] + 3 * dinner_quality_av[hostel] + 2 * raw_materials_quality[
                                    hostel]) / 14

            print('OPIs', opis)
            for hostel in hostelss:
                print('inside the opi calcutation loop')
                if len(Opi_calculated.objects.filter(hostelName=hostel, month=opi_month, year=opi_year)) == 0:
                    opi_object = Opi_calculated(hostelName=hostel)
                    opi_object.opi_value = round(opis[hostel], 2)
                    opi_object.numberOfFeedback = freq_hostelss[hostel]
                    # opi_object.numberOfSubscriptions = round(freq_hostelss[hostel], 2)
                    opi_object.cleanliness_av = round(cleanliness_av[hostel], 2)
                    opi_object.breakfast_quality_av = round(breakfast_quality_av[hostel], 2)
                    opi_object.lunch_quality_av = round(lunch_quality_av[hostel], 2)
                    opi_object.dinner_quality_av = round(dinner_quality_av[hostel], 2)
                    opi_object.catering_av = round(catering_av[hostel], 2)
                    opi_object.raw_materials_quality = round(raw_materials_quality[hostel], 2)
                    print('opi_object inside if ', opi_object)
                    print('hostelName ', hostel, opis[hostel], opi_object.cleanliness_av)
                    opi_object.save()
                else:
                    opi_object = Opi_calculated.objects.filter(hostelName=hostel, month=opi_month, year=opi_year)[0]
                    Opi_calculated.objects.filter(hostelName=hostel, month=opi_month, year=opi_year).delete()
                    # opi_object.opi_value = round(opis[hostel], 2)
                    opi_object.numberOfFeedback = freq_hostelss[hostel]
                    # opi_object.numberOfSubscriptions = round(freq_hostelss[hostel], 2)
                    opi_object.cleanliness_av = round(cleanliness_av[hostel], 2)
                    opi_object.breakfast_quality_av = round(breakfast_quality_av[hostel], 2)
                    opi_object.lunch_quality_av = round(lunch_quality_av[hostel], 2)
                    opi_object.dinner_quality_av = round(dinner_quality_av[hostel], 2)
                    opi_object.catering_av = round(catering_av[hostel], 2)

                    opi_object.raw_materials_quality = opi_object.raw_materials_quality

                    opi_object.opi_value = (2 * cleanliness_av[hostel] + 1 * catering_av[hostel] + 3 *
                                            breakfast_quality_av[hostel] + 3 * lunch_quality_av[hostel] + 3 *
                                            dinner_quality_av[hostel] + 2 * opi_object.raw_materials_quality) / 14
                    print('opi_object inside else ', opi_object)
                    print(' ELSE ', hostel, opis[hostel], opi_object.cleanliness_av)
                    opi_object.save()
                    print('opi_saved')
            print('Opi Calculated')

            data = Opi_calculated.objects.filter(month=opi_month, year=opi_year)
            data1 = Opi_calculated.objects.filter(month=m1, year=y1)

            return render(request, 'hab_app/mess_opi.html', {'data': data, 'data1': data1})

    else:
        form = LoginForm()
        return render(request, 'student_portal/login.html', {'message': 5, 'form': form})


# @login_required(login_url='/hab_portal/cms_login/')
@login_required(login_url='/hab_portal/temp_login/')
def mess_automation(request):
    if request.session['student'] == "no":
        mess_list = list()
        one_month = datetime.today().date() + relativedelta(months=+1)
        month_no = datetime.now().month

        if month_no == 12:
            month_1 = calendar.month_name[1]
        else:
            month_1 = calendar.month_name[month_no + 1]
        month_2 = calendar.month_name[month_no]
        if month_no == 1:
            month_3 = calendar.month_name[12]
        else:
            month_3 = calendar.month_name[month_no - 1]
        if month_no == 1:
            month_4 = calendar.month_name[11]
        elif month_no == 2:
            month_4 = calendar.month_name[12]
        else:
            month_4 = calendar.month_name[month_no - 2]
        if month_no == 1:
            month_5 = calendar.month_name[10]
        elif month_no == 2:
            month_5 = calendar.month_name[11]
        elif month_no == 3:
            month_5 = calendar.month_name[12]
        else:
            month_5 = calendar.month_name[month_no - 3]

        if request.method == 'GET':
            if HostelMessVacancies.objects.filter(month=month_1).exists():
                for obj in HostelMessVacancies.objects.filter(month=month_1).order_by('hostelName'):
                    mess_list.append(obj)
            else:
                for i in AllHostelMetaData.objects.all().order_by('hostelName'):
                    obj = HostelMessVacancies.objects.create()
                    obj.month = month_1
                    temp = i.hostelRoomOccupant
                    mymodel = apps.get_model(app_label='hab_app', model_name=temp)
                    # if DebarredStudents.objects.filter(webmail=request.user.username,debarred_hostel=mymodel.hostelName or , start_date__lte=one_month, end_date__gte=one_month ).exists():
                    obj.hostel_strengh = mymodel.objects.all().count()
                    obj.hostelName = i.hostelName
                    list_1 = HostelMessVacancies.objects.get_or_create(hostelName=i.hostelName, month=month_2)[0]
                    list_2 = HostelMessVacancies.objects.get_or_create(hostelName=i.hostelName, month=month_3)[0]
                    list_3 = HostelMessVacancies.objects.get_or_create(hostelName=i.hostelName, month=month_4)[0]
                    obj.occupied_history_1 = list_1.occupied
                    obj.occupied_history_2 = list_2.occupied
                    obj.occupied_history_3 = list_3.occupied
                    obj.save()
                    mess_list.append(obj)
                # if HostelMessVacancies.objects.filter(month=month_5).exists():
                #     HostelMessVacancies.objects.filter(month=month_5).delete()
                HostelMessVacancies.objects.create(hostelName="NA", month=month_1)
                HostelMessVacancies.objects.get_or_create(hostelName="NA", month=month_2)
                HostelMessVacancies.objects.get_or_create(hostelName="NA", month=month_3)
                HostelMessVacancies.objects.get_or_create(hostelName="NA", month=month_4)
            # ---------------------------------------------------------------------------------------------------------
            objects_all = Automation.objects.all().order_by('-year')
            # param is button name see automation.html
            if request.GET.get('param2'):
                mth_yr = request.GET.get('param2')
                mth = mth_yr.split('_')
                month = int(mth[0])
                year = int(mth[1])
                log = Automation.objects.get(month=month, year=year)
                form = MessAutomationForm(instance=log)
                return render(request, 'hab_app/automation_new_entry.html',
                              {'form': form, 'objects': objects_all})
            if request.GET.get('param3'):
                mth_yr = request.GET.get('param3')
                mth = mth_yr.split('_')
                month = int(mth[0])
                year = int(mth[1])
                if len(Automation.objects.filter(month=month, year=year)) > 0:
                    Automation.objects.filter(month=month, year=year).delete()

            form = MessAutomationForm()
            return render(request, 'hab_app/automation.html',
                          {'form': form, 'objects': objects_all, 'mess_list': mess_list,
                           'month1': month_1, 'month2': month_2, 'month3': month_3, 'month4': month_4})

        if request.method == 'POST' and 'btn1' in request.POST:
            form = MessAutomationForm()
            return render(request, 'hab_app/automation_new_entry.html', {'form': form})

        if request.method == 'POST' and 'btn2' in request.POST:
            form = MessAutomationForm(data=request.POST)
            mess_list = HostelMessVacancies.objects.filter(month=month_1).order_by('hostelName')
            if len(Automation.objects.filter(month=request.POST['month'], year=request.POST['year'])) > 0:
                Automation.objects.filter(month=request.POST['month'], year=request.POST['year']).delete()
            if form.is_valid():
                form.save()
                objects_all = Automation.objects.all()
                return render(request, 'hab_app/automation.html',
                              {'form': form, 'objects': objects_all, 'mess_list': mess_list,
                               'month1': month_1, 'month2': month_2, 'month3': month_3, 'month4': month_4})
            else:
                print(form.errors)
        if request.method == 'POST' and 'btn3' in request.POST:
            mess_list = HostelMessVacancies.objects.filter(month=month_1).order_by('hostelName')
            counter = HostelMessVacancies.objects.filter(month=month_1).count()
            objects_all = Automation.objects.all()
            for i in range(1, counter+1):
                mess_list1 = mess_list[i-1]
                mess_list1.upper_limit = request.POST.get(str(i))
                mess_list1.save()
            return render(request, 'hab_app/automation.html',
                          {'objects': objects_all, 'mess_list': mess_list,
                           'month1': month_1, 'month2': month_2, 'month3': month_3, 'month4': month_4, 'msg': 1})

    else:
        form = LoginForm()
        return render(request, 'student_portal/login.html', {'message': 5, 'form': form})


# @login_required(login_url='/hab_portal/cms_login/')
@login_required(login_url='/hab_portal/temp_login/')
def debarred_student(request):
    if request.session['student'] == "no":
        debarred_list = DebarredStudents.objects.all().order_by('-date_created')
        if request.method == 'GET':
            if request.GET.get('param4'):
                temp = request.GET.get('param4')
                [webmail, debarred_hostel] = temp.split('_')
                obj1 = DebarredStudents.objects.get(webmail=webmail, debarred_hostel=debarred_hostel).delete()
                return render(request, 'hab_app/debarredStudents.html',
                              {'debarred_list': debarred_list, 'msg': 'Successfully Deleted'})

            return render(request, 'hab_app/debarredStudents.html',
                          {'debarred_list': debarred_list})

        if request.method == 'POST' and 'btn3'in request.POST:
            queryDict = request.POST
            if OccupantDetails.objects.filter(idNo=queryDict['idNo'], webmail=queryDict['webmail']).exists():
                obj = DebarredStudents.objects.create(
                    name=queryDict['name'], idType=queryDict['idType'], idNo=queryDict['idNo'],
                    webmail=queryDict['webmail'], debarred_hostel=queryDict['debarred'], start_date=queryDict['start_date'],
                    end_date=queryDict['end_date'], reasons=queryDict['reasons'])

                return render(request, 'hab_app/debarredStudents.html',
                              {'debarred_list': debarred_list})
            else:
                return render(request, 'hab_app/debarredStudents.html',
                              {'debarred_list': debarred_list, 'err_msg': 'Student with the following details does not exist in Database'})
    else:
        form = LoginForm()
        return render(request, 'student_portal/login.html', {'message': 5, 'form': form})


# @login_required(login_url='/hab_portal/cms_login/')
@login_required(login_url='/hab_portal/temp_login/')
def search_student(request):
    if request.session['student'] == "no":
        if request.session['username'] == "chr_hab":
            if request.GET.get('param') and request.method == "GET":
                occupantId = request.GET.get('param')
                string = ""
                for i in AllHostelMetaData.objects.all():
                    temp = i.hostelRoomOccupant
                    mymodel = apps.get_model(app_label='hab_app', model_name=temp)
                    if mymodel.objects.filter(occupantId=occupantId).exists():
                        string = i.hostelCTid
                        break

                ROtable = AllHostelMetaData.objects.get(hostelCTid=string)
                temp = ROtable.hostelRoomOccupant
                mymodel = apps.get_model(app_label='hab_app', model_name=temp)
                room_model = apps.get_model(app_label='hab_app', model_name=ROtable.hostelRoom)
                form1 = HostelRoomOccupantRelationForm(instance=mymodel.objects.get(occupantId=occupantId))
                form2 = OccupantDetailsEditForm(instance=OccupantDetails.objects.get(idNo=occupantId))
                return render(request, 'hab_app/temp2_chr.html', {'ROtable': ROtable, 'form1': form1, 'form2': form2})

            if request.GET.get('param1') and request.method == "GET":
                occupantId = request.GET.get('param1')
                details = OccupantDetails.objects.get(idNo=occupantId)
                string = ""
                for i in AllHostelMetaData.objects.all():
                    temp = i.hostelRoomOccupant
                    mymodel = apps.get_model(app_label='hab_app', model_name=temp)
                    if mymodel.objects.filter(occupantId=occupantId).exists():
                        string = i.hostelCTid
                        break

                ROtable = AllHostelMetaData.objects.get(hostelCTid=string)
                temp = ROtable.hostelRoomOccupant
                mymodel = apps.get_model(app_label='hab_app', model_name=temp)
                roDetails = mymodel.objects.filter(occupantId=occupantId)[0]
                return render(request, 'hab_app/showDetails_chr.html', {'details': details, 'roDetails':roDetails})

            if request.method == "GET":
                return render(request, 'hab_app/search_student.html')

            if request.method == "POST" and 'btn1' in request.POST:
                try:
                    student_list = list()
                    if request.POST.get('name') != "":
                        for i in OccupantDetails.objects.all():
                            name = i.name
                            m = SequenceMatcher(None, request.POST.get('name').lower(), name.lower())
                            if request.POST.get('name').lower() in name.lower():
                                student_list.append(i)
                            elif m.ratio() > 0.70:
                                student_list.append(i)

                    elif request.POST.get('idNo') != "":
                        student_list = OccupantDetails.objects.filter(idNo__iexact=request.POST.get('idNo'))

                    elif request.POST.get('webmail') != "":
                        for i in OccupantDetails.objects.all():
                            webmail = i.webmail
                            m = SequenceMatcher(None, request.POST.get('webmail').lower(), webmail.lower())
                            if request.POST.get('webmail').lower() in webmail.lower():
                                student_list.append(i)
                            elif m.ratio() > 0.70:
                                student_list.append(i)

                    return render(request, 'hab_app/search_student.html', {'student': student_list})

                except Exception as ex:
                    print(ex)
                    return render(request, 'hab_app/search_student.html')

            if request.method == 'POST':
                occupantId = request.POST.get('occupantId')
                string = ""
                for i in AllHostelMetaData.objects.all():
                    temp = i.hostelRoomOccupant
                    mymodel = apps.get_model(app_label='hab_app', model_name=temp)
                    if mymodel.objects.filter(occupantId=occupantId).count() != 0:
                        string = i.hostelCTid
                        break

                ROtable = AllHostelMetaData.objects.get(hostelCTid=string)
                temp = ROtable.hostelRoomOccupant
                mymodel = apps.get_model(app_label='hab_app', model_name=temp)
                room_model = apps.get_model(app_label='hab_app', model_name=ROtable.hostelRoom)

                # instance1 = get_object_or_404(mymodel,occupantId=request.POST.get('occupantId'))
                instance2 = get_object_or_404(OccupantDetails, idNo=request.POST.get('occupantId'))
                form1 = HostelRoomOccupantRelationForm(request.POST)
                form2 = OccupantDetailsForm(request.POST, request.FILES, instance=instance2)

                if form2.is_valid():
                    occupant = form2.save(commit=False)
                    if form2.data['New_OccupantId']:
                        occupant.idNo = request.POST.get('New_OccupantId')
                        if OccupantDetails.objects.filter(idNo=request.POST.get('occupantId')).exists():
                            OccupantDetails.objects.filter(idNo=request.POST.get('occupantId')).delete()
                    occupant.save()

                else:
                    return HttpResponse("Form Invalid 2")

                if form1.is_valid():
                    occupant = form1.save(commit=False)
                    if form2.data['New_OccupantId']:

                        p = mymodel(occupantId=OccupantDetails.objects.get(idNo=request.POST.get('New_OccupantId')))
                        p.hostelName = ROtable.hostelName
                        p.roomNo = get_object_or_404(room_model, roomNo=request.POST.get('roomNo'))
                        p.messStatus = occupant.messStatus
                        # p.toMess = occupant.toMess
                        # p.fromMess = occupant.fromMess
                        p.toRoomStay = occupant.toRoomStay
                        p.fromRoomStay = occupant.fromRoomStay
                        p.comment = occupant.comment
                        p.save()
                    else:
                        p = mymodel.objects.get(occupantId=request.POST.get('occupantId'))
                        p.hostelName = ROtable.hostelName
                        p.roomNo = get_object_or_404(room_model, roomNo=request.POST.get('roomNo'))
                        p.messStatus = occupant.messStatus
                        # p.toMess = occupant.toMess
                        # p.fromMess = occupant.fromMess
                        p.toRoomStay = occupant.toRoomStay
                        p.fromRoomStay = occupant.fromRoomStay
                        p.comment = occupant.comment
                        p.save()
                else:
                    return HttpResponse("Form Invalid")

                if form2.data['New_OccupantId']:
                    student = OccupantDetails.objects.filter(idNo=request.POST.get('New_OccupantId'))
                else:
                    student = OccupantDetails.objects.filter(idNo=request.POST.get('occupantId'))
                return render(request, 'hab_app/search_student.html', {'student': student})

    else:
        form = LoginForm()
        return render(request, 'student_portal/login.html', {'message': 5, 'form': form})


# @login_required(login_url='/hab_portal/cms_login/')
@login_required(login_url='/hab_portal/temp_login/')
def inventory_management(request):
    if request.session['student'] == "no":
        list_1 = InventoryItemsLocation.objects.all().order_by('sub_category')
        return render(request, 'hab_app/inventory_management_home.html', {'list': list_1})
    else:
        form = LoginForm()
        return render(request, 'student_portal/login.html', {'message': 5, 'form': form})


# @login_required(login_url='/hab_portal/cms_login/')
@login_required(login_url='/hab_portal/temp_login/')
def inventory_details(request, category, sub_category):
    if request.session['student'] == "no":
        if request.session['username'] == "chr_hab":
            if request.method == 'GET' and category == "All" and sub_category == "All":
                item_list = InventoryItems.objects.all().order_by('-purchase_date')
                return render(request, 'hab_app/inventory_management_details.html', {'item_list': item_list, 'subcategory': sub_category, 'category': category})

            if request.method == 'GET' and category != "All" and sub_category == "All":
                item_list = InventoryItems.objects.filter(alloted_location_category=category).order_by('-purchase_date')
                return render(request, 'hab_app/inventory_management_details.html', {'item_list': item_list, 'subcategory': sub_category, 'category': category})

            if request.method == 'GET':
                item_list = InventoryItems.objects.filter(alloted_location_category=category, alloted_location_subcategory=sub_category).order_by('-purchase_date')
                return render(request, 'hab_app/inventory_management_details.html', {'item_list': item_list, 'subcategory': sub_category, 'category': category})

            if request.method == 'POST' and 'btn1' in request.POST:
                form = AddInventoryForm()
                return render(request, 'hab_app/add_inventory_details.html', {'form': form})

            if request.method == 'POST' and 'btn2' in request.POST:
                form = AddInventoryForm(data=request.POST)
                if form.is_valid():
                    item = form.save()
                    item.save()
                    obj = get_object_or_404(InventoryItems, purchase_order_no=form.cleaned_data['purchase_order_no'])
                    obj.alloted_location_category = category
                    obj.alloted_location_subcategory = sub_category
                    obj.save()
                    item_list = InventoryItems.objects.filter(alloted_location_category=category, alloted_location_subcategory=sub_category).order_by('-purchase_date')
                    return render(request, 'hab_app/inventory_management_details.html', {'item_list': item_list, 'subcategory': sub_category, 'category': category})
                else:
                    print(form.errors)
                    return HttpResponse("Form invalid")

        if AllHostelMetaData.objects.filter(hostelCTid=request.user.username).exists():
            user = get_object_or_404(AllHostelMetaData, hostelCTid=request.user.username)
            if request.method == 'GET':
                item_list = InventoryItems.objects.filter(alloted_location_category=category, alloted_location_subcategory=user.hostelName ).order_by('-purchase_date')
                return render(request, 'hab_app/ct_inventory_details.html', {'item_list': item_list})

            if request.method == 'POST' and 'btn1' in request.POST:
                form = AddInventoryForm()
                return render(request, 'hab_app/ct_add_inventory_details.html', {'form': form})

            if request.method == 'POST' and 'btn2' in request.POST:
                form = AddInventoryForm(data=request.POST)
                if form.is_valid():
                    item = form.save()
                    item.save()
                    obj = get_object_or_404(InventoryItems, purchase_order_no=form.cleaned_data['purchase_order_no'])
                    obj.alloted_location_category = category
                    obj.alloted_location_subcategory = user.hostelName
                    obj.save()
                    item_list = InventoryItems.objects.filter(alloted_location_category=category, alloted_location_subcategory=user.hostelName).order_by('-purchase_date')
                    return render(request, 'hab_app/ct_inventory_details.html', {'item_list': item_list})
                else:
                    print(form.errors)
                    return HttpResponse("Invalid Form")

    else:
        form = LoginForm()
        return render(request, 'student_portal/login.html', {'message': 5, 'form': form})


def inventory_full_details(request):
    if request.session['student'] == "no":
        if request.method == 'GET' and 'param' in request.GET:
            parameter = request.GET.get('param')
            item = get_object_or_404(InventoryItems, purchase_order_no=parameter)
            if request.user.username == "chr_hab":
                return render(request, 'hab_app/inventory_fullDetails.html', {'item': item})
            else:
                return render(request, 'hab_app/ct_inventory_fullDetails.html', {'item': item})

        if request.method == 'GET' and 'param2' in request.GET:
            parameter = request.GET.get('param2')
            item = get_object_or_404(InventoryItems, purchase_order_no=parameter)
            category = item.alloted_location_category
            sub_category = item.alloted_location_subcategory
            item.delete()
            item_list = InventoryItems.objects.filter(alloted_location_category=category, alloted_location_subcategory=sub_category).order_by('-purchase_date')
            if request.user.username == "chr_hab":
                return render(request, 'hab_app/inventory_management_details.html', {'item_list': item_list})
            else:
                return render(request, 'hab_app/ct_inventory_details.html', {'item_list': item_list})

        if request.method == 'GET' and 'param3' in request.GET:
            parameter = request.GET.get('param3')
            item = get_object_or_404(InventoryItems, purchase_order_no=parameter)
            form = AddInventoryForm(instance=item)
            if request.user.username == "chr_hab":
                return render(request, 'hab_app/add_inventory_details.html',
                          {'form': form})
            else:
                return render(request, 'hab_app/ct_add_inventory_details.html',
                              {'form': form})

        if request.method == 'GET' and 'param4' in request.GET:
            parameter = request.GET.get('param4')
            item = get_object_or_404(InventoryItems, purchase_order_no=parameter)
            if InventoryDamagedItems.objects.filter(purchase_order_no=parameter).count() == 0:
                obj = InventoryDamagedItems.objects.create(purchase_order_no=parameter)
            else:
                obj = InventoryDamagedItems.objects.filter(purchase_order_no=parameter)[0]
                InventoryDamagedItems.objects.create(purchase_order_no=parameter)

            return render(request, 'hab_app/ct_add_damaged_inventory.html', {'item':item, 'obj': obj})

        if request.method == 'POST' and 'btn2' in request.POST:
            form = AddInventoryForm(data=request.POST)
            obj1 = get_object_or_404(InventoryItems, purchase_order_no=request.POST['purchase_order_no'])
            category = obj1.alloted_location_category
            sub_category = obj1.alloted_location_subcategory
            temp = obj1
            obj1.delete()
            if form.is_valid():
                item = form.save()
                item.save()
                obj = get_object_or_404(InventoryItems, purchase_order_no=form.cleaned_data['purchase_order_no'])
                obj.alloted_location_category = category
                obj.alloted_location_subcategory = sub_category
                obj.save()
                if request.user.username == "chr_hab":
                    return render(request, 'hab_app/inventory_fullDetails.html', {'item': obj})
                else:
                    return render(request, 'hab_app/ct_inventory_fullDetails.html', {'item': obj})
            else:
                temp1 = InventoryItems()
                temp1 = temp
                temp1.save()
                print(form.errors)
                return HttpResponse("Invalid Form")

        if request.method == 'POST' and 'btn3' in request.POST:
            purchase_order_no = request.POST.get('purchase_order_no')
            if InventoryDamagedItems.objects.filter(purchase_order_no=purchase_order_no).count() == 1:
                damaged_item = get_object_or_404(InventoryDamagedItems, purchase_order_no=purchase_order_no)
                damaged_item.damaged_item_quantity = request.POST.get('damaged_item_quantity')
                damaged_item.comments_on_damage = request.POST.get('reasons')
                damaged_item.item_name = request.POST.get('item_name')
                damaged_item.total_damage_quantity = damaged_item.total_damage_quantity + int(request.POST.get('damaged_item_quantity'))
                damaged_item.save()

            else:
                damaged_item_list = InventoryDamagedItems.objects.filter(purchase_order_no=purchase_order_no).order_by('-id')
                damaged_item = damaged_item_list[0]
                temp = damaged_item_list[1]
                damaged_item.damaged_item_quantity = request.POST.get('damaged_item_quantity')
                damaged_item.comments_on_damage = request.POST.get('reasons')
                damaged_item.item_name = request.POST.get('item_name')
                damaged_item.total_damage_quantity = damaged_item.total_damage_quantity + int(request.POST.get('damaged_item_quantity')) + temp.total_damage_quantity
                damaged_item.save()
                for i in damaged_item_list:
                    i.total_damage_quantity = damaged_item.total_damage_quantity
                    i.save()

            item = get_object_or_404(InventoryItems, purchase_order_no=purchase_order_no)
            item_list = InventoryItems.objects.filter(alloted_location_category=item.alloted_location_category, alloted_location_subcategory=item.alloted_location_subcategory)
            return render(request, 'hab_app/ct_inventory_details.html', {'item_list': item_list})

    else:
        form = LoginForm()
        return render(request, 'student_portal/login.html', {'message': 5, 'form': form})


# @login_required(login_url='/hab_portal/cms_login/')
@login_required(login_url='/hab_portal/temp_login/')
def damaged_inventory_details(request, category, sub_category):
    if request.session['student'] == "no":
        if request.method == 'GET' and 'param' in request.GET:
            parameter = request.GET.get('param')
            damaged_item = InventoryDamagedItems.objects.get(pk=parameter)
            damaged_item_list_1 = InventoryDamagedItems.objects.filter(purchase_order_no=damaged_item.purchase_order_no)
            for i in damaged_item_list_1:
                i.total_damage_quantity = i.total_damage_quantity - damaged_item.damaged_item_quantity
                i.save()
            damaged_item.delete()

        if request.method == 'GET' and category == "All" and sub_category == "All":
            item_list = InventoryItems.objects.all()
            damaged_item_list = list()
            for i in InventoryDamagedItems.objects.all().order_by('-date'):
                if item_list.filter(purchase_order_no=i.purchase_order_no).exists():
                    damaged_item_list.append(i)
            return render(request, 'hab_app/inventory_management_damage_details.html',
                          {'item_list': damaged_item_list, 'subcategory': sub_category, 'category': category})

        if request.method == 'GET' and category != "All" and sub_category == "All":
            item_list = InventoryItems.objects.filter(alloted_location_category=category)
            damaged_item_list = list()
            for i in InventoryDamagedItems.objects.all().order_by('-date'):
                if item_list.filter(purchase_order_no=i.purchase_order_no).exists():
                    damaged_item_list.append(i)
            return render(request, 'hab_app/inventory_management_damage_details.html',
                          {'item_list': damaged_item_list, 'subcategory': sub_category, 'category': category})

        if request.method == 'GET':
            item_list = InventoryItems.objects.filter(alloted_location_category=category, alloted_location_subcategory=sub_category)
            damaged_item_list = list()
            for i in InventoryDamagedItems.objects.all().order_by('-date'):
                if item_list.filter(purchase_order_no=i.purchase_order_no).exists():
                    damaged_item_list.append(i)
            return render(request, 'hab_app/inventory_management_damage_details.html',
                          {'item_list': damaged_item_list, 'subcategory': sub_category, 'category': category})
    else:
        form = LoginForm()
        return render(request, 'student_portal/login.html', {'message': 5, 'form': form})


# @login_required(login_url='/hab_portal/cms_login/')
@login_required(login_url='/hab_portal/temp_login/')
def import_export_files(request):
    if request.session['student'] == "no":
        if request.method == 'GET':
            text = ''
            form = MessImportExportFilesForm
            return render(request, 'hab_app/import_export_files.html', {'form': form, 'text': text})

        queryDict = request.POST

        all_hostel_check_flag = 0

        try:
            if queryDict['hostelName'] == 'All Hostels':
                all_hostel_check_flag = 1

            if all_hostel_check_flag == 0:
                queryset_feedback = MessFeedback.objects.filter(subscribedHostelName=queryDict['hostelName'],
                                                                month=queryDict['month'], year=queryDict['year'])
                queryset_preference = Preference.objects.filter(hostelName=queryDict['hostelName'],
                                                                month=queryDict['month'], year=queryDict['year'])
                queryset_final_preference = FinalPreference.objects.filter(hostelName=queryDict['hostelName'],
                                                                month=queryDict['month'], year=queryDict['year'])
            else:
                queryset_feedback = MessFeedback.objects.filter(month=queryDict['month'], year=queryDict['year'])
                queryset_preference = Preference.objects.filter(month=queryDict['month'], year=queryDict['year'])
                queryset_final_preference = FinalPreference.objects.filter(month=queryDict['month'],
                                                                           year=queryDict['year'])
        except:
            pass

        # print(queryset)

        if request.method == 'POST' and 'btn_feedback_csv' in request.POST:
            messfeedback_resource = MessFeedbackResource()
            dataset = messfeedback_resource.export(queryset_feedback)
            response = HttpResponse(dataset.csv, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="mess_feedbacks.csv"'
            return response

        if request.method == 'POST' and 'btn_feedback_xls' in request.POST:
            messfeedback_resource = MessFeedbackResource()
            dataset = messfeedback_resource.export(queryset_feedback)
            response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="mess_feedbacks.xls"'
            return response

        if request.method == 'POST' and 'btn_preference_csv' in request.POST:
            preference_resource = PreferenceResource()
            dataset = preference_resource.export(queryset_preference)
            response = HttpResponse(dataset.csv, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="mess_preferences.csv"'
            return response

        if request.method == 'POST' and 'btn_preference_xls' in request.POST:
            preference_resource = PreferenceResource()
            dataset = preference_resource.export(queryset_preference)
            response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="mess_preferences.xls"'
            return response

        if request.method == 'POST' and 'btn_mess_csv' in request.POST:
            final_preference_resource = FinalPreferenceResource()
            dataset = final_preference_resource.export(queryset_final_preference)
            response = HttpResponse(dataset.csv, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="mess_alloted_list.csv"'
            return response

        if request.method == 'POST' and 'btn_mess_xls' in request.POST:
            final_preference_resource = FinalPreferenceResource()
            dataset = final_preference_resource.export(queryset_final_preference)
            response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="mess_alloted_list.xls"'
            return response

        # imorting files as csv
        # PREFERENCE
        if request.method == 'POST' and 'btn5' in request.POST:
            # print(request.POST.get('month_val'))
            pref_month_val = request.POST.get('month_val')
            pref_year_val = request.POST.get('year_val')
            # print(pref_year_val)
            form = MessImportExportFilesForm
            final_preference_resource = FinalPreferenceResource()
            dataset = Dataset()
            file_name = request.FILES['myfile']
            # print (file_name)
            if '.csv' not in str(file_name):
                error = ' Line no 1011, Please Upload a csv File !'
                return render(request, 'hab_app/import_export_files.html',
                              {'form': form, 'text': error, 'text_type': str(type(error).__name__)})

            try:

                error_dic = {}  # line no  : error  : no of fileds , valid hostel name
                # imported_data = dataset.load(file_name.read().decode('utf-8'))
                decoded_data = file_name.read().decode('utf-8')
                # loaded_data = dataset.load(decoded_data)   #this will load the data in a table
                splited_data = decoded_data.split()  # this will make the list of the data
                print(len(splited_data))
                # print("\n".join(splited_data))
                print(splited_data)
                # print(loaded_data)
                for i in range(1, len(splited_data)):
                    # print(splited_data[i])
                    # print(splited_data[i].count(",")+1)
                    if splited_data[i].count(",") + 1 < 3:
                        error_dic[str('line no.' + str(
                            i + 1) + ': error  :')] = 'FIELDS MISSING ! PLEASE CHECK THE LINE NO. AND FILL THE CORRECT DETAILS'
                    if splited_data[i].count(",") + 1 > 3:
                        error_dic[str('line no.' + str(
                            i + 1) + ': error  :')] = 'FIELDS EXCEED THAN USUAL NUMBER ! PLEASE CHECK THE LINE NO. AND MAKE REQUIRED CHANGES'
                    if splited_data[i].count(",") + 1 == 3:
                        line_content_array = splited_data[i].split(",")
                        print(line_content_array)
                        if len(line_content_array[1]) == 0:
                            error_dic[str('line no.' + str(
                                i + 1) + ':  empty username error  :')] = 'USERNAME FIELD NOT ENTERED! PLEASE ENTER CORRECT NAME IN THE GIVEN LINE'
                        if (line_content_array[0], line_content_array[0]) not in HOSTEL_CHOICES:
                            error_dic[str('line no.' + str(
                                i + 1) + ':  base hostel error  :')] = 'HOSTEL NAME DOES NOT MATCH! PLEASE ENTER CORRECT NAME IN THE GIVEN LINE'
                        if (line_content_array[-1], line_content_array[-1]) not in HOSTEL_CHOICES:
                            error_dic[str('line no.' + str(
                                i + 1) + ': error  :')] = 'HOSTEL NAME DOES NOT MATCH! PLEASE ENTER CORRECT NAME IN THE GIVEN LINE'

                    splited_data[i] = splited_data[i] + ',' + str(pref_month_val) + ',' + str(pref_year_val)

                splited_data[0] = splited_data[0] + ',' + 'month' + ',' + 'year'
                print(splited_data)
                print('yay')
                decoded_data = "\n".join(splited_data)
                loaded_data = dataset.load(decoded_data)
                print(decoded_data)
                # print(error_dic)
                if error_dic:  # check for non empty dictionary
                    return render(request, 'hab_app/import_export_files.html',
                                  {'form': form, 'text': sorted(error_dic.items()),
                                   'text_type': str(type(error_dic).__name__)})

                else:
                    # print(splited_data)

                    result = final_preference_resource.import_data(dataset, dry_run=True)
                    # print(result)
                    # if True:

                    if not result.has_errors():
                        success_message = 'The file was successfully loaded !'
                        final_preference_resource.import_data(dataset, dry_run=False)
                        # messages.success(request, 'Changes are saved!!')
                        # form = MessImportExportFilesForm
                        return render(request, 'hab_app/import_export_files.html',
                                      {'form': form, 'text': success_message,
                                       'text_type': str(type(success_message).__name__)})

                    else:
                        error = ' File Not readable, Please upload valid csv file!'
                        return render(request, 'hab_app/import_export_files.html',
                                      {'form': form, 'text': text, 'text_type': str(type(error).__name__)})

                print(imported_data)
                print('imported_data')
                # error_dic is empty
                # if no error

                # insert into database each row
                # if error :
                # return render(request, 'hab_app/import_export_files.html',{'form':from, 'text': error})
            except:
                error = ' File Not readable, Please upload valid csv file!'
                # form = MessImportExportFilesForm
                return render(request, 'hab_app/import_export_files.html', {'form': form, 'text': error})

        if request.method == 'POST' and 'btn6' in request.POST:
            queryset = FinalPreference.objects.filter(hostelName='')
            preference_resource = FinalPreferenceResource()
            dataset = preference_resource.export(queryset)
            response = HttpResponse(dataset.csv, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="mess_finalpreferences_sample.csv"'
            return response

            # queryset = FinalPreference.objects.filter(hostelName='')
            # preference_resource = FinalPreferenceResource()
            # dataset = preference_resource.export(queryset)
            # response = HttpResponse(dataset.csv, content_type='text/csv')
            # response['Content-Disposition'] = 'attachment; filename="mess_finalpreferences_sample.csv"'
            # return response
    else:
        form = LoginForm()
        return render(request, 'student_portal/login.html', {'message': 5, 'form': form})
