'''
This file contains all the 'models'
They are basically templates for the objects represented by our tables.
Django builds the database based off these objects
It then handles building these objects from the database automatically
It also adds a few other calculated fields, like object references from foreign keys and others that I added.
'''
import os
from datetime import timedelta
from hashlib import md5 as hash

from django.db import models

from reel_logger.settings import MEDIA_ROOT
from reel_logger_app.previewHandler import generate_preview


def get_footage_root():
    return os.path.join(MEDIA_ROOT, "footage/")

class Footage(models.Model):
    # attributes for database
    path = models.FilePathField(path=get_footage_root, blank=False, null=False, recursive=True, unique=True)
    hash = models.CharField(max_length=32, blank=True, editable=False)
    length = models.DurationField(blank=True, default=timedelta(0))
    has_audio = models.BooleanField(default=False)
    has_video = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    logged = models.BooleanField(default=False)
    preview = models.FileField(upload_to='previews/', blank=True, null=True, editable=False)
    original_filename = models.CharField(max_length=32, blank=True, default="", editable=False)

    # takes in 'take_set' 
    # footagetake in 'footagetake_set'

    # computed attributes

    # returns name of the file from the path (eg. '00017.MTS')
    @property
    def filename(self):
        return os.path.basename(self.path)

    # returns th type of the file (eg. '.MTS')
    @property
    def filetype(self):
        return self.path.split('.')[-1]
    
    # returns th type of the PREVIEW file (only 'mp4' or 'mp3')
    @property
    def previewtype(self):
        return self.preview.path.split('.')[-1]
    
    @property
    def average_rating(self):
        ratings = list(self.take_set.values_list('rating', flat=True))
        if len(ratings) != 0:
            return sum(ratings) / len(ratings)
        else:
            return 0
    
    @property
    def max_rating(self):
        ratings = list(self.take_set.values_list('rating', flat=True))
        if len(ratings) != 0:
            return max(ratings)
        else:
            return 0
    
    # helper function
    # custom move function to ensure changing file path happens smoothly
    def move(self, new_path):
        print(new_path)
        try :
            os.rename(self.path, new_path)
            print("Source path renamed to destination path successfully.")
            self.path = new_path

        except Exception as error:
            print(error)
        
        with open(self.path, "rb") as file:
            newhash = hash(file.read()).hexdigest()
            if newhash != self.hash:
                print("hash changed!")
        
        self.save()

    # overrides

    # override save so that values like the hash are auto calculated
    def save(self, *args, **kwargs):
        print("models.py" + self.path)
        with open(self.path, "rb") as file:
            newhash = hash(file.read()).hexdigest()

            # only run if hash is changed
            if newhash != self.hash:
                print("hash changed! recalculate video")
                self.hash = newhash

                # create preview and autofill length, hash_video, has_audio
                generate_preview(self)
        super(Footage, self).save(*args, **kwargs)
    
    # custom print method
    def __str__(self):
        return "Footage('" + str(self.path) + "')"
    
    # override delete so that the associated files are deleted
    def delete(self, *args, **kwargs):
        if os.path.exists(self.path):
            os.remove(self.path)
        self.preview.delete(save=False)
        super(Footage, self).delete(*args, **kwargs)

class Comment(models.Model):
    # attributes for database
    footage = models.ForeignKey(Footage, on_delete=models.CASCADE)
    time = models.DurationField()
    comment = models.TextField()

class Scene(models.Model):
    script_number = models.PositiveSmallIntegerField(primary_key=True)
    title = models.CharField(max_length=128)
    description = models.TextField(blank=True)

    # custom print method
    def __str__(self):
        return str(self.script_number) + ' - ' + self.title

class Shot(models.Model):
    # primary key constraint
    pk = models.CompositePrimaryKey("scene_id", "shot")
    # attributes for database
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE)
    shot = models.CharField(max_length=64)
    description = models.TextField(blank=True)

    # custom print method
    def __str__(self):
        return str(self.scene.script_number) + ' ' + self.shot

class Take(models.Model):
    # primary key constraint
    pk = models.CompositePrimaryKey("shot_scene", "shot_name", "take_no")

    # shot reference
    shot_scene = models.ForeignKey(Scene, on_delete=models.CASCADE)
    shot_name = models.CharField(max_length=64)
    shot = models.ForeignObject(Shot,
                                on_delete=models.CASCADE,
                                from_fields=("shot_scene", "shot_name"),
                                to_fields=("scene_id", "shot"))
    
    # other attributes for database
    take_no = models.PositiveSmallIntegerField()
    marked_scene = models.PositiveSmallIntegerField(blank=True)
    marked_shot = models.CharField(max_length=64, blank=True)
    marked_take = models.PositiveSmallIntegerField(blank=True)
    rating = models.SmallIntegerField(blank=True, default=0)
    notes = models.TextField(blank=True)

    # many to many relationship with footage
    footage = models.ManyToManyField(
        Footage,
        through="FootageTake",
        through_fields=("take", "footage"),
    )

    # override save function
    # so that marked scene, shot, take are auto-filled with actual scene, shot take iff empty
    def save(self, *args, **kwargs):
        if not self.marked_scene:
            self.marked_scene = self.shot_scene_id
        if not self.marked_shot:
            self.marked_shot = self.shot_name
        if not self.marked_take:
            self.marked_take = self.take_no
        super(Take, self).save(*args, **kwargs)

class FootageTake(models.Model):
    # primary key constraint
    pk = models.CompositePrimaryKey("footage_id", "take_scene", "take_shot", "take_no")

    # footage reference (simple)
    footage = models.ForeignKey(Footage, on_delete=models.CASCADE)

    # take reference (not so simple)
    take_scene = models.ForeignKey(Scene, on_delete=models.CASCADE)
    take_shot = models.CharField(max_length=64)
    take_no = models.PositiveSmallIntegerField()
    take = models.ForeignObject(Take,
                                on_delete=models.CASCADE,
                                from_fields=("take_scene", "take_shot", "take_no"),
                                to_fields=("shot_scene", "shot_name", "take_no"))

    # other attributes for database
    start_time = models.DurationField(blank=True, default=timedelta(0))
