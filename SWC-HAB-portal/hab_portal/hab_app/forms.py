from django import forms
from django.contrib.auth.models import User
from hab_app.models import *
from django.apps import apps
from django.utils.translation import gettext_lazy as _
from django.forms import ModelChoiceField


class UpcomingOccupantForm(forms.ModelForm):
    required_css_class = 'required'
    toStay = forms.DateField(widget=forms.DateInput(format='%m/%d/%Y'), input_formats=('%m/%d/%Y',),
                             label='End Date Of Stay')
    fromStay = forms.DateField(widget=forms.DateInput(format='%m/%d/%Y'), input_formats=('%m/%d/%Y',),
                               label='Start Date Of Stay')

    class Meta():
        model = UpcomingOccupant
        fields = ('occupantName', 'idType', 'occupantId', 'hostelName', 'roomNo', 'fromStay', 'toStay', 'comments')


class UpcomingOccupantRequestForm(forms.ModelForm):
    required_css_class = 'required'
    photo = forms.ImageField(label='Photo', required=False)
    idPhoto = forms.ImageField(label='Id Photo', required=False)
    To_Date = forms.DateField(widget=forms.DateInput(format='%m/%d/%Y'), input_formats=('%m/%d/%Y',),
                              label='End Date Of Stay')
    From_Date = forms.DateField(widget=forms.DateInput(format='%m/%d/%Y'), input_formats=('%m/%d/%Y',),
                                label='Start Date Of Stay')

    class Meta():
        model = UpcomingOccupantRequest
        exclude = ('isApprovedChr', 'hostelName', 'comments',)


class UpcomingOccupantRequestChrForm(forms.ModelForm):
    required_css_class = 'required'
    photo = forms.ImageField(label='Photo', required=False)
    idPhoto = forms.ImageField(label='Id Photo', required=False)
    To_Date = forms.DateField(widget=forms.DateInput(format='%m/%d/%Y'), input_formats=('%m/%d/%Y',),
                              label='End Date Of Stay')
    From_Date = forms.DateField(widget=forms.DateInput(format='%m/%d/%Y'), input_formats=('%m/%d/%Y',),
                                label='Start Date Of Stay')

    class Meta():
        model = UpcomingOccupantRequest
        exclude = ('isApprovedChr',)


class HostelRoomOccupantRelationForm(forms.ModelForm):
    required_css_class = 'required'
    occupantId = forms.CharField(required=True, max_length=255)
    roomNo = forms.CharField(max_length=255)
    hostelName = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    toRoomStay = forms.DateField(widget=forms.DateInput(format='%m/%d/%Y'), input_formats=('%m/%d/%Y',),
                                 label='End Date Of Stay')
    fromRoomStay = forms.DateField(widget=forms.DateInput(format='%m/%d/%Y'), input_formats=('%m/%d/%Y',),
                                   label='Start Date Of Stay')

    class Meta():
        model = HostelRoomOccupantRelation
        exclude = ('toMess', 'fromMess')
        # label = {
        # 'Toroomstay': _('End Date Of Stay'),
        # 'fromRoomStay': _('Start Date Of Stay'),
        # }


class OccupantDetailsForm(forms.ModelForm):
    required_css_class = 'required'
    photo = forms.ImageField(label='Photo', required=False)
    idPhoto = forms.ImageField(label='Id Photo', required=False)

    class Meta():
        model = OccupantDetails
        exclude = ('idNo', 'flag')


class OccupantDetailsEditForm(forms.ModelForm):
    required_css_class = 'required'
    New_OccupantId = forms.CharField(max_length=255, required=False, label='New Occupant Id(in case of change)')
    photo = forms.ImageField(label='Photo', required=False)
    idPhoto = forms.ImageField(label='Id Photo', required=False)

    class Meta():
        model = OccupantDetails
        exclude = ('idNo', 'flag')


class CtApproveStudentEditForm(forms.ModelForm):
    required_css_class = 'required'
    photo = forms.ImageField(label='photo', required=False)
    idPhoto = forms.ImageField(label='idPhoto', required=False)
    idNo = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    idType = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    webmail = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta():
        model = TemporaryDetails
        exclude = ('ct_approval', 'flag', 'created', 'updated')


class AddInventoryForm(forms.ModelForm):
    required_css_class = 'required'
    purchase_date = forms.DateField(widget=forms.DateInput(format='%m/%d/%Y'), input_formats=('%m/%d/%Y',))
    receipt_date = forms.DateField(widget=forms.DateInput(format='%m/%d/%Y'), input_formats=('%m/%d/%Y',), required=False)

    class Meta:
        model = InventoryItems
        exclude = ('alloted_location_category', 'alloted_location_subcategory')


GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
)
STATUS_CHOICES = (
    ('Pending', 'Pending'),
    ('Approved', 'Approved'),
    ('Disapproved', 'Disapproved'),
)
FLOOR_CHOICES = (
    ('Ground Floor', 'Ground Floor'),
    ('First Floor', 'First Floor'),
    ('Second Floor', 'Second Floor'),
    ('Third Floor', 'Third Floor'),
    ('Fourth Floor', 'Fourth Floor'),
)
ROOM_STATUS_CHOICES = (
    ('Usable', 'Usable'),
    ('Abandoned', 'Abandoned'),
    ('Partially Damaged', 'Partially Damaged'),
)

HOSTEL_CHOICES = (
    ('Barak', 'Barak'),
    ('Bramhaputra', 'Bramhaputra'),
    ('Dhansiri', 'Dhansiri'),
    ('Dibang', 'Dibang'),
    ('Dihing', 'Dihing'),
    ('Kameng', 'Kameng'),
    ('Kapili', 'Kapili'),
    ('Lohit', 'Lohit'),
    ('Manas', 'Manas'),
    ('Siang', 'Siang'),
    ('Subansiri', 'Subansiri'),
    ('Umiam', 'Umiam'),
)


##room details edit

class chrRoomDetailsEditForm(forms.Form):
    roomNo = forms.CharField(max_length=255)
    roomOccupancyType = forms.ModelChoiceField(queryset=RoomCategory.objects.all(), empty_label=None)
    floorInfo = forms.ChoiceField(choices=FLOOR_CHOICES)
    roomStatus = forms.ChoiceField(choices=ROOM_STATUS_CHOICES)
    roomOccupancyGender = forms.ChoiceField(choices=GENDER_CHOICES)
    comments = forms.CharField(max_length=255, required=False)


# MESS automation
class MessAutomationForm(forms.ModelForm):
    # jan_fb_start_date = forms.DateField(widget = forms.DateInput(format='%m/%d/%Y',attrs={'class' : 'form-control pull-right'}), input_formats=('%m/%d/%Y',))
    # jan_fb_end_date = forms.DateField(widget = forms.DateInput(format='%m/%d/%Y',attrs={'class' : 'form-control pull-right'}), input_formats=('%m/%d/%Y',))
    # jan_pf_start_date = forms.DateField(widget = forms.DateInput(format='%m/%d/%Y',attrs={'class' : 'form-control pull-right'}), input_formats=('%m/%d/%Y',))
    # jan_pf_end_date = forms.DateField(widget = forms.DateInput(format='%m/%d/%Y',attrs={'class' : 'form-control pull-right'}), input_formats=('%m/%d/%Y',))
    # # january = forms.BooleanField()

    feed_start_date = forms.DateField(widget=forms.DateInput(format='%m/%d/%Y'), input_formats=('%m/%d/%Y',))
    feed_off_date = forms.DateField(widget=forms.DateInput(format='%m/%d/%Y'), input_formats=('%m/%d/%Y',))

    pref_start_date = forms.DateField(widget=forms.DateInput(format='%m/%d/%Y'), input_formats=('%m/%d/%Y',))
    pref_off_date = forms.DateField(widget=forms.DateInput(format='%m/%d/%Y'), input_formats=('%m/%d/%Y',))
    feed_on_off = forms.TypedChoiceField(coerce=lambda x: x == 'True', choices=((True, 'ON'), (False, 'OFF')),
                                         widget=forms.RadioSelect)
    pref_on_off = forms.TypedChoiceField(coerce=lambda x: x == 'True', choices=((True, 'ON'), (False, 'OFF')),
                                         widget=forms.RadioSelect)

    class Meta():
        model = Automation
        exclude = ()

    def clean_date(self):
        jan_fb_start_date = self.cleaned_data['date']
        if jan_fb_start_date < datetime.date.today():
            raise forms.ValidationError("The date cannot be in the past!")
        return date



class MessImportExportFilesForm(forms.ModelForm):
    class Meta():
        model = ImportExportFiles
        exclude = ()
