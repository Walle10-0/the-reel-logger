from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.core.files.storage import default_storage
from django.contrib import messages

from reel_logger_app.models import Footage, Comment, Scene, Shot, Take
from reel_logger_app.forms import FootageForm, TakeForm

def index(request):
    return HttpResponse("Hello, world. You're at the index.")

def fileupload(request):    
    if request.method == 'POST':
        for file in request.FILES.getlist('posts'):
            print(file)
            new_filename = default_storage.generate_filename("footage/unlogged/" + file.name)
            new_filename = default_storage.save(new_filename, file)
            full_filename = default_storage.location + '/' + new_filename
            print(full_filename)
            newfoot = Footage.objects.create(path=full_filename)
        messages.success(request, 'The files have been uploaded successfully.')
        return redirect(str(newfoot.id) + "/edit/")
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
        form = FootageForm(instance=footage)

    takes = TakeForm()

    print(form.is_bound)

    context = {'form': form, 'takes': takes}
    return render(request, "form_edit.html", context)
