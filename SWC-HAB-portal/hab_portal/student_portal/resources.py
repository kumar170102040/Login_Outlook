from import_export import resources
from .models import *

class MessFeedbackResource(resources.ModelResource):
    class Meta:
        model = MessFeedback
        exclude = ('description', 'uploaded_at', 'document')
