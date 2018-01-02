# vidDistill - Automated Video Summarization Using Captions
## Try it out at vid-distill.herokuapp.com!

Things you'll need to do to get this project set up locally:
1. Specify a secret key in config.py. (Make sure to add config.py to your .gitignore).
2. Install requirements from requirements.txt.
3. Install and start postgres.
4. Set up environment variables:

...a. DATABASE_URL (the URL for where your database is stored, whether that's local or )
...b. APP_SETTINGS (should be either config.DevelopmentConfig or config.ProductionConfig)

5. Download the NLTK components specified in nltk.txt