from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from datetime import datetime
import calendar

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
HOSTEL_CHOICES1 = (
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
HOSTEL_CHOICES2 = (
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
    ('All Hostels', 'All Hostels'),
)

ID_CHOICES = (
    ('Rollno', 'Rollno'),
    ('ProjectId', 'ProjectId'),
    ('IITG_Employee Id', 'IITG_Employee Id'),
    ('GovtId_VoterCard', 'GovtId_VoterCard'),
    ('GovtId_PANCard', 'GovtId PANCard'),
    ('GovtID_AadharCard', 'GovtID_AadharCard'),
    ('GovtID_PassportNo', 'GovtID_PassportNo'),
    ('OtherCollegeId', 'OtherCollegeId'),

)

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
TOAPPROVEDBY_CHOICES = (
    ('hodcse', 'hodcse'),
    ('HOSAA', 'HOSAA'),
    ('chr_hab', 'chr_hab'),
)
MESS_CHOICES = (
    ('Subscribed', 'Subscribed'),
    ('Unsubscribed', 'Unsubscribed'),
    ('PayAndEat', 'PayAndEat'),
)
PURPOSE_CHOICES = (
    ('Intern', 'Intern'),
    ('Project', 'Project'),
    ('Unofficial', 'Unofficial'),
)
ROOM_STATUS_CHOICES = (
    ('Usable', 'Usable'),
    ('Abandoned', 'Abandoned'),
    ('Partially Damaged', 'Partially Damaged'),
)
FLOOR_CHOICES = (
    ('Ground Floor', 'Ground Floor'),
    ('First Floor', 'First Floor'),
    ('Second Floor', 'Second Floor'),
    ('Third Floor', 'Third Floor'),
    ('Fourth Floor', 'Fourth Floor'),
)
ABILITY_CHOICES = (
    ('Specially/Differently Abled', 'Specially/Differently Abled'),
    ('No', 'No'),
)

REGISTRATION_STATUS_CHOICES = (
    ('REGISTERED', 'REGISTERED'),
    ('NOT-REGISTERED', 'NOT-REGISTERED'),
    ('NOT-APPLICABLE', 'NOT-APPLICABLE'),
    ('UNKNOWN', 'UNKNOWN'),

)

LOCATION_CHOICE = (
    ('Hostel', 'Hostel'),
    ('Academic Complex', 'Academic Complex'),
    ('Lecture Hall', 'Lecture Hall'),
    ('Sports', 'Sports'),
    ('Auditorium', 'Auditorium'),
    ('Conference Hall', 'Conference Hall'),
    ('New SAC', 'New SAC'),

)

# table with general information regarding all hostels

class AllHostelMetaData(models.Model):
    class Meta:
        verbose_name = "AllHostelMetaData"
        verbose_name_plural = "AllHostelMetaData"

    hostelName = models.CharField(max_length=255, primary_key=True, choices=HOSTEL_CHOICES)
    hostelCode = models.CharField(max_length=255, unique=True)
    # gensec webmail id
    hostelGensec = models.CharField(max_length=255, null=False)
    # caretaker office id
    hostelCTid = models.CharField(max_length=255, unique=True)
    # hostel rooms table name
    hostelRoom = models.CharField(max_length=255, unique=True)
    # room occupant relation table name
    hostelRoomOccupant = models.CharField(max_length=255, unique=True)
    # view permission table name
    hostelViewPermission = models.CharField(max_length=255, null=False)

    def __str__(self):
        return self.hostelName


# table with different room categories and its abbrevations used

class RoomCategory(models.Model):
    class Meta:
        verbose_name = "RoomCategory"
        verbose_name_plural = "RoomCategory"

    roomId = models.IntegerField(null=False)
    abbrevation = models.CharField(max_length=255, primary_key=True)
    # description such as single occupancy/double occupancy/attached toilets etc
    description = models.CharField(max_length=255, null=False)

    def __str__(self):
        return str(self.description)


# table with different occupant categories and its abbrevations used

class OccupantCategory(models.Model):
    class Meta:
        verbose_name = "OccupantCategory"
        verbose_name_plural = "OccupantCategory"

    occupantId = models.IntegerField(null=False)
    abbrevation = models.CharField(max_length=255, primary_key=True)
    # description - student/project staff etc
    description = models.CharField(max_length=255, null=False)

    def __str__(self):
        return self.description


# table with details of rooms in hostels .one for each hostel

class HostelRoom(models.Model):
    class Meta:
        verbose_name = "HostelRoom"
        verbose_name_plural = "HostelRoom"

    # occupancy as singlee/double etc
    roomOccupancyType = models.ForeignKey(RoomCategory, on_delete=models.CASCADE)
    # floor as 1st/2nd etc
    floorInfo = models.CharField(max_length=255, choices=FLOOR_CHOICES)
    # status as abandoned/partially damaged etc
    roomStatus = models.CharField(max_length=255, choices=ROOM_STATUS_CHOICES)
    roomOccupancyGender = models.CharField(max_length=255, choices=GENDER_CHOICES, blank=True, null=True)
    special_category = models.IntegerField(default=0)
    comments = models.CharField(max_length=255, blank=True, null=True)


# table with information regarding occupants staying in hostel.one for each hostel


class HostelRoomOccupantRelation(models.Model):
    class Meta:
        verbose_name = "HostelRoomOccupantRelation"
        verbose_name_plural = "HostelRoomOccupantRelation"

    hostelName = models.CharField(max_length=255, null=False, blank=False, choices=HOSTEL_CHOICES)

    # mess subscription status
    messStatus = models.CharField(max_length=255, choices=MESS_CHOICES, null=True, blank=True)
    registrationStatus = models.CharField(max_length=255, choices=REGISTRATION_STATUS_CHOICES, null=True, blank=True,
                                          default="UNKNOWN")
    # toMess - end date of mess subscription
    toMess = models.DateField(null=True, blank=True)
    # fromMess - start date of mess subscription
    fromMess = models.DateField(null=True, blank=True)
    # fromRoomStay - start date of room stay
    fromRoomStay = models.DateField(null=True, blank=True)
    # toRoomStay - end date of room stay
    toRoomStay = models.DateField(null=True, blank=True)
    comment = models.CharField(max_length=255, null=True, blank=True)


# #table with name and webmail of the people with access permissions(view only).one for each hostel
#
class HostelViewAccess(models.Model):
    class Meta:
        verbose_name = "HostelViewAccess"
        verbose_name_plural = "HostelViewAccess"

    name = models.CharField(max_length=255, null=False)
    webmail = models.CharField(max_length=255, primary_key=True)

    def __str__(self):
        return self.webmail


# table with all information of a particular OccupantDetails

class OccupantDetails(models.Model):
    # def validate_image(fieldfile_obj):
    #     filesize = fieldfile_obj.file.size
    #     megabyte_limit = 0.5
    #     if filesize > megabyte_limit*1024*1024:
    #         raise ValidationError("Max file size is %sMB" % str(megabyte_limit))
    class Meta:
        verbose_name = "OccupantDetails"
        verbose_name_plural = "OccupantDetails"

    name = models.CharField(max_length=255, null=False, blank=False, default="")
    # id type - roll no/aadhar no/project id etc
    idType = models.CharField(max_length=255, choices=ID_CHOICES, null=False, blank=False, default="Rollno")
    # rollno/aadhar no etc
    # primary_key removed temp
    idNo = models.CharField(max_length=255, primary_key=True, null=False, blank=False, default="", unique=True)
    # vgv
    gender = models.CharField(max_length=255, choices=GENDER_CHOICES, null=False, blank=False, default="Male")
    # specially abled/differently abled
    saORda = models.CharField(max_length=255, choices=ABILITY_CHOICES, null=False, blank=False, default="No")
    webmail = models.CharField(max_length=255, null=True, blank=True)
    altEmail = models.EmailField(max_length=255, null=False, blank=False, default="")
    mobNo = models.CharField(max_length=12, null=False, blank=False, default="")
    emgercencyNo = models.CharField(max_length=12, null=False, blank=False, default="")
    photo = models.ImageField(upload_to='profile_pics', blank=True, null=True)
    idPhoto = models.ImageField(upload_to='id_pics', blank=True, null=True)
    Address = models.CharField(max_length=300, null=False, blank=False, default="")
    Pincode = models.CharField(max_length=12, null=False, blank=False, default="")
    bankName = models.CharField(max_length=255, null=True, blank=True)
    bankAccount = models.CharField(max_length=255, null=True, blank=True)
    IFSCCode = models.CharField(max_length=255, null=True, blank=True)
    # account holder name
    accHolderName = models.CharField(max_length=255, null=True, blank=True)
    flag = models.IntegerField(default=0)

    def __str__(self):
        return self.idNo


# following are the hostelRoom,roomOccupantRelation and view access tables for each hostel(13*3=39 tables)
# hostelRoom inherits HostelRoom
# hostelView inherits HostelViewAccess
# hostelRORelation inherits HostelRoomOccupantRelation

class TemporaryDetails(models.Model):
    # def validate_image(fieldfile_obj):
    #     filesize = fieldfile_obj.file.size
    #     megabyte_limit = 0.5
    #     if filesize > megabyte_limit*1024*1024:
    #         raise ValidationError("Max file size is %sMB" % str(megabyte_limit))
    class Meta:
        verbose_name = "TemporaryDetails"
        verbose_name_plural = "TemporaryDetails"

    name = models.CharField(max_length=255, null=False, blank=False, default="")
    # id type - roll no/aadhar no/project id etc
    idType = models.CharField(max_length=255, choices=ID_CHOICES, null=False, blank=False, default="Rollno")
    # rollno/aadhar no etc
    # primary_key removed temp
    idNo = models.CharField(max_length=255, null=False, blank=False, default="")
    # vgv
    gender = models.CharField(max_length=255, choices=GENDER_CHOICES, null=False, blank=False, default="Male")
    # specially abled/differently abled
    saORda = models.CharField(max_length=255, choices=ABILITY_CHOICES, null=False, blank=False, default="No")
    webmail = models.CharField(max_length=255, null=True, blank=True)
    altEmail = models.EmailField(max_length=255, null=False, blank=False, default="")
    mobNo = models.CharField(max_length=12, null=False, blank=False, default="")
    emgercencyNo = models.CharField(max_length=12, null=False, blank=False, default="")
    photo = models.ImageField(upload_to='profile_pics', blank=True, null=True)
    idPhoto = models.ImageField(upload_to='id_pics', blank=True, null=True)
    Address = models.CharField(max_length=300, null=False, blank=False, default="")
    Pincode = models.CharField(max_length=12, null=False, blank=False, default="")
    bankName = models.CharField(max_length=255, null=False, blank=False, default="")
    bankAccount = models.CharField(max_length=255, null=False, blank=False, default="")
    IFSCCode = models.CharField(max_length=255, null=False, blank=False, default="")
    # account holder name
    accHolderName = models.CharField(max_length=255, null=False, blank=False, default="")
    ct_approval = models.CharField(max_length=255, choices=STATUS_CHOICES, default="Pending")
    comments = models.CharField(max_length=255, null=True, blank=True)
    flag = models.IntegerField(default=0)
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.name


class UpcomingOccupantRequest(models.Model):
    # def validate_image(fieldfile_obj):
    #     filesize = fieldfile_obj.file.size
    #     megabyte_limit = 0.5
    #     if filesize > megabyte_limit*1024*1024:
    #         raise ValidationError("Max file size is %sMB" % str(megabyte_limit))
    hostelName = models.CharField(max_length=255, choices=HOSTEL_CHOICES)
    guestname = models.CharField(max_length=255, null=False)
    hostelName = models.CharField(max_length=255, choices=HOSTEL_CHOICES)
    id_type = models.CharField(max_length=255, choices=ID_CHOICES)
    id_no = models.CharField(max_length=20, null=False)
    Gender = models.CharField(max_length=255, choices=GENDER_CHOICES)
    saORda = models.CharField(max_length=255, choices=ABILITY_CHOICES, default="No")
    Address = models.CharField(max_length=300, null=False)
    Pincode = models.CharField(max_length=255, null=False, blank=False, default="")
    Mobile_No = models.CharField(max_length=12, null=False, blank=False, default="")
    Emergency_Mobile_No = models.CharField(max_length=12, null=False, blank=False, default="")
    Webmail_id = models.CharField(max_length=255, null=True, blank=True, default="")
    Alternate_email_id = models.EmailField(null=False)
    Bank_Name = models.CharField(max_length=255, null=True, blank=True)
    Account_Holder_Name = models.CharField(max_length=255, null=True, blank=True)
    Bank_Account_No = models.CharField(max_length=255, null=False, blank=False, default="")
    IFSCCode = models.CharField(max_length=255, null=True, blank=True)
    From_Date = models.DateField()
    To_Date = models.DateField()
    Purpose_Of_Stay = models.CharField(max_length=255, choices=PURPOSE_CHOICES, null=True, blank=True)
    Preference_Room = models.ForeignKey(RoomCategory, null=True, blank=True, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='profile_pics', blank=True, null=True)
    idPhoto = models.ImageField(upload_to='id_pics', blank=True, null=True)
    #
    # prefernce??
    Host_Name = models.CharField(max_length=255, null=False)
    Host_Webmail_Id = models.CharField(max_length=255)
    Host_Id = models.CharField(max_length=255, null=False)
    # To_be_approved_by=models.CharField(max_length=255,choices = TOAPPROVEDBY_CHOICES)
    # approved by hod,hosaa etc
    # isApprovedFirst = models.CharField(max_length=255,choices = STATUS_CHOICES,default = "Pending")
    # is aproved by chr_hab
    isApprovedChr = models.CharField(max_length=255, choices=STATUS_CHOICES, default="Pending")
    comments = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "allotment"
        verbose_name_plural = "allotment"
        # unique_together = ('Mobile_No', 'Emergency_Mobile_No',)

    def __str__(self):
        return self.guestname


class UpcomingOccupant(models.Model):
    class Meta:
        verbose_name = "UpcomingOccupant"
        verbose_name_plural = "UpcomingOccupant"

    occupantName = models.CharField(max_length=255)
    idType = models.CharField(max_length=255, choices=ID_CHOICES)
    occupantId = models.CharField(max_length=255)
    hostelName = models.CharField(max_length=255, choices=HOSTEL_CHOICES)
    roomNo = models.CharField(max_length=255, blank=True, null=True)
    fromStay = models.DateField()
    toStay = models.DateField()
    comments = models.CharField(max_length=255, null=True, blank=True,default="")

    def __str__(self):
        return self.occupantName


class Login(models.Model):
    name = models.CharField(max_length=255, null=False)
    webmail = models.CharField(max_length=255, null=False)
    password = models.CharField(max_length=255, null=False)


class ChrViewAccess(models.Model):
    name = models.CharField(max_length=255, null=False)
    webmail = models.CharField(max_length=255, null=False)


# log table of room occuopant relation
class Log_Table(models.Model):
    occupantId = models.CharField(max_length=255)
    roomNo = models.CharField(max_length=255)
    hostelName = models.CharField(max_length=255, null=False, blank=False, choices=HOSTEL_CHOICES)
    # mess subscription status
    messStatus = models.CharField(max_length=255, choices=MESS_CHOICES, null=True, blank=True)
    registrationStatus = models.CharField(max_length=255, choices=REGISTRATION_STATUS_CHOICES, null=True, blank=True,
                                          default="UNKNOWN")
    # toMess - end date of mess subscription
    toMess = models.DateField(null=True, blank=True)
    # fromMess - start date of mess subscription
    fromMess = models.DateField(null=True, blank=True)
    # fromRoomStay - start date of room stay
    fromRoomStay = models.DateField(null=True, blank=True)
    # toRoomStay - end date of room stay
    toRoomStay = models.DateField(null=True, blank=True)
    comment = models.CharField(max_length=255, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Log_Table_ror"
        verbose_name_plural = "Log_Table_ror"


# log table of occupant details
class Occupant_Log_Table(models.Model):
    class Meta:
        verbose_name = "Log_Table_occupant"
        verbose_name_plural = "Log_Table_occupant"

    name = models.CharField(max_length=255, null=False, blank=False, default="")
    # id type - roll no/aadhar no/project id etc
    idType = models.CharField(max_length=255, choices=ID_CHOICES, null=False, blank=False, default="Rollno")
    # rollno/aadhar no etc
    # primary_key removed temp
    idNo = models.CharField(max_length=255, null=False, blank=False, default="")
    # vgv
    gender = models.CharField(max_length=255, choices=GENDER_CHOICES, null=False, blank=False, default="Male")
    # specially abled/differently abled
    saORda = models.CharField(max_length=255, choices=ABILITY_CHOICES, null=False, blank=False, default="No")
    webmail = models.CharField(max_length=255, null=True, blank=True)
    altEmail = models.EmailField(max_length=255, null=False, blank=False, default="")
    mobNo = models.CharField(max_length=12, null=False, blank=False, default="")
    emgercencyNo = models.CharField(max_length=12, null=False, blank=False, default="")
    photo = models.ImageField(upload_to='profile_pics', blank=True, null=True)
    idPhoto = models.ImageField(upload_to='id_pics', blank=True, null=True)
    Address = models.CharField(max_length=300, null=False, blank=False, default="")
    Pincode = models.CharField(max_length=12, null=False, blank=False, default="")
    bankName = models.CharField(max_length=255, null=True, blank=True)
    bankAccount = models.CharField(max_length=255, null=True, blank=True)
    IFSCCode = models.CharField(max_length=255, null=True, blank=True)
    # account holder name
    accHolderName = models.CharField(max_length=255, null=True, blank=True)
    flag = models.IntegerField(default=0)

    def __str__(self):
        return self.idNo


class SiangRoom(HostelRoom):
    roomNo = models.CharField(max_length=255, primary_key=True, null=False, blank=False, default="")

    class Meta:
        verbose_name = "siangRoom"
        verbose_name_plural = "siangRoom"

    def __str__(self):
        return str(self.roomNo)


class SiangView(HostelViewAccess):
    class Meta:
        verbose_name = "siangView"
        verbose_name_plural = "siangView"


class SiangRORelation(HostelRoomOccupantRelation):
    occupantId = models.OneToOneField(OccupantDetails, on_delete=models.CASCADE,
                                      primary_key=True, null=False, blank=False, default="")
    # occupantId = models.ForeignKey(OccupantDetails, primary_key=True, null=False, blank=False, default="")
    roomNo = models.ForeignKey(SiangRoom, on_delete=models.CASCADE, null=False, blank=False)

    class Meta:
        verbose_name = "siangRORelation"
        verbose_name_plural = "siangRORelation"

    def __str__(self):
        return str(self.occupantId)


class LohitRoom(HostelRoom):
    roomNo = models.CharField(max_length=255, primary_key=True, null=False, blank=False, default="")

    class Meta:
        verbose_name = "lohitRoom"
        verbose_name_plural = "lohitRoom"

    def __str__(self):
        return str(self.roomNo)


class LohitView(HostelViewAccess):
    class Meta:
        verbose_name = "lohitView"
        verbose_name_plural = "lohitView"


class LohitRORelation(HostelRoomOccupantRelation):
    occupantId = models.OneToOneField(OccupantDetails, on_delete=models.CASCADE,
                                      primary_key=True, null=False, blank=False)
    # occupantId = models.ForeignKey(OccupantDetails, primary_key=True, null=False, blank=False, default="")
    roomNo = models.ForeignKey(LohitRoom, on_delete=models.CASCADE, null=False, blank=False)

    class Meta:
        verbose_name = "lohitRORelation"
        verbose_name_plural = "lohitRORelation"

    def __str__(self):
        return str(self.occupantId)


class DihingRoom(HostelRoom):
    roomNo = models.CharField(max_length=255, primary_key=True, null=False, blank=False, default="")

    class Meta:
        verbose_name = "dihingRoom"
        verbose_name_plural = "dihingRoom"

    def __str__(self):
        return str(self.roomNo)


class DihingView(HostelViewAccess):
    class Meta:
        verbose_name = "dihingView"
        verbose_name_plural = "dihingView"


class DihingRORelation(HostelRoomOccupantRelation):
    occupantId = models.OneToOneField(OccupantDetails, on_delete=models.CASCADE,
                                      primary_key=True, null=False, blank=False, default="")
    # occupantId = models.ForeignKey(OccupantDetails, primary_key=True, null=False, blank=False, default="")
    roomNo = models.ForeignKey(DihingRoom, on_delete=models.CASCADE, null=False, blank=False, default="")

    class Meta:
        verbose_name = "dihingRORelation"
        verbose_name_plural = "dihingRORelation"

    def __str__(self):
        return str(self.occupantId)


class DibangRoom(HostelRoom):
    roomNo = models.CharField(max_length=255, primary_key=True, null=False, blank=False, default="")

    class Meta:
        verbose_name = "dibangRoom"
        verbose_name_plural = "dibangRoom"

    def __str__(self):
        return str(self.roomNo)


class DibangView(HostelViewAccess):
    class Meta:
        verbose_name = "dibangView"
        verbose_name_plural = "dibangView"


class DibangRORelation(HostelRoomOccupantRelation):
    occupantId = models.OneToOneField(OccupantDetails, on_delete=models.CASCADE,
                                      primary_key=True, null=False, blank=False)
    # occupantId = models.ForeignKey(OccupantDetails, primary_key=True, null=False, blank=False, default="")
    roomNo = models.ForeignKey(DibangRoom, on_delete=models.CASCADE, null=False, blank=False)

    class Meta:
        verbose_name = "dibangRORelation"
        verbose_name_plural = "dibangRORelation"

    def __str__(self):
        return str(self.occupantId)


class KapiliRoom(HostelRoom):
    roomNo = models.CharField(max_length=255, primary_key=True, null=False, blank=False, default="")

    class Meta:
        verbose_name = "kapiliRoom"
        verbose_name_plural = "kapiliRoom"

    def __str__(self):
        return str(self.roomNo)


class KapiliView(HostelViewAccess):
    class Meta:
        verbose_name = "kapiliView"
        verbose_name_plural = "kapiliView"


class KapiliRORelation(HostelRoomOccupantRelation):
    occupantId = models.OneToOneField(OccupantDetails, on_delete=models.CASCADE,
                                      primary_key=True, null=False, blank=False)
    # occupantId = models.ForeignKey(OccupantDetails, primary_key=True, null=False, blank=False, default="")
    roomNo = models.ForeignKey(KapiliRoom, on_delete=models.CASCADE, null=False, blank=False)

    class Meta:
        verbose_name = "kapiliRORelation"
        verbose_name_plural = "kapiliRORelation"

    def __str__(self):
        return str(self.occupantId)


class ManasRoom(HostelRoom):
    roomNo = models.CharField(max_length=255, primary_key=True, null=False, blank=False, default="")

    class Meta:
        verbose_name = "manasRoom"
        verbose_name_plural = "manasRoom"

    def __str__(self):
        return str(self.roomNo)


class ManasView(HostelViewAccess):
    class Meta:
        verbose_name = "manasView"
        verbose_name_plural = "manasView"


class ManasRORelation(HostelRoomOccupantRelation):
    occupantId = models.OneToOneField(OccupantDetails, on_delete=models.CASCADE,
                                      primary_key=True, null=False, blank=False)
    # occupantId = models.ForeignKey(OccupantDetails, primary_key=True, null=False, blank=False, default="")
    roomNo = models.ForeignKey(ManasRoom, on_delete=models.CASCADE, null=False, blank=False)

    class Meta:
        verbose_name = "manasRORelation"
        verbose_name_plural = "manasRORelation"

    def __str__(self):
        return str(self.occupantId)


class BarakRoom(HostelRoom):
    roomNo = models.CharField(max_length=255, primary_key=True, null=False, blank=False, default="")

    class Meta:
        verbose_name = "barakRoom"
        verbose_name_plural = "barakRoom"

    def __str__(self):
        return str(self.roomNo)


class BarakView(HostelViewAccess):
    class Meta:
        verbose_name = "barakView"
        verbose_name_plural = "barakView"


class BarakRORelation(HostelRoomOccupantRelation):
    occupantId = models.OneToOneField(OccupantDetails, on_delete=models.CASCADE,
                                      primary_key=True, null=False, blank=False)
    # occupantId = models.ForeignKey(OccupantDetails, primary_key=True, null=False, blank=False, default="")
    roomNo = models.ForeignKey(BarakRoom, on_delete=models.CASCADE, null=False, blank=False)

    class Meta:
        verbose_name = "barakRORelation"
        verbose_name_plural = "barakRORelation"

    def __str__(self):
        return str(self.occupantId)


class UmiamRoom(HostelRoom):
    roomNo = models.CharField(max_length=255, primary_key=True, null=False, blank=False, default="")

    class Meta:
        verbose_name = "umiamRoom"
        verbose_name_plural = "umiamRoom"

    def __str__(self):
        return str(self.roomNo)


class UmiamView(HostelViewAccess):
    class Meta:
        verbose_name = "umiamView"
        verbose_name_plural = "umiamView"


class UmiamRORelation(HostelRoomOccupantRelation):
    occupantId = models.OneToOneField(OccupantDetails, on_delete=models.CASCADE,
                                      primary_key=True, null=False, blank=False)
    # occupantId = models.ForeignKey(OccupantDetails, primary_key=True, null=False, blank=False, default="")
    roomNo = models.ForeignKey(UmiamRoom, on_delete=models.CASCADE, null=False, blank=False)

    class Meta:
        verbose_name = "umiamRORelation"
        verbose_name_plural = "umiamRORelation"

    def __str__(self):
        return str(self.occupantId)


class BramhaputraRoom(HostelRoom):
    roomNo = models.CharField(max_length=255, primary_key=True, null=False, blank=False)

    class Meta:
        verbose_name = "bramhaputraRoom"
        verbose_name_plural = "bramhaputraRoom"

    def __str__(self):
        return str(self.roomNo)


class BramhaputraView(HostelViewAccess):
    class Meta:
        verbose_name = "bramhaputraView"
        verbose_name_plural = "bramhaputraView"


class BramhaputraRORelation(HostelRoomOccupantRelation):
    occupantId = models.OneToOneField(OccupantDetails, on_delete=models.CASCADE,
                                      primary_key=True, null=False, blank=False)  # models.ForeignKey(OccupantDetails,primary_key=True)
    roomNo = models.ForeignKey(BramhaputraRoom, on_delete=models.CASCADE, null=False, blank=False)

    class Meta:
        verbose_name = "bramhaputraRORelation"
        verbose_name_plural = "bramhaputraRORelation"

    def __str__(self):
        return str(self.occupantId)


class DhansiriRoom(HostelRoom):
    roomNo = models.CharField(max_length=255, primary_key=True, null=False, blank=False, default="")

    class Meta:
        verbose_name = "dhansiriRoom"
        verbose_name_plural = "dhansiriRoom"

    def __str__(self):
        return str(self.roomNo)


class DhansiriView(HostelViewAccess):
    class Meta:
        verbose_name = "dhansiriView"
        verbose_name_plural = "dhansiriView"


class DhansiriRORelation(HostelRoomOccupantRelation):
    occupantId = models.OneToOneField(OccupantDetails, on_delete=models.CASCADE,
                                      primary_key=True, null=False, blank=False)
    # occupantId = models.ForeignKey(OccupantDetails, primary_key=True, null=False, blank=False, default="")
    roomNo = models.ForeignKey(DhansiriRoom, on_delete=models.CASCADE, null=False, blank=False)

    class Meta:
        verbose_name = "dhansiriRORelation"
        verbose_name_plural = "dhansiriRORelation"

    def __str__(self):
        return str(self.occupantId)


class SubansiriRoom(HostelRoom):
    roomNo = models.CharField(max_length=255, primary_key=True, null=False, blank=False)

    class Meta:
        verbose_name = "subansiriRoom"
        verbose_name_plural = "subansiriRoom"

    def __str__(self):
        return str(self.roomNo)


class SubansiriView(HostelViewAccess):
    class Meta:
        verbose_name = "subansiriView"
        verbose_name_plural = "subansiriView"


class SubansiriRORelation(HostelRoomOccupantRelation):
    occupantId = models.OneToOneField(OccupantDetails, on_delete=models.CASCADE,
                                      primary_key=True, null=False, blank=False)
    # occupantId = models.ForeignKey(OccupantDetails, primary_key=True,null=False, blank=False, default="")
    roomNo = models.ForeignKey(SubansiriRoom, on_delete=models.CASCADE, null=False, blank=False)

    class Meta:
        verbose_name = "subansiriRORelation"
        verbose_name_plural = "subansiriRORelation"

    def __str__(self):
        return str(self.occupantId)


class KamengRoom(HostelRoom):
    roomNo = models.CharField(max_length=255, primary_key=True, null=False, blank=False, default="")

    class Meta:
        verbose_name = "kamengRoom"
        verbose_name_plural = "kamengRoom"

    def __str__(self):
        return str(self.roomNo)


class KamengView(HostelViewAccess):
    class Meta:
        verbose_name = "kamengView"
        verbose_name_plural = "kamengView"


class KamengRORelation(HostelRoomOccupantRelation):
    occupantId = models.OneToOneField(OccupantDetails, on_delete=models.CASCADE,
                                      primary_key=True, null=False, blank=False)
    # occupantId = models.ForeignKey(OccupantDetails, primary_key=True, null=False, blank=False, default="")
    roomNo = models.ForeignKey(KamengRoom, on_delete=models.CASCADE, null=False, blank=False)

    class Meta:
        verbose_name = "kamengRORelation"
        verbose_name_plural = "kamengRORelation"

    def __str__(self):
        return str(self.occupantId)


# MESS automation
# default=m2  default=y2
MONTHS_CHOICES = [(str(i), calendar.month_name[i]) for i in range(1, 13)]
YEARS_CHOICES = [(i, i) for i in range(2010, datetime.now().year + 1)]
curr_month = datetime.now().month
curr_year = datetime.now().year
m1 = curr_month
y1 = curr_year
m1 = m1 - 1
m1_y1 = ""
if m1 < 1:
    m1 = 12
    y1 = y1 - 1


# MESS automation
# default=m2  default=y2
class Automation(models.Model):
    class Meta:
        verbose_name = "Automation"
        verbose_name_plural = "Automation"
        unique_together = ('month', 'year')

    month = models.CharField(max_length=9, choices=MONTHS_CHOICES)
    year = models.IntegerField(choices=YEARS_CHOICES)

    feed_on_off = models.BooleanField(default=False)
    feed_start_date = models.DateField(null=True, blank=True)
    feed_off_date = models.DateField(null=True, blank=True)

    pref_on_off = models.BooleanField()
    pref_start_date = models.DateField(null=True, blank=True)
    pref_off_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return '%s_%s' % (self.month, self.year)


# MESS model for csv files import and export
EXPORT_CHOICES_LIST = [('All Hostels', 'All Hostels')] + list(HOSTEL_CHOICES)
EXPORT_CHOICES_TUPLE = tuple(EXPORT_CHOICES_LIST)


class HostelMessVacancies(models.Model):
    class Meta:
        verbose_name = "Hostel Mess Vacancies"
        verbose_name_plural = "Hostel Mess Vacancies"

    hostelName = models.CharField(max_length=255, null=False, blank=False, choices=HOSTEL_CHOICES1)
    upper_limit = models.IntegerField(null=True, blank=False, default=0)
    hostel_strengh = models.IntegerField(null=False, blank=False, default=0)
    occupied = models.IntegerField(null=False, blank=False, default=0)
    month = models.CharField(max_length=255, null=False, blank=False, default="")
    occupied_history_1 = models.IntegerField(null=False, blank=False, default=0)
    occupied_history_2 = models.IntegerField(null=False, blank=False, default=0)
    occupied_history_3 = models.IntegerField(null=False, blank=False, default=0)

    def __str__(self):
        return str(self.hostelName)


class DebarredStudents(models.Model):
    class Meta:
        verbose_name = "Debarred Students"
        verbose_name_plural = "Debarred Students"
        unique_together = ('idNo', 'webmail', 'debarred_hostel', 'start_date', 'end_date')

    name = models.CharField(max_length=255, null=False, blank=False)
    idType = models.CharField(max_length=255, choices=ID_CHOICES, null=False, blank=False, default="Rollno")
    idNo = models.CharField(max_length=255, null=False, blank=False, default="")
    webmail = models.CharField(max_length=255, null=False, blank=False, default="")
    debarred_hostel = models.CharField(max_length=255, null=False, blank=False, choices=HOSTEL_CHOICES2)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    date_created = models.DateTimeField(null=False, blank=False, default=datetime.now)
    reasons = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return str(self.name) + "_" + str(self.debarred_hostel)


class InventoryItemsLocation(models.Model):
    category = models.CharField(max_length=255, null=False, blank=False, choices=LOCATION_CHOICE)
    sub_category = models.CharField(max_length=255, null=False, blank=False, default="")

    def __str__(self):
        return str(self.category) + "_" + str(self.sub_category)


class InventoryItems(models.Model):
    class Meta:
        verbose_name = "Inventory Items"
        verbose_name_plural = "Inventory Items"

    purchase_order_no = models.CharField(max_length=255, null=False, blank=False, default="", unique=True)
    purchase_date = models.DateField(null=False, blank=False, default=datetime.now)
    item_name = models.CharField(max_length=255, null=False, blank=False, default="")
    description = models.CharField(max_length=1000, null=False, blank=False, default="")
    quantity = models.IntegerField(null=False, blank=False, default=0)
    total_cost = models.IntegerField(null=False, blank=False, default=0)
    bill_no = models.CharField(max_length=1000, null=False, blank=False, default="")
    supplier_name = models.CharField(max_length=255, null=False, blank=False, default="")
    supplier_email = models.EmailField(max_length=255, null=False, blank=False, default="")
    supplier_address = models.TextField(max_length=1000, null=False, blank=False, default="")
    supplier_phone_no1 = models.IntegerField(null=False, blank=False, default=0)
    supplier_phone_no2 = models.IntegerField(null=True, blank=True)
    receipt_date = models.DateField(null=True, blank=True)
    alloted_location_category = models.CharField(max_length=255, null=False, blank=False, choices=LOCATION_CHOICE)
    alloted_location_subcategory = models.CharField(max_length=255, null=False, blank=False, default="")
    alloted_to_details = models.CharField(max_length=500, null=False, blank=False, default="")
    # transfer_order_no = models.CharField(max_length=255, null=True, blank=True)
    # transfer_date = models.DateField(null=True, blank=True)
    # transferred_to = models.CharField(max_length=500, null=True, blank=True)
    remarks = models.TextField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return str(self.purchase_order_no) + "_" + str(self.item_name) + "_" + str(self.alloted_location_subcategory)


class InventoryDamagedItems(models.Model):
    class Meta:
        verbose_name = "Inventory Damaged Items"
        verbose_name_plural = "Inventory Damaged Items"

    purchase_order_no = models.CharField(max_length=255, null=False, blank=False, default="")
    item_name = models.CharField(max_length=255, null=False, blank=False, default="")
    damaged_item_quantity = models.IntegerField(null=False, blank=False, default=0)
    comments_on_damage = models.TextField(max_length=1000, null=True, blank=True)
    date = models.DateField(null=False, blank=False, default=datetime.now)
    total_damage_quantity = models.IntegerField(null=False, blank=False, default=0)

    def __str__(self):
        return str(self.purchase_order_no)


class ImportExportFiles(models.Model):
    hostelName = models.CharField(max_length=255, choices=EXPORT_CHOICES_TUPLE)
    month = models.CharField(max_length=9, choices=MONTHS_CHOICES)
    year = models.IntegerField(choices=YEARS_CHOICES)


