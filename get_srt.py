# Functionality to download subtitles.

import subprocess
import sys
import os
import downloaded_subtitles
from task_manager import *

# Returns false if SRT already exists or there are no subtitles to be found. 
def get_srt(youtube_link, proportion):
    """
        Downloads subtitles if necessary. Returns True if subtitles are already downloaded or subtitles are successfully downloaded
        and stored. Returns False if no automatic or manual captions are available for the supplied youtube_link.
    """
    if downloaded_subtitles.subs_already_downloaded(youtube_link):
        return True

    vid_id = get_video_id_from_url(youtube_link)
    
    # how to get manual subs, autosubs, or nothing in one command: https://github.com/rg3/youtube-dl/issues/1412
    # decode text https://stackoverflow.com/questions/21486703/how-to-get-the-output-of-subprocess-check-output-python-module
    subs = str(subprocess.check_output("youtube-dl " + youtube_link + " --skip-download --write-sub --write-auto-sub --sub-lang \"en\" -o 'tmp/%(id)s.vtt'", shell=True, stderr=subprocess.STDOUT).decode(sys.stdout.encoding))
    print(subs)
    if "\n[info]" not in subs:
        print("Neither automated subtitles nor captions available.")
        return False
    
    print("Obtained subtitles.")
    looking_for = "[info] Writing video subtitles to: "
    vtt_filename = subs[subs.find(looking_for) + len(looking_for) : -1]
    srt_filename = vtt_filename[:-3] + "srt"
    subprocess.check_output("ffmpeg -n -i " + vtt_filename + " " + srt_filename, shell=True).decode(sys.stdout.encoding)
    
    # read in the srt file and put that in the database
    with open(srt_filename) as the_srt_file:
        set_task_without_ratio(vid_id, proportion, 1, subs=the_srt_file.read())
    
    return True