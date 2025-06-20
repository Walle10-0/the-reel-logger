'''
This is the heart of reel_logger_app.
All web responses for the app go through here.
It references html templates included in `templates`.
It also handles a lot of internal logic and checking.
'''
from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse
from django.core.files.storage import default_storage
from django.contrib import messages
from django.views.generic.edit import DeleteView, UpdateView
from django.urls import reverse_lazy
from django.urls import reverse as urlreverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

import datetime
import os
from pathlib import Path

from reel_logger_app.models import Footage, Comment, Scene, Shot, Take, FootageTake
from reel_logger_app.forms import FootageForm, SceneForm, ShotForm, NewSceneForm, ShotInSceneForm, AddTakeToFootageForm, TakeInFootageForm, CommentForm, FootageSearch, FormatSettings
from reel_logger_app.directoryFormatter import formatFootageDirectory

# saves on repeated code
def simple_save_if_valid(form, request):
    # check if form data is valid
    if form.is_valid():
        # save the form data to model
        form.save()
        messages.info(request, "saved successfully!!!")
    else:
        messages.error(request, 'Please correct the following errors:')

# ------------ misc ------------------

# simply returns a webpage
def index(request):
    return render(request, "index.html")

@login_required
def settings(request):
    context = {'formatter': FormatSettings()}
    return render(request, "settings.html", context)

# file upload page (handles multi-file upload)
@login_required
def fileupload(request):    
    if request.method == 'POST':
        first = ""
        for file in request.FILES.getlist('posts'):
            print(file)
            original_filename = file.name.rsplit(".", 1)[0]

            # get full filename in new location
            try_filename = os.path.join("footage", "unlogged", file.name)
            new_filename = default_storage.generate_filename(try_filename)
            new_filename = default_storage.save(new_filename, file)
            full_filename = os.path.join(default_storage.location, new_filename)
            full_filename = str(Path(full_filename).resolve(strict=True))
            print("views.py: " + full_filename)

            try:
                # create new footage object
                newfoot = Footage.objects.create(path=full_filename, original_filename=original_filename)

                if first == "":
                    first = newfoot.id
            except Exception as e:
                # handle exceptions (more common than I would like)
                print(f"An error occurred: {e}")
                print("making footage failed")
                default_storage.delete(new_filename)

        # redirects to the first footage successfully uploaded
        if first != "":
            messages.success(request, 'The files have been uploaded successfully.')
            return redirect('Footage_Editor', first)
    return render(request, "upload.html")

# posting to this page formats the footage files
@login_required
def formatDirectory(request):
    if request.method == 'POST':
        form = FormatSettings(request.POST)

        if form.is_valid():
            # grab all footage
            footage_list = Footage.objects.all()
            # format all the footage files
            formatFootageDirectory(form, footage_list)
    return redirect('logger_settings')

# ------------ footage ------------------

def viewFootage(request):
    # grab all footage
    footage_list = Footage.objects.all()

    # you can submit the form with GET
    if request.method == 'GET':
        form = FootageSearch(request.GET)
    else:
        form = FootageSearch()
    
    # filter results
    if form.is_valid():
        if form['scene'].value():
            query1 = footage_list.filter(take__shot_scene_id=form['scene'].value()).distinct()
            query2 = footage_list.filter(take__marked_scene=form['scene'].value()).distinct()
            footage_list = query1 | query2
        if form['shot'].value():
            query1 = footage_list.filter(take__shot_name=form['shot'].value()).distinct()
            query2 = footage_list.filter(take__marked_shot=form['shot'].value()).distinct()
            footage_list = query1 | query2
        if form['take'].value():
            query1 = footage_list.filter(take__take_no=form['take'].value()).distinct()
            query2 = footage_list.filter(take__marked_take=form['take'].value()).distinct()
            footage_list = query1 | query2
        if form['logged_filter'].value() == '2':
            footage_list = footage_list.filter(logged=True).distinct()
        elif form['logged_filter'].value() == '3':
            footage_list = footage_list.filter(logged=False).distinct()

    # order results
    footage_list.order_by("path")

    context = {"list": footage_list, "form":form}
    return render(request, "footage_list.html", context)

# this is the view for editing footage
def editFootage(request, footage_id):
    # get the footage
    footage = get_object_or_404(Footage, pk=footage_id)

    # save on POST if authenticated
    if request.method == 'POST' and request.user.is_authenticated:
        form = FootageForm(request.POST, instance=footage)
        simple_save_if_valid(form, request)
    else:
        form = FootageForm(instance=footage)
    
    # create forms for making new take or comment
    take_to_footage = AddTakeToFootageForm(initial={'footage': footage})
    comment_to_footage = CommentForm(initial={'footage': footage})

    # get all take forms
    all_takes = []
    for take in footage.take_set.all():
        start = FootageTake.objects.get(footage=footage, take=take).start_time
        newTakeForm = TakeInFootageForm(instance=take, initial={"start_time": start})
        all_takes.append(newTakeForm)
    
    # make all comment forms
    comment_forms = []
    for comment in Comment.objects.filter(footage=footage).order_by("time"):
        newCommentForm = CommentForm(instance=comment)
        comment_forms.append(newCommentForm)

    context = {'form': form, "take_to_footage": take_to_footage,
               "comment_to_footage": comment_to_footage,
               "takes": all_takes,
               "comments": comment_forms}
    return render(request, "footage_edit.html", context)

class FootageDeleteView(LoginRequiredMixin, DeleteView):
    model = Footage
    success_url = reverse_lazy('View_Footage')

# page that sends the preview file for a specific footage
# allows html pages to pull previews for playback
def getPreview(request, footage_id):
    footage = get_object_or_404(Footage, pk=footage_id)
    if footage.preview:
        filetype = footage.preview.path.rsplit(".", 1)[-1]

        if filetype == 'mp4':
            return FileResponse(footage.preview.open('rb'), content_type='video/mp4')
        elif filetype == 'mp3':
            return FileResponse(footage.preview.open('rb'), content_type='audio/mp3')

# ------------ scene ------------------

def viewScenes(request):
    # get all scenes
    scene_list = Scene.objects.order_by("script_number")

    # creates new scene on POST
    if request.method == 'POST' and request.user.is_authenticated:
        form = NewSceneForm(request.POST)
        # check if form data is valid
        if form.is_valid():
            # save the form data to model
            form.save()
            form = NewSceneForm()
            return redirect('View_Scenes')
        else:
            messages.error(request, 'Please correct the following errors:')
    else:
        form = NewSceneForm()

    context = {"list": scene_list, "form": form}
    return render(request, "scene_list.html", context)

class SceneDeleteView(LoginRequiredMixin, DeleteView):
    model = Scene
    success_url = reverse_lazy('View_Scenes')

def editScene(request, script_number):
    scene = get_object_or_404(Scene, script_number=script_number)
    shot_list = Shot.objects.filter(scene=scene).order_by("shot")

    if request.method == 'POST' and request.user.is_authenticated:
        form = SceneForm(request.POST, instance=scene)

        simple_save_if_valid(form, request)
    else:
        form = SceneForm(instance=scene)
    
    shot_form = ShotInSceneForm(initial={'scene': scene})

    context = {"list": shot_list, "form": form, "shot_form": shot_form}
    return render(request, "scene_edit.html", context)

# ------------ shot ------------------

@login_required
def createShot(request):
    if request.method == 'POST':
        form = ShotForm(request.POST)
        
        simple_save_if_valid(form, request)
    else:
        form = ShotForm()

    context = {'form': form}
    return render(request, "generic.html", context)

@login_required
def deleteShot(request, scene_id, shot):
    if request.method == 'POST':
        item = get_object_or_404(Shot, scene_id=scene_id, shot=shot)
        item.delete()
        messages.info(request, "shot removed !!!")
    return redirect('Scene_Editor', scene_id)

@login_required
def addShotToScene(request, scene_id):
    if request.method == 'POST':
        form = ShotInSceneForm(request.POST)
        form.instance.scene_id = scene_id
        
        simple_save_if_valid(form, request)
    return redirect('Scene_Editor', scene_id)

def editShot(request, scene_id, shot):
    shot = get_object_or_404(Shot, scene_id=scene_id, shot=shot)

    if request.method == 'POST' and request.user.is_authenticated:
        form = ShotForm(request.POST, instance=shot)

        simple_save_if_valid(form, request)

        return redirect('Scene_Editor', scene_id)
    else:
        form = ShotForm(instance=shot)
    
    context = {'form': form}
    return render(request, "generic.html", context)

# ------------ FootageTake ------------------

@login_required
def addTakeToFootage(request, footage_id):
    if request.method == 'POST':
        form = AddTakeToFootageForm(request.POST)
        form.instance.footage_id = footage_id
        # check if form data is valid
        if form.is_valid():
            # create shot if not exists
            Shot.objects.get_or_create(
                scene = form.instance.take_scene,
                shot = form.instance.take_shot)

            # create take if not exists
            Take.objects.get_or_create(
                shot_scene = form.instance.take_scene,
                shot_name = form.instance.take_shot,
                take_no = form.instance.take_no)
            
            form.save()
            messages.info(request, "take saved !!!")
        else:
            messages.error(request, 'Please correct the following errors:')
    return redirect('Footage_Editor', footage_id)

@login_required
def deleteFootageTake(request, footage_id, take_scene, take_shot, take_no):
    if request.method == 'POST':
        item = get_object_or_404(FootageTake, take_scene=take_scene, take_shot=take_shot, take_no=take_no, footage_id=footage_id)
        item.delete()
        messages.info(request, "take removed !!!")
    return redirect('Footage_Editor', footage_id)

# saves take in footage
# also saves edits to footageTake relation
@login_required
def editFootageTake(request, footage_id, take_scene, take_shot, take_no):
    # only acts on POST
    if request.method == 'POST':
        # get FootageTake linking take to footage
        link = get_object_or_404(FootageTake, take_scene=take_scene, take_shot=take_shot, take_no=take_no, footage_id=footage_id)
        form = TakeInFootageForm(request.POST)

        # fill in missing feilds
        form.instance.shot_scene_id = take_scene
        form.instance.shot_name = take_shot
        form.instance.take_no = take_no

        # format time
        dt = datetime.datetime.strptime(form.data['start_time'], "%H:%M:%S")  # string to datetime conversion
        total_sec = dt.hour*3600 + dt.minute*60 + dt.second  # total seconds calculation
        time = datetime.timedelta(seconds=total_sec) 
        # save time to associated FootageTake
        link.start_time = time

        # if form is valid, save both the FootageTake and Take
        if form.is_valid():
            # save the form data to model
            link.save()
            form.save()
            messages.info(request, "take modified !!!")
        else:
            messages.error(request, 'Please correct the following errors:')
    return redirect('Footage_Editor', footage_id)

# ------------ Comment ------------------

class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment

    def get_success_url(self):
        return urlreverse('Footage_Editor', kwargs={'footage_id': self.object.footage_id})

class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    fields = ['time', 'comment']

    def get_success_url(self):
        return urlreverse('Footage_Editor', kwargs={'footage_id': self.object.footage_id})

@login_required
def addCommentToFootage(request, footage_id):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        form.instance.footage_id = footage_id

        simple_save_if_valid(form, request)

    return redirect('Footage_Editor', footage_id)
