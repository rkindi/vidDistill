# Defines how the database is created.

from app import db

class TaskEntry(db.Model):

    """
        Represents the model for the PostgreSQL database with the subtitle information. The database is designed so that all information
        for the vidDistill application can be stored on a single table (to avoid additional complexity on Heroku).
    """
    
    __name__ = "tasks"

    ''' 
    
        task_id can have two forms:
            1. <vid_id>@<ratio> where <vid_id> is the video id is the Youtube video id and <ratio> is a multiple of 0.1 from 0.1 - 1.0 representing
               the ratio of the original video's transcript's length desired for the shortened output video. Example of video id: The video id for
               Sir Ken Robinson's 'Do schools kill creativity?' (which can be found at https://www.youtube.com/watch?v=iG9CE55wbtY) is iG9CE55wbtY.
            2. <vid_id>
        
        The reason for the two types of IDs is that downloading and punctuating subs is an expensive operation. Say user A wants to shorten
        video X to 0.1 of the original. She finds the video is too short, so she then tries to shorten video X to 0.2 of the original. We don't want to
        download the subtitles and punctuate the text twice in this scenario. So we use a row in the database with a task_id that is just <vid_id> for the video
        X and then we have 2 additional rows <vid_id>@0.1 and <vid_id>@0.2 that are constructed using data that was previously entered into the <vid_id> row.
        
        Perhaps one might use two different tables to store such information, but I opted to use 1 to simply things while I was getting set up with
        Heroku for the first time.
        
     '''
    task_id = db.Column(db.String, nullable=False)
    '''
        If the status corresponds to a TaskEntry whose task_id is of the form <vid_id>, then status can be the following values:
            0 - no progress has been made on the task
            1 - finished downloading subs
            2 - finished punctuating the downloaded subs    
        
        If the status corresponds to a TaskEntry whose task_id is of the form <vid_id>@<ratio>, then status can be the following values:
            0 - no progress has been made on the task (reflected to match the status of the entry with task_id = to just <vid_id>)
            1 - finished downloading subs (reflected to match the status of the entry with task_id = to just <vid_id>)
            2 - finished punctuating the downloaded subs (reflected to match the status of the entry with task_id = to just <vid_id>)
            3 - successfully generated shortened video (requires that the entry with task_id = to just <vid_id> has status = 2)
            4 - operation failed (due to subtitles not being available)
    '''
    status = db.Column(db.Integer, nullable=False)
    '''
        times is:
            -always empty (empty string) if task_type is 0 (see below for info on task_type)
            -filled with the final json output (containing all the info the client needs to play the shortened video) if task_type is 1 
    '''
    times = db.Column(db.String, nullable=False)
    '''
        subs is:
            -filled with the subtitles of the video corresponding to <vid_id> if status >= 1 if task_type is 0 (see below for info on task_type)
                -this entry in the database is formatted in such a way that if the text of the entry was directly pasted into a text editor and
                 the file was saved as an SRT, the file would be a valid SRT
            -always empty (empty string) if task_type is 1
    '''
    subs = db.Column(db.String, nullable=False)
    '''
        punct_subs is:
            -filled with the punctuated subtitles of the video corresponding to <vid_id> if status >= 2 if task_type is 0 (see below for info on task_type)
                -this entry in the database is not formatted in the same way as subs. This entry contains all the actual caption text (no times, etc.) from
                 SRT entry in the same row strung together with the necessary punctuation inserted in. In other words, the contents of this entry are just
                 a big paragraph of text.
            -always empty (empty string) if task_type is 1
    '''
    punct_subs = db.Column(db.String, nullable=False)
    '''
        task_type can hold two values:
            0 - if task_id is of the form <vid_id>
            1 - if task_id is of the form <vid_id>@<ratio>
    '''
    task_type = db.Column(db.Integer, nullable=False)
    '''
        id to be used a primary_key. Necessary to be used for SQLAlchemy.
    '''
    id = db.Column(db.Integer, primary_key=True)
    
    def __init__(self, task_id, status, times, subs, punct_subs, task_type):
        self.task_id = task_id
        self.status = status
        self.times = times
        self.subs = subs
        self.punct_subs = punct_subs
        self.task_type = task_type
    
    def __repr__(self):
        return str(self.task_id) + "\t" + str(self.status) + "\t" + str(self.times) + "\t" + str(self.subs) + "\t" + str(self.punct_subs) + "\t" + str(self.task_type)