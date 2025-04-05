from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.core.files.storage import default_storage
from django.contrib import messages

from reel_logger_app.models import Footage, Comment, Scene, Shot, Take, FootageTake
from reel_logger_app.forms import FootageForm, TakeForm, SceneForm, ShotForm

def index(request):
    return HttpResponse("Hello, world. You're at the index.")

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
            return render(request,'form_edit.html',{'form':form})
    else:
        form = FootageForm(instance=footage, exclude="script_number")

    takes = FootageTake.objects.filter(footage=footage)

    print(takes)

    context = {'form': form, 'takes': takes}
    return render(request, "form_edit.html", context)

def viewScenes(request):
    scene_list = Scene.objects.order_by("script_number")

    if request.method == 'POST':
        form = SceneForm(request.POST)
        # check if form data is valid
        if form.is_valid():
            # save the form data to model
            form.save()
            form = SceneForm()
            return redirect('View_Scenes')
        else:
            messages.error(request, 'Please correct the following errors:')
    else:
        form = SceneForm()

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
    
    shot_form = ShotForm()

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
