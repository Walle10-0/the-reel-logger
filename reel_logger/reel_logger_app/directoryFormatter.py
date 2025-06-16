'''
not related to Django
This is a separate file I made to handle creating directories and organizing footage.
The idea behind it is to modularize the code.
'''
import os

from reel_logger.settings import MEDIA_ROOT
from reel_logger_app.models import Footage, Scene, Shot, Take

def get_footage_root():
    return os.path.join(MEDIA_ROOT, "footage/")

# small function to create the directory only if it does not exist
def mkdir_if_not_exists(path):
    newPath = get_footage_root() + path
    if not os.path.isdir(newPath): 
        os.makedirs(newPath)
    return newPath

# small function to convert rating to a symbol
# completely arbitrary - may be changed later
def ratingToSymbol(rating):
    if rating < -15:
        return 'XXX'
    if rating < -10:
        return 'XX'
    if rating < -5:
        return 'X'
    if rating < 0:
        return 'x'
    if rating < 5:
        return '^'
    if rating < 10:
        return 'o'
    else:
        return 'O'

# this function makes all the directories ahead of time
def make_all_directories(folder_sort_type):
    # create directories
    if folder_sort_type == 1:
        mkdir_if_not_exists("logged")
    else:
        # get all scene numbers
        scenes = Scene.objects.all().values_list('script_number', flat=True)

        # make scene directories
        for scene in scenes:
            mkdir_if_not_exists(f"scene{scene}")

        if folder_sort_type > 2:
            # get all shots
            shots = list(Shot.objects.all().values_list('scene', 'shot'))

            # make shot directories
            for scene, shot in shots:
                mkdir_if_not_exists(os.path.join(f"scene{scene}", f"shot{scene}{shot}"))

            if folder_sort_type > 3:
                # get all takes
                takes = list(Take.objects.all().values_list('shot_scene', 'shot_name', 'take_no'))

                # make take directories
                for scene, shot, take in takes:
                    mkdir_if_not_exists(os.path.join(f"scene{scene}", f"shot{scene}{shot}", f"take{scene}{shot}{take}"))

# this function finds a single take for the entire footage based on the settings
# used in the filename and directory sorting
def getTake(form, footage):
    scene = 0
    shot = ''
    take = footage.id

    if footage.take_set:
        take_set = footage.take_set.order_by('shot_scene', 'shot_name', 'take_no')
        preferred_order = form["for_multiple_takes_use"].value()

        if preferred_order == '2':
            take_set = take_set.latest()
        if preferred_order == '3':
            count = take_set.count()
            take_set = take_set[int(round(count/2))]
        else:
            take_set = take_set.first()
        
        if take_set:
            if take_set.shot_scene:
                scene = take_set.shot_scene.script_number
            shot = take_set.shot_name
            take = take_set.take_no

            if form['base_takes_on'].value() == '2':
                if take_set.marked_scene:
                    scene = take_set.marked_scene
                if take_set.marked_shot:
                    shot = take_set.marked_shot
                if take_set.marked_take:
                    take = take_set.marked_take

    return scene, shot, take

# generates a filename based on the filename settings
def get_filename(form, footage, scene, shot, take):
    filename = []
    delim = '-'

    if form['include_uid'].value():
        filename.append(str(footage.id))
    if form['include_hash'].value():
        filename.append(footage.hash)
    if form['include_original_filename'].value():
        filename.append(footage.original_filename)
    if form['include_take_in_filename'].value():
        filename.append(f"{scene}{shot}")
        filename.append(f"{take}")
    if form['include_rating'].value() != '1':
        if form['use_rating'].value() == '2':
            rating = footage.max_rating
        else:
            rating = round(footage.average_rating)
        if form['include_rating'].value() == '3':
            filename.append(ratingToSymbol(rating))
        else:
            filename.append(str(rating))
    if not filename:
        filename.append(footage.id)

    return f"{delim.join(filename)}.{footage.filetype}"

# figures out the correct folder based on the folder settings
# it creates it if it does not exist
def get_folder(form, scene, shot, take):
    folder_sort_type = int(form['sort_folders_by'].value())

    if folder_sort_type == 1:
        return mkdir_if_not_exists("logged")
    else:
        newPath = mkdir_if_not_exists(f"scene{scene}")

        if folder_sort_type > 2:
            newPath = mkdir_if_not_exists(os.path.join(f"scene{scene}", f"shot{scene}{shot}"))

            if folder_sort_type > 3:
                newPath = mkdir_if_not_exists(os.path.join(f"scene{scene}", f"shot{scene}{shot}", f"take{scene}{shot}{take}"))
        
        return newPath

# simple function to move the footage
# the hard work is done by the other functions
def moveFootage(form, footage):
    scene, shot, take = getTake(form, footage)
    filename = get_filename(form, footage, scene, shot, take)
    filepath = get_folder(form, scene, shot, take)
    filepath = os.path.join(filepath, filename)
    footage.move(filepath)

# this organizes all the footage into the proper directories
def formatFootageDirectory(form, footage_list):
    # filter for logged footage
    if form['only_logged_footage'].value():
        footage_list = footage_list.filter(logged=True)
    
    # create all directories ahead of time if the user wants to
    if not form['only_create_used_directories'].value():
        make_all_directories(int(form['sort_folders_by'].value()))

    # move all the footage
    for footage in footage_list:
        moveFootage(form, footage)
    
