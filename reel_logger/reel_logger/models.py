from django.db import models

class Footage(models.Model):
    path = models.FilePathField()
    hash = models.CharField(max_length=32)
    length = models.DurationField()
    has_audio = models.BooleanField()
    has_video = models.BooleanField()
    notes = models.TextField()

    takes = None

class Comment(models.Model):
    footage = models.ForeignKey(Footage, on_delete=models.CASCADE)
    time = models.DurationField()
    comment = models.TextField()

class Scene(models.Model):
    script_number = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=128)
    description = models.TextField()

class Shot(models.Model):
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE)
    shot = models.CharField(max_length=64)
    description = models.TextField()

class Take(models.Model):
    footage = models.ManyToManyRel(field="takes", to=Footage)
    shot = models.ForeignKey(Shot, on_delete=models.CASCADE)
    take_no = models.PositiveSmallIntegerField()
    start_time = models.DurationField()
    marked_scene = models.PositiveSmallIntegerField()
    marked_shot = models.CharField(max_length=64)
    marked_take = models.PositiveSmallIntegerField()
    rating = models.SmallIntegerField()
    notes = models.TextField()

