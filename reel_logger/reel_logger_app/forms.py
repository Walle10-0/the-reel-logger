from django import forms

from reel_logger_app.models import Footage, Take, Scene, Shot, FootageTake, Comment
 
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
        exclude = ['footage']

class NewSceneForm(forms.ModelForm):
    class Meta:
        model = Scene
        fields = "__all__"

class SceneForm(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = Scene
        fields = "__all__"
        exclude = ['script_number']

class ShotForm(forms.ModelForm):
    class Meta:
        model = Shot
        fields = "__all__"

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = "__all__"
        exclude = ['footage']

class ShotInSceneForm(forms.ModelForm):
    class Meta:
        model = Shot
        fields = "__all__"
        exclude = ['scene']

class AddTakeToFootageForm(forms.ModelForm):
    class Meta:
        model = FootageTake
        fields = "__all__"
        exclude = ['footage']

class TakeInFootageForm(forms.ModelForm):
    start_time = forms.DurationField()

    class Meta:
        model = Take
        fields = "__all__"
        exclude = ['footage', 'shot_scene', 'shot_name', 'take_no']

class FootageSearch(forms.Form):
    scene = forms.IntegerField(required=False, min_value=0, max_value=255)
    shot = forms.CharField(max_length=64, required=False)
    take = forms.IntegerField(required=False, min_value=0, max_value=255)
    logged_filter = forms.ChoiceField(required=False, choices=((1, 'Logged and Unlogged'), (2, 'Logged only'), (3, 'Unlogged only')))