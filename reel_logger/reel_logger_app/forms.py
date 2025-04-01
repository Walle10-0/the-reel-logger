from django import forms

from reel_logger_app.models import FootageUpload

class UploadForm(forms.ModelForm):
    footage = forms.FileField(widget = forms.TextInput(attrs={
            "name": "images",
            "type": "File",
            "class": "form-control",
            "multiple": "True",
        }), label = "")
    class Meta:
        model = FootageUpload
        fields = ['footage']