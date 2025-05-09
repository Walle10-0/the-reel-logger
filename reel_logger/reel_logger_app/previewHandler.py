'''
Not part of Django
This file handles creating the preview and ffmpeg.
I moved it here for increased modularity and to de-clutter models.py
We need to generate mp4 and mp3 previews of all media so that we can play it in a web browser
'''
from datetime import timedelta
from math import ceil

import ffmpeg

from django.core.files import File

# extracts info from media
def _get_media_info(input_path):
    # extract data from media
    probe = ffmpeg.probe(input_path)
    video_stream = next((s for s in probe['streams'] if s['codec_type'] == 'video'), None)
    audio_stream = next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)

    # figure out if media has audio or video
    media_info = {
        'has_video': video_stream is not None,
        'has_audio': audio_stream is not None,
    }

    # extract duration
    format_info = probe.get('format', {})
    if 'duration' in format_info:
        total_seconds = ceil(float(format_info['duration']))
        media_info['duration'] = timedelta(seconds=total_seconds)

    # extract video specific information
    if video_stream:
        media_info.update({
            'width': int(video_stream['width']),
            'height': int(video_stream['height']),
            'framerate': eval(video_stream['r_frame_rate']),
        })

    # extract audio specific information
    if audio_stream:
        media_info.update({
            'sample_rate': int(audio_stream['sample_rate']),
        })

    return media_info
    
# creates preview and auto-fills attributes (has_video, has_audio, length)
def generate_preview(footage):
    # read media
    info = _get_media_info(footage.path)
    input_stream = ffmpeg.input(footage.path)

    # separate audio and video streams for filtering
    video_stream = input_stream.video if info.get('has_video') else None
    audio_stream = input_stream.audio if info.get('has_audio') else None

    # check for video specific stuff
    if info.get('has_video', False):
        footage.has_video = True
        default_width = 720

        # if video is in high definition, downgrade it
        if info.get('width', default_width) > default_width:
            new_height = int(info.get('height') * default_width / info.get('width'))

            # Make sure new height is divisible by 2
            if new_height % 2 != 0:
                new_height += 1  # Or subtract 1 to round down

            video_stream = video_stream.filter('scale', default_width, new_height)
        
        # if video has a high framerate, downgrade it
        if info.get('framerate', 24) > 24:
            video_stream = video_stream.filter('fps', fps=24)

        # set output type to mp4 to so we know to render it later as an mp4
        output_type = "mp4"
    else:
        footage.has_video = False
    
    # check for audio specific stuff
    if info.get('has_audio'):
        footage.has_audio = True

        # if sample rate is high, downgrade it
        if info.get('sample_rate', 44100) > 44100:
            audio_stream = audio_stream.filter('aresample', 44100)

        # if there was no video data (but there is audio data), then we render as an mp3
        if not info.get('has_video'):
            output_type = "mp3"
    else:
        footage.has_audio = False
    
    # put the audio and video back together
    output_args = []
    if video_stream:
        output_args.append(video_stream)
    if audio_stream:
        output_args.append(audio_stream)

    # if there is any data to output, render it
    if output_args and output_type:
        # converts media
        ffmpeg.output(*output_args, f"tmp.{output_type}").run(overwrite_output=True)

        # saves file to previews
        with open(f"tmp.{output_type}", 'rb') as f:
            footage.preview.save(f'{footage.hash}.{output_type}', File(f), save=False)
    else:
        print("No preview created")
                
    # get time
    if 'duration' in info:
        footage.length = info["duration"]