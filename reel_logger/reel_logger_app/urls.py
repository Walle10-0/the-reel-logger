from django.conf import settings
from django.urls import path
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('upload/', views.fileupload, name = "File_Uploads"),
    path('footage/', views.viewFootage, name = "View_Footage"),
    path("footage/<int:footage_id>/edit/", views.editFootage, name="Footage_Editor"),
    path("footage/<int:footage_id>/preview/", views.getPreview, name="Footage_Preview"),
    path("footage/<int:pk>/delete/", views.FootageDeleteView.as_view(), name="Delete_Footage"),
    path("footage/<int:footage_id>/add take/", views.addTakeToFootage, name="Add_Take_To_Footage"),
    path("footage/<int:footage_id>/remove take/<int:take_scene>/<str:take_shot>/<int:take_no>/", views.deleteFootageTake, name="Remove_Take_From_Footage"),
    path("footage/<int:footage_id>/edit take/<int:take_scene>/<str:take_shot>/<int:take_no>/", views.editFootageTake, name="Edit_Take_In_Footage"),
    path("footage/<int:footage_id>/add comment/", views.addCommentToFootage, name="Add_Comment_To_Footage"),
    path('scene/', views.viewScenes, name = "View_Scenes"),
    path("scene/<int:script_number>/", views.editScene, name="Scene_Editor"),
    path("scene/<int:pk>/delete/", views.SceneDeleteView.as_view(), name="Delete_Scene"),
    path("scene/<int:scene_id>/add shot/", views.addShotToScene, name="Add_Shot_To_Scene"),
    path('shot/new/', views.createShot, name = "Create_Shot"),
    path('shot/<int:scene_id>/<str:shot>/delete/', views.deleteShot, name = "Delete_Shot"),
    path("shot/<int:scene_id>/<str:shot>/", views.editShot, name="Shot_Editor"),
    path("comment/<int:pk>/delete/", views.CommentDeleteView.as_view(), name="Delete_Comment"),
    path("comment/<int:pk>/edit/", views.CommentUpdateView.as_view(), name="Edit_Comment"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)