from django.shortcuts import render, redirect
from django.http import HttpResponse

from reel_logger_app.models import Footage, Comment, Scene, Shot, Take, FootageUpload
from reel_logger_app.forms import UploadForm

def index(request):
    return HttpResponse("Hello, world. You're at the index.")

def fileupload(request):
    form = UploadForm(request.POST, request.FILES)
    if request.method == 'POST':
        files = request.FILES.getlist('footage')
        for f in files:
            f_ins = FootageUpload(footage = f)
            f_ins.save()
        return redirect('index')
    context = {'form': form}
    return render(request, "upload.html", context)