from django.db import models
from hashlib import md5 as hash

from reel_logger.settings import MEDIA_ROOT

def get_footage_root():
    return MEDIA_ROOT + "footage/"

class Footage(models.Model):
    path = models.FilePathField(path=get_footage_root, blank=False, null=False, recursive=True, unique=True)
    hash = models.CharField(max_length=32, blank=True, editable=False)
    length = models.DurationField(blank=True, default=0)
    has_audio = models.BooleanField(default=False)
    has_video = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    takes = None

    def save(self, *args, **kwargs):
        print(self.path)
        with open(self.path, "rb") as file:
            self.hash = hash(file.read()).hexdigest()
        super(Footage, self).save(*args, **kwargs)

class Comment(models.Model):
    footage = models.ForeignKey(Footage, on_delete=models.CASCADE)
    time = models.DurationField()
    comment = models.TextField()

class Scene(models.Model):
    script_number = models.PositiveSmallIntegerField(unique=True)
    title = models.CharField(max_length=128)
    description = models.TextField(blank=True)

class Shot(models.Model):
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE)
    shot = models.CharField(max_length=64)
    description = models.TextField(blank=True)

class Take(models.Model):
    footage = models.ManyToManyRel(field="takes", to=Footage)
    shot = models.ForeignKey(Shot, on_delete=models.CASCADE)
    take_no = models.PositiveSmallIntegerField()
    start_time = models.DurationField()
    marked_scene = models.PositiveSmallIntegerField()
    marked_shot = models.CharField(max_length=64)
    marked_take = models.PositiveSmallIntegerField()
    rating = models.SmallIntegerField()
    notes = models.TextField(blank=True)

class FootageUpload(models.Model):
    footage = models.FileField(upload_to='footage/unlogged/')

    class Meta:
        db_table = "reel_logger_app_footage_upload"
