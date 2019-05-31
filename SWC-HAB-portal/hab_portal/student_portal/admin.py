from django.contrib import admin
from .models import *
from django.apps import apps
from import_export.admin import ImportExportModelAdmin
from import_export import resources

app = apps.get_app_config('student_portal')

class FinalPreferenceResource(resources.ModelResource):
    class Meta:
        model = FinalPreference
        exclude = ('id',)
        skip_unchanged = True
        report_skipped = True
        import_id_fields = ['username', 'month', 'year']


class FinalPreferenceAdmin(ImportExportModelAdmin):
    resource_class = FinalPreferenceResource
    search_fields = ('username', 'month')


admin.site.register(FinalPreference, FinalPreferenceAdmin)


class MessFeedbackResource(resources.ModelResource):
    class Meta:
        model = MessFeedback


class MessFeedbackAdmin(ImportExportModelAdmin):
    resource_class = MessFeedbackResource
    search_fields = ('username', 'month')


admin.site.register(MessFeedback, MessFeedbackAdmin)


class PreferenceResource(resources.ModelResource):
    class Meta:
        model = Preference
        exclude = ('id',)
        skip_unchanged = True
        report_skipped = True


class PreferenceAdmin(ImportExportModelAdmin):
    readonly_fields = ['latest_submission_time']
    search_fields = ['student_id', 'student_name', 'username']
    resource_class = PreferenceResource


admin.site.register(Preference, PreferenceAdmin)

admin.site.register(Opi_calculated)
