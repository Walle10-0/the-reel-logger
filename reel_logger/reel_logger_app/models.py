from django.db import models
from hashlib import md5 as hash
import datetime 

from reel_logger.settings import MEDIA_ROOT

def get_footage_root():
    return MEDIA_ROOT + "footage/"

class Footage(models.Model):
    path = models.FilePathField(path=get_footage_root, blank=False, null=False, recursive=True, unique=True)
    hash = models.CharField(max_length=32, blank=True, editable=False)
    length = models.DurationField(blank=True, default=datetime.timedelta(0))
    has_audio = models.BooleanField(default=False)
    has_video = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    # takes in 'take_set' 
    # footagetake in 'footagetake_set' (I think)

    def save(self, *args, **kwargs):
        print(self.path)
        with open(self.path, "rb") as file:
            self.hash = hash(file.read()).hexdigest()
        super(Footage, self).save(*args, **kwargs)
    
    # custom print method
    def __str__(self):
        return "Footage('" + str(self.path) + "')"

class Comment(models.Model):
    footage = models.ForeignKey(Footage, on_delete=models.CASCADE)
    time = models.DurationField()
    comment = models.TextField()

class Scene(models.Model):
    script_number = models.PositiveSmallIntegerField(primary_key=True)
    title = models.CharField(max_length=128)
    description = models.TextField(blank=True)

    def __str__(self):
        return str(self.script_number) + ' - ' + self.title

class Shot(models.Model):
    pk = models.CompositePrimaryKey("scene_id", "shot")
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE)
    shot = models.CharField(max_length=64)
    description = models.TextField(blank=True)

    def __str__(self):
        return str(self.scene.script_number) + ' ' + self.shot

class Take(models.Model):
    pk = models.CompositePrimaryKey("shot_scene", "shot_name", "take_no")

    shot_scene = models.ForeignKey(Scene, on_delete=models.CASCADE)
    shot_name = models.CharField(max_length=64)
    shot = models.ForeignObject(Shot,
                                on_delete=models.CASCADE,
                                from_fields=("shot_scene", "shot_name"),
                                to_fields=("scene_id", "shot"))
    
    take_no = models.PositiveSmallIntegerField()
    marked_scene = models.PositiveSmallIntegerField(blank=True)
    marked_shot = models.CharField(max_length=64, blank=True)
    marked_take = models.PositiveSmallIntegerField(blank=True)
    rating = models.SmallIntegerField(blank=True)
    notes = models.TextField(blank=True)

    footage = models.ManyToManyField(
        Footage,
        through="FootageTake",
        through_fields=("take", "footage"),
    )

class FootageTake(models.Model):
    pk = models.CompositePrimaryKey("footage_id", "take_scene", "take_shot", "take_no")

    footage = models.ForeignKey(Footage, on_delete=models.CASCADE)
    take_scene = models.ForeignKey(Scene, on_delete=models.CASCADE)
    take_shot = models.CharField(max_length=64)
    take_no = models.PositiveSmallIntegerField()
    take = models.ForeignObject(Take,
                                on_delete=models.CASCADE,
                                from_fields=("take_scene", "take_shot", "take_no"),
                                to_fields=("shot_scene", "shot_name", "take_no"))

    start_time = models.DurationField()


