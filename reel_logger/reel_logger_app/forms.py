from django import forms

from reel_logger_app.models import Footage, Take, Scene, Shot
 
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

class SceneForm(forms.ModelForm):
    class Meta:
        model = Scene
        fields = "__all__"

class ShotForm(forms.ModelForm):
    class Meta:
        model = Shot
        fields = "__all__"
