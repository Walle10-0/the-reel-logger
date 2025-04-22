import os
from datetime import timedelta
from math import ceil
from hashlib import md5 as hash

from django.db import models
from django.core.files import File

import ffmpeg

from reel_logger.settings import MEDIA_ROOT


def get_footage_root():
    return MEDIA_ROOT + "footage/"

class Footage(models.Model):
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
    # footagetake in 'footagetake_set' (I think)

    @property
    def filename(self):
        return self.path.split('/')[-1]
    
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

    # extracts info from media
    def _get_media_info(self, input_path):
        probe = ffmpeg.probe(input_path)
        video_stream = next((s for s in probe['streams'] if s['codec_type'] == 'video'), None)
        audio_stream = next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)

        media_info = {
            'has_video': video_stream is not None,
            'has_audio': audio_stream is not None,
        }

        format_info = probe.get('format', {})
        if 'duration' in format_info:
            total_seconds = ceil(float(format_info['duration']))
            media_info['duration'] = timedelta(seconds=total_seconds)

        if video_stream:
            media_info.update({
                'width': int(video_stream['width']),
                'height': int(video_stream['height']),
                'framerate': eval(video_stream['r_frame_rate']),
            })

        if audio_stream:
            media_info.update({
                'sample_rate': int(audio_stream['sample_rate']),
            })

        return media_info
    
    # creates preview and auto-fills attributes
    def generate_preview(self):
        info = self._get_media_info(self.path)
        input_stream = ffmpeg.input(self.path)

        video_stream = input_stream.video if info.get('has_video') else None
        audio_stream = input_stream.audio if info.get('has_audio') else None

        if info.get('has_video', False):
            self.has_video = True
            default_width = 720

            if info.get('width', default_width) > default_width:
                new_height = int(info.get('height') * default_width / info.get('width'))

                # Make sure new height is divisible by 2
                if new_height % 2 != 0:
                    new_height += 1  # Or subtract 1 to round down

                video_stream = video_stream.filter('scale', default_width, new_height)
            if info.get('framerate', 24) > 24:
                video_stream = video_stream.filter('fps', fps=24)

            output_type = "mp4"
        else:
            self.has_video = False
        if info.get('has_audio'):
            self.has_audio = True

            if info.get('sample_rate', 44100) > 44100:
                audio_stream = audio_stream.filter('aresample', 44100)

            if not info.get('has_video'):
                output_type = "mp3"
        else:
            self.has_audio = False
                
        output_args = []
        if video_stream:
            output_args.append(video_stream)
        if audio_stream:
            output_args.append(audio_stream)

        if output_args and output_type:
            ffmpeg.output(*output_args, f"tmp.{output_type}").run(overwrite_output=True)

            with open(f"tmp.{output_type}", 'rb') as f:
                self.preview.save(f'{self.hash}.{output_type}', File(f), save=False)
        else:
            print("No preview created")
                
        # get time
        if 'duration' in info:
            self.length = info["duration"]


    def save(self, *args, **kwargs):
        print(self.path)
        with open(self.path, "rb") as file:
            newhash = hash(file.read()).hexdigest()
            if newhash != self.hash:
                print("hash changed! recalculate video")
                self.hash = newhash

                # create preview
                self.generate_preview()
        super(Footage, self).save(*args, **kwargs)
    
    # custom print method
    def __str__(self):
        return "Footage('" + str(self.path) + "')"
    
    def delete(self, *args, **kwargs):
        if os.path.exists(self.path):
            os.remove(self.path)
        self.preview.delete(save=False)
        super(Footage, self).delete(*args, **kwargs)

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
    rating = models.SmallIntegerField(blank=True, default=0)
    notes = models.TextField(blank=True)

    footage = models.ManyToManyField(
        Footage,
        through="FootageTake",
        through_fields=("take", "footage"),
    )

    def save(self, *args, **kwargs):
        if not self.marked_scene:
            self.marked_scene = self.shot_scene_id
        if not self.marked_shot:
            self.marked_shot = self.shot_name
        if not self.marked_take:
            self.marked_take = self.take_no
        super(Take, self).save(*args, **kwargs)

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


