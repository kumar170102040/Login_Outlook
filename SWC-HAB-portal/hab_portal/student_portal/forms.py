from django import forms
from .models import *

LOGIN_SERVERS = [
    ('202.141.80.9', 'Namboor'),
    ('202.141.80.10', 'Disang'),
    ('202.141.80.11', 'Tamdil'),
    ('202.141.80.12', 'Teesta'),
    ('202.141.80.13', 'Dikrong'),
]
ABILITY_CHOICES =[
    ('Specially/Differently Abled','Specially/Differently Abled'),
    ('No','No'),
]

class LoginForm(forms.Form):
    username = forms.CharField(max_length=254, label='Webmail')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')
    login_server = forms.ChoiceField(choices=LOGIN_SERVERS)

class NewFeedbackForm(forms.ModelForm):
    class Meta:
        model = MessFeedback
        widgets = {
          'comment': forms.Textarea(attrs={'rows':6, 'cols':100}),
        }
        # Add Base Hostel and Subscribed Hostel
        fields  = ['subscribedHostelName' , 'baseHostelName', 'roomNo', 'month', 'year', 'cleanliness_hygiene','qual_breakfast','qual_lunch', 'qual_dinner','catering_punctuality','comment','description', 'document',]

    def save(self, username=None):
        print('Caling save function of NewFeedbackForm')
        feedback_form = super(NewFeedbackForm, self).save(commit=False)
        if username:
            feedback_form.username = username
        print('Username from forms.py:', username)
        feedback_form.save()
        return feedback_form


class NewPreferenceForm(forms.ModelForm):
    class Meta:
        model = Preference
        fields = ['hostelName', 'roomNo','h1','h2','h3','month','year', 'student_id', 'student_name',]
        

    def save(self, username=None):
        preference_form = super(NewPreferenceForm, self).save(commit=False)
        if username:
            preference_form.username = username
        preference_form.save()
        return preference_form

class GenSecFeedbackForm(forms.ModelForm):
    class Meta:
        model = Opi_calculated
        fields = ['raw_materials_quality']


#edit student details

from django.utils.translation import ugettext_lazy as _

from hab_app.models import *
class updateinfoform(forms.ModelForm):
    required_css_class = 'required'
    photo = forms.ImageField(label='Photo' , required=False)
    idPhoto = forms.ImageField(label='Id Photo' , required=False)
    Address = forms.CharField(label='Home Address')
    idNo = forms.CharField(widget = forms.TextInput(attrs={'readonly':'readonly'}))
    idType = forms.CharField(widget = forms.TextInput(attrs={'readonly':'readonly'}))
    emgercencyNo = forms.CharField(label='Emergency No')
    mobNo = forms.CharField(label='Mobile No')
    altEmail = forms.CharField(label='Alternate Email')
    saORda = forms.ChoiceField(label='PWD Status',choices=ABILITY_CHOICES)


    class Meta():
        model = TemporaryDetails
        exclude = ('webmail','flag','ct_approval','comments','created','updated')
