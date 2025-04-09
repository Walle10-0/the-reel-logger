from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.core.files.storage import default_storage
from django.contrib import messages

import datetime

from reel_logger_app.models import Footage, Comment, Scene, Shot, Take, FootageTake
from reel_logger_app.forms import FootageForm, TakeForm, SceneForm, ShotForm, NewSceneForm, ShotInSceneForm, AddTakeToFootageForm, TakeInFootageForm

def index(request):
    return render(request, "index.html")

def fileupload(request):    
    if request.method == 'POST':
        first = ""
        for file in request.FILES.getlist('posts'):
            print(file)

            new_filename = default_storage.generate_filename("footage/unlogged/" + file.name)
            new_filename = default_storage.save(new_filename, file)
            full_filename = default_storage.location + '/' + new_filename
            print(full_filename)

            newfoot = Footage.objects.create(path=full_filename)

            if first == "":
                first = str(newfoot.id) + "/edit/"
        messages.success(request, 'The files have been uploaded successfully.')
        return redirect(first)
    return render(request, "upload.html")

def viewFootage(request):
    footage_list = Footage.objects.order_by("path")

    context = {"list": footage_list}
    return render(request, "footage_list.html", context)

def editFootage(request, footage_id):
    footage = get_object_or_404(Footage, pk=footage_id)

    if request.method == 'POST':
        form = FootageForm(request.POST, instance=footage)

        # check if form data is valid
        if form.is_valid():
            # save the form data to model
            form.save()
        else:
            messages.error(request, 'Please correct the following errors:')
            #return render(request,'form_edit.html',{'form':form})
    else:
        form = FootageForm(instance=footage)
    
    take_to_footage = AddTakeToFootageForm(initial={'footage': footage})

    # get all take forms
    all_takes = []
    for take in footage.take_set.all():
        start = FootageTake.objects.get(footage=footage, take=take).start_time
        newTakeForm = TakeInFootageForm(instance=take, initial={"start_time": start})
        all_takes.append(newTakeForm)

    context = {'form': form, "take_to_footage": take_to_footage, "takes": all_takes}
    return render(request, "footage_edit.html", context)

def viewScenes(request):
    scene_list = Scene.objects.order_by("script_number")

    if request.method == 'POST':
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

def deleteScene(request, script_number):
    if request.method == 'POST':
        item = get_object_or_404(Scene, script_number=script_number)
        item.delete()
        messages.info(request, "scene removed !!!")
    return redirect('View_Scenes')

def editScene(request, script_number):
    scene = get_object_or_404(Scene, script_number=script_number)
    shot_list = Shot.objects.filter(scene=scene).order_by("shot")

    if request.method == 'POST':
        form = SceneForm(request.POST, instance=scene)

        if form.is_valid():
            # save the form data to model
            form.save()
        else:
            messages.error(request, 'Please correct the following errors:')
    else:
        form = SceneForm(instance=scene)
    
    shot_form = ShotInSceneForm(initial={'scene': scene})

    context = {"list": shot_list, "form": form, "shot_form": shot_form}
    return render(request, "scene_edit.html", context)

def createShot(request):
    if request.method == 'POST':
        form = ShotForm(request.POST)
        # check if form data is valid
        if form.is_valid():
            # save the form data to model
            form.save()
        else:
            messages.error(request, 'Please correct the following errors:')
    else:
        form = ShotForm()

    context = {'form': form}
    return render(request, "generic.html", context)

def deleteShot(request, scene_id, shot):
    if request.method == 'POST':
        item = get_object_or_404(Shot, scene_id=scene_id, shot=shot)
        item.delete()
        messages.info(request, "shot removed !!!")
    return redirect('Scene_Editor', scene_id)

def addShotToScene(request, scene_id):
    if request.method == 'POST':
        form = ShotInSceneForm(request.POST)
        form.instance.scene_id = scene_id
        # check if form data is valid
        if form.is_valid():
            # save the form data to model
            form.save()
            messages.info(request, "shot saved !!!")
        else:
            messages.error(request, 'Please correct the following errors:')
    return redirect('Scene_Editor', scene_id)

def editShot(request, scene_id, shot):
    shot = get_object_or_404(Shot, scene_id=scene_id, shot=shot)

    if request.method == 'POST':
        form = ShotForm(request.POST, instance=shot)

        if form.is_valid():
            # save the form data to model
            form.save()
        else:
            messages.error(request, 'Please correct the following errors:')
    else:
        form = ShotForm(instance=shot)
    
    context = {'form': form}
    return render(request, "generic.html", context)

def addTakeToFootage(request, footage_id):
    if request.method == 'POST':
        form = AddTakeToFootageForm(request.POST)
        form.instance.footage_id = footage_id
        # check if form data is valid
        if form.is_valid():
            # create if not exists
            Take.objects.get_or_create(
                shot_scene = form.instance.take_scene,
                shot_name = form.instance.take_shot,
                take_no = form.instance.take_no)
            
            form.save()
            messages.info(request, "take saved !!!")
        else:
            messages.error(request, 'Please correct the following errors:')
    return redirect('Footage_Editor', footage_id)

def deleteFootageTake(request, footage_id, take_scene, take_shot, take_no):
    if request.method == 'POST':
        item = get_object_or_404(FootageTake, take_scene=take_scene, take_shot=take_shot, take_no=take_no, footage_id=footage_id)
        item.delete()
        messages.info(request, "take removed !!!")
        return redirect('Footage_Editor', footage_id)

def editFootageTake(request, footage_id, take_scene, take_shot, take_no):
    if request.method == 'POST':
        link = get_object_or_404(FootageTake, take_scene=take_scene, take_shot=take_shot, take_no=take_no, footage_id=footage_id)
        take = get_object_or_404(FootageTake, take_scene=take_scene, take_shot=take_shot, take_no=take_no)
        form = TakeInFootageForm(request.POST)
        
        # save other information
        dt = datetime.datetime.strptime(form.data['start_time'], "%H:%M:%S")  # string to datetime conversion
        total_sec = dt.hour*3600 + dt.minute*60 + dt.second  # total seconds calculation
        time = datetime.timedelta(seconds=total_sec) 
        link.start_time = time

        if form.is_valid():
            # save the form data to model
            link.save()
            form.save()
            messages.info(request, "take modified !!!")
        else:
            messages.error(request, 'Please correct the following errors:')
        return redirect('Footage_Editor', footage_id)

def deleteTake(request, shot_scene, shot_name, take_no, redirect_footage=None):
    if request.method == 'POST':
        item = get_object_or_404(Take, shot_scene=shot_scene, shot_name=shot_name, take_no=take_no)
        item.delete()
        messages.info(request, "take removed !!!")
    if redirect_footage:
        return redirect('Footage_Editor', redirect_footage)
    else:
        return redirect('index')
