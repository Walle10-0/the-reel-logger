from django import forms

from reel_logger_app.models import Footage, Take
 
# create a ModelForm
class FootageForm(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = Footage
        fields = "__all__"
        exclude = ['path']

class TakeForm(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = Take
        fields = "__all__"
