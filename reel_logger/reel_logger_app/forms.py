'''
These are the forms used on webpages.
These form objects help facilitate taking information from the user and translating that into objects.
It is also used to query information from the user in general
'''
from django import forms

from reel_logger_app.models import Footage, Take, Scene, Shot, FootageTake, Comment
 
# -------------- Model Forms ------------------
# the following forms are based on models and translate between use input and models.

class FootageForm(forms.ModelForm):
    class Meta:
        model = Footage # specify the name of model to use
        fields = "__all__" # use all fields
        exclude = ['path'] # exclude path - that is not able to be changed

# form for modifying takes in general
# not used
class TakeForm(forms.ModelForm):
    class Meta:
        model = Take
        fields = "__all__" 
        exclude = ['footage'] # exclude footage - it gets too confusing

# form for modifying take inside of a footage instance
class TakeInFootageForm(forms.ModelForm):
    # add start_time
    # this 'technically' represents a FootageTake
    start_time = forms.DurationField()

    class Meta:
        model = Take
        fields = "__all__" # use all fields except the excluded ones
        exclude = ['footage', 'shot_scene', 'shot_name', 'take_no']

# form for creating an entirely new scene
class NewSceneForm(forms.ModelForm):
    class Meta:
        model = Scene
        fields = "__all__" # we want all attributes

# form for editing an existing scene
class SceneForm(forms.ModelForm):
    class Meta:
        model = Scene
        fields = "__all__"
        exclude = ['script_number'] # we don't want to change script_number

# form for creating a new shot in general
# mainly kept for debugging purposes
class ShotForm(forms.ModelForm):
    class Meta:
        model = Shot
        fields = "__all__"

# form for creating and modifying a shot belonging to a specific scene
class ShotInSceneForm(forms.ModelForm):
    class Meta:
        model = Shot
        fields = "__all__"
        exclude = ['scene'] # exclude scene since that's constant

# form for creating and modifying comments
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = "__all__"
        exclude = ['footage'] # exclude footage - we will fill that in programmatically

# form for adding a footageTake given a footage
class AddTakeToFootageForm(forms.ModelForm):
    class Meta:
        model = FootageTake
        fields = "__all__"
        exclude = ['footage'] # we are assuming footage is given

# -------------- Actual Forms ------------------

# form used to search for footage
class FootageSearch(forms.Form):
    scene = forms.IntegerField(required=False, min_value=0, max_value=255)
    shot = forms.CharField(max_length=64, required=False)
    take = forms.IntegerField(required=False, min_value=0, max_value=255)
    logged_filter = forms.ChoiceField(required=False, choices=((1, 'Logged and Unlogged'), (2, 'Logged only'), (3, 'Unlogged only')))

# form used for the settings when organizing footage
class FormatSettings(forms.Form):
    include_uid = forms.BooleanField(required=False, initial=True, help_text="Recommended True")
    include_hash = forms.BooleanField(required=False, initial=False, help_text="Recommended False")
    include_original_filename = forms.BooleanField(required=False, initial=True)
    base_takes_on = forms.ChoiceField(required=True, choices=((1, 'True Take'), (2, 'Marked Take First')))
    include_take_in_filename = forms.BooleanField(required=False, initial=True)
    for_multiple_takes_use = forms.ChoiceField(required=True, choices=((1, 'First Take'), (2, 'Last Take'), (3, 'Median Take')))
    sort_folders_by = forms.ChoiceField(required=True, choices=((1, 'None'), (2, 'Scene'), (3, 'Scene and Shot'), (4, 'Scene, Shot, and Take')))
    include_rating = forms.ChoiceField(required=True, choices=((1, 'No'), (2, 'As number'), (3, 'As symbol')))
    use_rating = forms.ChoiceField(required=False, choices=((1, 'Average (rounded)'), (2, 'Max')))
    only_logged_footage = forms.BooleanField(required=False, initial=True, help_text="Recommended True")
    only_create_used_directories = forms.BooleanField(required=False, initial=False, help_text="Recommended False")