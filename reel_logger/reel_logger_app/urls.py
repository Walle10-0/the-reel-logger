from django.conf import settings
from django.urls import path
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('upload', views.fileupload, name = "File_Uploads"),
    path("footage/<int:footage_id>/edit/", views.editFootage, name="Footage_Editor"),
    path('scene', views.viewScenes, name = "View_Scenes"),
    path("scene/<int:script_number>/", views.editScene, name="Scene_Editor"),
    path("scene/<int:script_number>/delete", views.deleteScene, name="Delete_Scene"),
    path('shot/new', views.createShot, name = "Create_Shot"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)