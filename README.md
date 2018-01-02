# vidDistill - Automated Video Summarization Using Captions
## Try it out at [vid-distill.herokuapp.com](https://vid-distill.herokuapp.com)!

Have you ever felt that a video on YouTube was too long and just wanted to watch the important parts? That's what vidDistill is for! The goal is to build a web service where people can enter a YouTube URL, choose what percent of the original video length you want, and wait for a shortened video.

Things you'll need to do to get this project set up locally:
1. Specify a secret key in config.py. (Make sure to add config.py to your .gitignore).
2. Install requirements from requirements.txt.
3. Install and start postgres.
4. Set up environment variables:
	
    a. DATABASE_URL (the URL for where your database is stored, whether that's local or with Heroku)
    
    b. APP_SETTINGS (should be either config.DevelopmentConfig or config.ProductionConfig)

5. Download the NLTK components specified in nltk.txt