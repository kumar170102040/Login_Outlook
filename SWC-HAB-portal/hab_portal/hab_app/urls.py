"""
#from django.conf.urls import url
from django.urls import path
from hab_app import views
from django.contrib import admin

app_name = 'hab_app'
from django.conf.urls.static import static
#from hab_portal import settings
from django.conf import settings

urlpatterns = [
    path('login/$', views.user_login, name='user_login'),
    path('login_page/$', views.login_page, name='login_page'),
    path('vacate/$', views.vacate, name='vacate'),
    path('allot/$', views.allot, name='allot'),
    path('chrApproveApplication/$', views.chrApproveApplication, name='chrApproveApplication'),
                  # url(r'^chrDisapproveApplication/$', views.chrDisapproveApplication,name='chrDisapproveApplication'),
    path('showDetails/$', views.showDetails, name='showDetails'),
    path('showDetails2/$', views.showDetails2, name='showDetails2'),
    path('addDetails/$', views.addDetails, name='addDetails'),
    path('addDetails2/$', views.addDetails2, name='addDetails2'),
    path('chrAllot/$', views.chrAllot, name='chrAllot'),
                  # url(r'^approveApplication/$', views.approveApplication,name='approveApplication'),
                  # url(r'^disapproveApplication/$', views.disapproveApplication,name='disapproveApplication'),
    path('generalAllot/$', views.generalAllot, name='generalAllot'),
    path('trackApplication/$', views.trackApplication, name='trackApplication'),
    path('deleteDetails/$', views.deleteDetails, name='deleteDetails'),
    path('existingOccupants/$', views.existingOccupants, name='existingOccupants'),
    path('roomDetails/$', views.roomDetails, name='roomDetails'),
    path('chrViewRoom/$', views.chrViewRoom, name='chrViewRoom'),
    path('chrHostelSummary/$', views.chrHostelSummary, name='chrHostelSummary'),
    path('chrCaretakerView/$', views.chrCaretakerView, name='chrCaretakerView'),
    path('chrFreshersBulkAllot/$', views.chrFreshersBulkAllot, name='chrFreshersBulkAllot'),
    path('caretakerapproveinfo/$', views.caretakerapproveinfo, name='caretakerapproveinfo'),
    path('ct_add_occupant/$', views.ct_add_occupant, name='ct_add_occupant'),

    path('chrViewSpecialRooms/$', views.chrViewSpecialRooms, name='chrViewSpecialRooms'),
    path('editRODetails/(?P<occ_id>(\S)+)$', views.editRODetails, name='editRODetails'),
    path('editOccupantDetails/$', views.editOccupantDetails, name='editOccupantDetails'),
    path('chrRoomDetailsEdit/$', views.chrRoomDetailsEdit, name='chrRoomDetailsEdit'),
    path('chrRoomDetailsEdit2/(?P<hostel_name>[a-zA-Z0-9_]+)$', views.chrRoomDetailsEdit2,
                      name='chrRoomDetailsEdit2'),
    path('chrRoomAdd/(?P<hostel_name>[a-zA-Z0-9_]+)$', views.chrRoomAdd, name='chrRoomAdd'),
    path('chrRoomDelete/(?P<hostel_name>[a-zA-Z0-9_]+)$', views.chrRoomDelete, name='chrRoomDelete'),

    path('search_student/$', views.search_student, name='search_student'),
    path('mess_opi/$', views.mess_opi, name='mess_opi'),
                  # url(r'^mess_opi/calculate$', views.opi_calculate,name='opi_calculate'), #comment it
    path('mess_automation/$', views.mess_automation, name='mess_automation'),
    path('debarred_student/$', views.debarred_student, name='debarred_student'),
                  # url(r'^inventory_management/$', views.inventory_management, name='inventory_management'),
                  # url(r'^inventory_fullDetails/$', views.inventory_full_details, name='inventory_fullDetails'),
                  # url(r'^inventory_details/(?P<category>[a-zA-Z0-9_ ]+)/(?P<sub_category>[a-zA-Z0-9_ ]+)$', views.inventory_details, name='inventory_details'),
                  # url(r'^damaged_inventory_details/(?P<category>[a-zA-Z0-9_ ]+)/(?P<sub_category>[a-zA-Z0-9_ ]+)$', views.damaged_inventory_details, name='damaged_inventory_details'),
    path('mess_import_export_files/$', views.import_export_files, name='mess_import_export'),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
"""


from django.conf.urls import url
from hab_app import views
from django.contrib import admin

app_name = 'hab_app'
from django.conf.urls.static import static
#from hab_portal import settings
from django.conf import settings

urlpatterns = [
    url(r'^login/$', views.user_login, name='user_login'),
    url(r'^login_page/$', views.login_page, name='login_page'),
    url(r'^vacate/$', views.vacate, name='vacate'),
    url(r'^allot/$', views.allot, name='allot'),
    url(r'^chrApproveApplication/$', views.chrApproveApplication, name='chrApproveApplication'),
    url(r'^showDetails/$', views.showDetails, name='showDetails'),
    url(r'^showDetails2/$', views.showDetails2, name='showDetails2'),
    url(r'^addDetails/$', views.addDetails, name='addDetails'),
    url(r'^addDetails2/$', views.addDetails2, name='addDetails2'),
    url(r'^chrAllot/$', views.chrAllot, name='chrAllot'),
    url(r'^generalAllot/$', views.generalAllot, name='generalAllot'),
    url(r'^trackApplication/$', views.trackApplication, name='trackApplication'),
    url(r'^deleteDetails/$', views.deleteDetails, name='deleteDetails'),
    url(r'^existingOccupants/$', views.existingOccupants, name='existingOccupants'),
    url(r'^roomDetails/$', views.roomDetails, name='roomDetails'),
    url(r'^chrViewRoom/$', views.chrViewRoom, name='chrViewRoom'),
    url(r'^chrHostelSummary/$', views.chrHostelSummary, name='chrHostelSummary'),
    url(r'^chrCaretakerView/$', views.chrCaretakerView, name='chrCaretakerView'),
    url(r'^chrFreshersBulkAllot/$', views.chrFreshersBulkAllot, name='chrFreshersBulkAllot'),
    url(r'^caretakerapproveinfo/$', views.caretakerapproveinfo, name='caretakerapproveinfo'),
    url(r'^ct_add_occupant/$', views.ct_add_occupant, name='ct_add_occupant'),

    url(r'^chrViewSpecialRooms/$', views.chrViewSpecialRooms, name='chrViewSpecialRooms'),
    url(r'^editRODetails/(?P<occ_id>(\S)+)$', views.editRODetails, name='editRODetails'),
    url(r'^editOccupantDetails/$', views.editOccupantDetails, name='editOccupantDetails'),
    url(r'^chrRoomDetailsEdit/$', views.chrRoomDetailsEdit, name='chrRoomDetailsEdit'),
    url(r'^chrRoomDetailsEdit2/(?P<hostel_name>[a-zA-Z0-9_]+)$', views.chrRoomDetailsEdit2, name='chrRoomDetailsEdit2'),
    url(r'^chrRoomAdd/(?P<hostel_name>[a-zA-Z0-9_]+)$', views.chrRoomAdd, name='chrRoomAdd'),
    url(r'^chrRoomDelete/(?P<hostel_name>[a-zA-Z0-9_]+)$', views.chrRoomDelete, name='chrRoomDelete'),

    url(r'^search_student/$', views.search_student, name='search_student'),
    url(r'^mess_opi/$', views.mess_opi, name='mess_opi'),
    url(r'^mess_automation/$', views.mess_automation, name='mess_automation'),
    url(r'^debarred_student/$', views.debarred_student, name='debarred_student'),
    url(r'^mess_import_export_files/$', views.import_export_files, name='mess_import_export'),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
