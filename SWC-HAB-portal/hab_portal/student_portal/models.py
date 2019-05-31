from django.db import models
from datetime import datetime
from decimal import Decimal
from django.contrib.auth.models import User

curr_month = datetime.now().month
curr_year = datetime.now().year
m1 = curr_month
y1 = curr_year
m1 = m1 - 1
m1_y1 = ""
if m1 < 1:
    m1 = 12
    y1 = y1 - 1
m1_y1 = str(m1) + '_' + str(y1)

m2 = curr_month
y2 = curr_year
m2 = m2 + 1
m2_y2 = ""
if m2 > 12:
    m2 = 1
    y2 = y2 + 1
m2_y2 = str(m2) + '_' + str(y2)

# Create your models here.

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
    ('NA', 'NA'),
)
# Not final
FEEDBACK_CHOICES = (
    (0, ("Worst")),
    (1, ("Very Poor")),
    (2, ("Poor")),
    (3, ("Average")),
    (4, ("Good")),
    (5, ("Very Good")),
)


class MessFeedback(models.Model):
    subscribedHostelName = models.CharField(max_length=255, choices=HOSTEL_CHOICES)  # Subscribed Hostel
    baseHostelName = models.CharField(max_length=255, choices=HOSTEL_CHOICES, blank=True, default="")
    roomNo = models.CharField(max_length=225, null=True, blank=True, default="")  # Add subscribed Hostel

    # Add Base hostel Room no and Subscribed Hostel

    # hostelName = models.ForeignKey('UpcomingOccupantRequest', on_delete=models.CASCADE)
    # Base_hostel , base_hostel : Room_No, Subscribed Hostel
    username = models.CharField(max_length=255)  # ,null = True,blank= True
    cleanliness_hygiene = models.IntegerField(choices=FEEDBACK_CHOICES, null=True)
    qual_breakfast = models.IntegerField(choices=FEEDBACK_CHOICES, null=True)
    qual_lunch = models.IntegerField(choices=FEEDBACK_CHOICES, null=True)
    qual_dinner = models.IntegerField(choices=FEEDBACK_CHOICES, null=True)
    catering_punctuality = models.IntegerField(choices=FEEDBACK_CHOICES, null=True)
    filled = models.BooleanField(default=False)
    month = models.IntegerField(default=m1)
    year = models.IntegerField(default=y1)
    # month_year = models.CharField(max_length=255,default=m1_y1)
    comment = models.TextField(blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    document = models.FileField(upload_to='documents/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "MessFeedback"
        verbose_name_plural = "MessFeedback"
        unique_together = ('username', 'month', 'year')

    # add month, year (as pk along with username)
    # add further comments field
    def __str__(self):
        return '%s_%s_%s' % (self.username, self.month, self.year)


# numbr of subscribptions
# hostel NAME
# hardcode formula
# month
# year
# username

class Preference(models.Model):
    hostelName = models.CharField(max_length=255, choices=HOSTEL_CHOICES)
    roomNo = models.CharField(max_length=225, null=True, blank=True, default="")
    # Base Hostel Room No
    student_id = models.CharField(max_length=225, null=True, blank=True)
    student_name = models.CharField(max_length=225, null=True, blank=True)
    latest_submission_time = models.DateTimeField(auto_now=True)
    username = models.CharField(max_length=255)
    month = models.IntegerField(default=m2)
    year = models.IntegerField(default=y2)
    # month_year = models.CharField(max_length=255,default=m2_y2)
    h1 = models.CharField(max_length=255, choices=HOSTEL_CHOICES)
    h2 = models.CharField(max_length=255, choices=HOSTEL_CHOICES)
    h3 = models.CharField(max_length=255, choices=HOSTEL_CHOICES)

    class Meta:
        verbose_name = "Preferences"
        verbose_name_plural = "Preferences"
        unique_together = ('username', 'month', 'year')

    def __str__(self):
        return '%s_%s_%s' % (self.username, self.month, self.year)


class FinalPreference(models.Model):
    hostelName = models.CharField(max_length=255, choices=HOSTEL_CHOICES)
    roomNo = models.CharField(max_length=225, null=True, blank=True, default="")
    # Base Hostel Room No
    student_name = models.CharField(max_length=255, null=False, blank=False, default="")
    student_id = models.CharField(max_length=255, null=False, blank=False, default="")
    username = models.CharField(max_length=255, null=False, blank=False, default="")
    month = models.IntegerField()
    year = models.IntegerField()
    final_hostel = models.CharField(max_length=255, choices=HOSTEL_CHOICES)

    class Meta:
        verbose_name = "FinalPreference"
        verbose_name_plural = "FinalPreference"
        unique_together = ('username', 'month', 'year')

    def __str__(self):
        return '%s_%s_%s' % (self.username, self.month, self.year)


class Opi_calculated(models.Model):
    hostelName = models.CharField(max_length=255, choices=HOSTEL_CHOICES)
    opi_value = models.DecimalField(max_digits=20, decimal_places=2)
    numberOfFeedback = models.IntegerField(default=0)
    numberOfSubscriptions = models.IntegerField(default=0)  # actually no of feedback
    month = models.IntegerField(default=m1)
    year = models.IntegerField(default=y1)
    # month_year = models.CharField(max_length=255,default=m1_y1)
    cleanliness_av = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    breakfast_quality_av = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    lunch_quality_av = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    dinner_quality_av = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    catering_av = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    raw_materials_quality = models.IntegerField(choices=FEEDBACK_CHOICES, null=True,
                                                default=0)  # change it  to DecimalField

    class Meta:
        verbose_name = "Opi_calculated"
        verbose_name_plural = "Opi_calculated"
        unique_together = ('hostelName', 'month', 'year')

    def __str__(self):
        return '%s_%s_%s' % (self.hostelName, self.month, self.year)
# createcachetable if db is renewed



