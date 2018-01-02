# Functionality to download subs, punctuate them, summarize them, and produce the JSON (plus some helper functions)

import subprocess
import sys
import os
import downloaded_subtitles
import get_srt
from nltk.tokenize import word_tokenize
from nltk import pos_tag
import requests
import string
import shlex
from task_manager import get_task_status
from task_manager import get_entire_row
from task_manager import set_task_without_ratio
from task_manager import set_task_with_ratio
from downloaded_subtitles import punctuated_text_already_downloaded
import json

def getTimeRange(time_sections):
    '''
    Takes a list/tuple of time ranges (a time range is formatted like so time1 --> time2) and returns a single all-encompassing time range
    :param time_sections: a list/tuple of time ranges (a time range is formatted like so time1 --> time2)
    :return: the first time of the first time section + " --> " + the last time of the last time section
    '''
    first = time_sections[0].split(" --> ")[0]
    last = time_sections[-1].split(" --> ")[1]
    return first + " --> " + last

def isIndexGreaterThanOrEqualTo(ind1, ind2):
    '''
    Helper function that returns True if a tuple (a, b) is >= a tuple (c, d).
    For example:
        isIndexGreaterThanOrEqualTo((4, 2), (4, 2)) returns True
        isIndexGreaterThanOrEqualTo((4, 3), (4, 2)) returns True
        isIndexGreaterThanOrEqualTo((4, 0), (4, 3)) returns False
        isIndexGreaterThanOrEqualTo((3, 7), (4, 3)) returns False
    :param ind1: the first tuple/list
    :param ind2: the second tuple/list
    :return: True if ind1 >= ind2, False otherwise
    '''
    if ind1[0] > ind2[0]:
        return True
    elif ind1[0] == ind2[0] and ind1[1] >= ind2[1]:
        return True
    else:
        return False

def get_times(youtube_link, proportion):
    '''
    Downloads subtitles, punctuates them, summarizes them, and generates final JSON for shortened video, all while updating database status and other values.
    :param youtube_link: URL to YouTube video with v URL param.
    :param proportion: Ratio of the original video's transcript length desired.
    '''
    video_id = downloaded_subtitles.get_video_id_from_url(youtube_link)
    
    if get_task_status(video_id) < 1:
        if not get_srt.get_srt(youtube_link, proportion):
            print("Can't produce para.")
            set_task_with_ratio(video_id + '@' + str(proportion), 4)
            return
        else:
            set_task_without_ratio(video_id, proportion, 1)
    
    s = []
    for line in get_entire_row(video_id)[3].split("\n"):
        s.append(line.strip())
    
    cnt = 0
    i = 1
    para = [] # contains the indices of the lines we will want to append
    items = [] # can pass this to
    while i < len(s):
        time_stamp = s[i]
        i += 1
        item = []
        while s[i] != "":
            for j in word_tokenize(s[i]):
                if j not in string.punctuation:
                    item.append(j)
            para.append(i)
            i += 1
        time_and_tokens = (time_stamp, item)
        items.append(time_and_tokens)
        i += 2

    # Gets a list of time sections from items data structure given starting index and how many indices to go forward
    def get_time_sections(items, ind, streak):
        curr = [i for i in ind]
        li = [items[curr[0]][0], ]
        for i in range(streak):
            if li[-1] != items[curr[0]][0]:
                li.append(items[curr[0]][0])
            curr[1] += 1
            if curr[1] == len(items[curr[0]][1]):
                curr[0] += 1
                curr[1] = 0
        return li
    
    complete_text = ''.join([s[i] + " " for i in para])
    
    def send_curl_req(message):
        data = [('text', message),]
        response = requests.post('http://bark.phon.ioc.ee/punctuator', data=data)
        return response.text
    
    punctuated_text = None
    
    if punctuated_text_already_downloaded(video_id):
        punctuated_text = get_entire_row(video_id)[4]
    else:
        punctuated_text = send_curl_req(complete_text)
        set_task_without_ratio(video_id, proportion, 2, punct_subs=punctuated_text)

    arr1 = [(i, False) for i in word_tokenize(complete_text) if i not in string.punctuation]
    arr2 = [(i, False) for i in word_tokenize(punctuated_text) if i not in string.punctuation]
    
    # transfer over the punctuated content into items
    item_ind_1 = 0
    item_ind_2 = 0
    
    for i in range(len(arr2)):
        items[item_ind_1][1][item_ind_2] = arr2[i][0]
        item_ind_2 += 1
        if item_ind_2 == len(items[item_ind_1][1]):
            item_ind_2 = 0
            item_ind_1 += 1


    # summarize by making call to summarization service

    d = dict()
    d["text"] = punctuated_text
    d["ratio"] = proportion
    
    def send_req_to_summarizer(data):
        response = requests.post('https://summa-summarize.herokuapp.com', data=data)
        return response.text
        
    summary = send_req_to_summarizer(json.dumps(d))

    
    tokenized_summary = [i for i in word_tokenize(summary) if i not in string.punctuation]
    
    # Need to go from tokenized summary with punctuation back to selection from original subtitles. General strategy:
    # find the longest possible match, consume, repeat.

    tok_ind = 0
    item_ind_1 = 0
    item_ind_2 = 0
    
    output = [video_id, ]
    
    latest_ind = [0, 0]
    while tok_ind < len(tokenized_summary):
        best_ind = [-1, -1]
        best_streak = 0
        for item_ind_1 in range(len(items)):
            for item_ind_2 in range(len(items[item_ind_1][1])):
                if tok_ind < len(tokenized_summary) and tokenized_summary[tok_ind] == items[item_ind_1][1][item_ind_2]:
                    # start looping to see how long it matches for
                    new_tok_ind = tok_ind
                    streak_len = 0
                    a = item_ind_1
                    b = item_ind_2
                    while a < len(items) and new_tok_ind < len(tokenized_summary):
                        if tokenized_summary[new_tok_ind] == items[a][1][b]:
                            streak_len += 1
                            new_tok_ind += 1
                            b += 1
                            if b == len(items[a][1]):
                                a += 1
                                b = 0
                        else:
                            break
                    if streak_len > best_streak and isIndexGreaterThanOrEqualTo([item_ind_1, item_ind_2], latest_ind):
                        best_streak = streak_len
                        best_ind = [item_ind_1, item_ind_2]
        if best_streak == 0:
            break
        tok_ind += best_streak
        latest_ind = best_ind
        time_sections = get_time_sections(items, best_ind, best_streak)
        output.append(getTimeRange(time_sections))
    
    caps = []
    selected_time_stamp_set = set(output[1:])
    for i in range(len(items)):
        section = []
        if items[i][0] in selected_time_stamp_set:
            section.append(items[i][0])
        else:
            section.append(items[i][0])
        section.append(' '.join(items[i][1]))
        caps.append(section)

    # build JSON
    result = dict()
    result["status"] = 3
    result["video_id"] = video_id
    result["selected_times"] = output[1:]
    result["full_captions"] = caps
    json_dump = json.dumps(result)
    print(json_dump)
    set_task_with_ratio(video_id + '@' + str(proportion), 3, message=json_dump) # update database to indicate task is successful
    return json_dump