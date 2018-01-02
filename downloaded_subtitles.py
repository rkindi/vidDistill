# Helper functions to determine if subtitles or punctuated subtitles have been downloaded and stored.

import urllib.parse as urlparse # https://stackoverflow.com/questions/5074803/retrieving-parameters-from-a-url
from pathlib import Path

from task_manager import *
from app import db
from models import *

def subs_already_downloaded(youtube_url):
    """
        Returns True if subtitles already downloaded. Returns False otherwise.
    """
    video_id = get_video_id_from_url(youtube_url)
    exists = db.session.query(db.session.query(TaskEntry).filter_by(task_id=video_id, status=1).exists()).scalar() # indicates if exists in db
    if exists:
        print("Subtitles for " + video_id + " already exist.")
    else:
        print("Subtitles for " + video_id + " do not already exist.")
    return exists

def punctuated_text_already_downloaded(video_id):
    """
        Returns True if punctuated text already downloaded. Returns False otherwise.
    """
    exists = db.session.query(db.session.query(TaskEntry).filter_by(task_id=video_id, status=2).exists()).scalar()
    if exists:
        print("Punctuated subtitles for " + video_id + " already exist.")
    else:
        print("Punctuated subtitles for " + video_id + " do not already exist.")
    return exists