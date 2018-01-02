# Various functions to manage/create/update task entries in the database.

import urllib.parse as urlparse
from pathlib import Path
import psycopg2
from app import db
from models import *

def get_video_id_from_url(youtube_url):
    '''
    Returns the v URL param from a YouTube URL. Only works on URLs with a v param.
    :param youtube_url: A YouTube URL of the form https://www.youtube.com/watch?v=<video_id>
    :return: The video_id of the supplied YouTube video URL
    '''
    parsed = urlparse.urlparse(youtube_url)
    video_id = urlparse.parse_qs(parsed.query)['v'][0]
    return video_id

def set_task_with_ratio(task_id, status, message=None):
    '''
    Finds the row with the supplied task_id and sets the status and times to the supplied status and message respectively.
    If message is None (or not supplied), no value for times is assigned and just the status is updated.
    :param task_id: task_id for row in database. precondition: task_id must be of form <vid_id>@<ratio>
    :param status: status number to set for the row with the task_id supplied
    :param message: 'times' to set for the row with the task_id supplied (optional)
    '''
    target_task = db.session.query(TaskEntry).filter_by(task_id=task_id).first()
    target_task.status = status
    if message != None:
        target_task.times = message
    db.session.commit()

def set_task_without_ratio(task_id, ratio, status, subs=None, punct_subs=None):
    '''
    Finds the row with the supplied task_id and sets the status as well as the subs or punct_subs if specified.
    The status value gets carried over to the entry with task_id <vid_id>@<ratio> based off the specified ratio.
    :param task_id: task_id for row in database. precondition: task_id must be of form <vid_id> (don't include the ratio)
    :param ratio: ratio that the user provided must still be provided. This is so that this function can update the status of the entry of task_id <vid_id>@<ratio> bases off of changes to entry with task_id <vid_id>
    :param status: status number to set for this task
    :param subs: subtitles to store (the text of an SRT file) (optional)
    :param punct_subs: punctuated text to store (optional)
    '''
    target_task = db.session.query(TaskEntry).filter_by(task_id=task_id).first()
    target_task.status = status
    if subs != None:
        target_task.subs = subs
    if punct_subs != None:
        target_task.punct_subs = punct_subs
    db.session.commit()
    set_task_with_ratio(task_id + "@" + str(ratio), status)

def task_not_inserted(task_id):
    '''
    Returns True if a task with the specified task_id exists in the database. Returns False otherwise.
    :param task_id: task_id for the task
    :return: True if entry with specified task_id is present in database, False otherwise
    '''
    exists = db.session.query(db.session.query(TaskEntry).filter_by(task_id=task_id).exists()).scalar()
    return not exists

def create_task(task_id, status):
    '''
    Create a task in the database with the specified task_id and status. All other attributes are initialized to empty strings.
    If there already exists an entry in the database with the specified task_id, this function doesn't do anything
    :param task_id: the task_id desired for the newly created entry in the database
    :param status: the status desired for the newly created entry in the database
    '''
    if task_not_inserted(task_id):
        if '@' in task_id:
            db.session.add(TaskEntry(task_id, status, "", "", "", 1))
        else:
            db.session.add(TaskEntry(task_id, status, "", "", "", 0))
        db.session.commit()

def get_task_status(task_id):
    '''
    Returns the status of entry with the task_id specified. Precondition: Entry with task_id exists in database.
    :param task_id: the task_id of the entry the caller wants the status for
    :return: the status of the entry with the task_id specified
    '''
    target_task = db.session.query(TaskEntry).filter_by(task_id=task_id).first()
    return target_task.status

def get_entire_row(task_id):
    '''
    Returns a tuple with the task_id, status, times, subs, punct_subs, and task_type of the entry in the database with the supplied task_id.
    Precondition: an entry with the specified task_id exists in the database.
    :param task_id: the task_id of the entry in the database whose information the caller wants
    :return: a tuple organized as follows: (task_id, status, times, subs, punct_subs, task_type)
    '''
    target_task = db.session.query(TaskEntry).filter_by(task_id=task_id).first()
    return (target_task.task_id, target_task.status, target_task.times, target_task.subs, target_task.punct_subs, target_task.task_type)