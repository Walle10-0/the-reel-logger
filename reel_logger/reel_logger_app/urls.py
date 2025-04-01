from django.conf import settings
from django.urls import path
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('upload', views.fileupload, name = "File_Uploads"),
    path("<int:footage_id>/edit/", views.editFootage, name="Footage_Editor"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)