# Flask application code (defining routes, getting access to the database, etc.)

from flask import Flask
from flask import request
import os
from flask.ext.sqlalchemy import SQLAlchemy
import threading

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
print(os.environ['APP_SETTINGS'])

db = SQLAlchemy(app)

from models import *
from task_manager import *
from get_para import get_times
from downloaded_subtitles import get_video_id_from_url

# Just testing if the server is up!
@app.route("/")
def hello():
    return "Hello World!"

# Need to supply a link and a rate in the raw body of the request
@app.route("/times")
def times():
    link = request.args.get('link') # get the youtube URL from the raw body
    rate = round(float(request.args.get('rate')), 1) # get the ratio from the raw body
    video_id = get_video_id_from_url(link)
    print(link, rate, video_id)
    create_task(video_id, 0) # create entry in database (if necessary) with id <vid_id>
    create_task(video_id + '@' + str(rate), 0) # create entry in database (if necessary) with id <vid_id>@<ratio>
    total_identifier = video_id + '@' + str(rate)
    print("successfully added?", db.session.query(db.session.query(TaskEntry).filter_by(task_id=total_identifier).exists()).scalar())
    t = threading.Thread(target = get_times, args=(link, rate)) # start a background thread to process this task
    t.daemon = True
    t.start()
    return "ok"

# Get the status of the task with the task_id supplied
@app.route("/waiting/<taskid>")
def get_task_progess(taskid):
    return str(get_task_status(taskid)) # Return the status in the database corresponding to the video and ratio the user wants

# Get the finished JSON for the shortened video.
@app.route("/finished/<taskid>")
def finished(taskid):
    return str(get_entire_row(taskid)[2]) # Return the final JSON

@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response
 
if __name__ == "__main__":
    app.run(threaded=True, host=os.getenv('IP', '0.0.0.0'),port=int(os.getenv('PORT', 8080)))