# MediaPlayer
 password protected online media player for audio books

# Installation

This works best with already running Django web server being serverd via Apache2

## settings.py

Add this to INSTALLED_APPS in  <appname>/settings.py:

    INSTALLED_APPS = [
    ...
    'media.apps.MediaConfig',
    ...
    
]

Add this to <appname>/urls.py

    urlpatterns = [
        ...
        path('media/', include('media.urls')),
        ...
]

## database

run

        ./manage.py makemigrations media
        ./manage.py migrate

# Running

## sychronize static files

The media files are served with Apache2 static hosting. The database objects need to match the files which the Apache server is hosting. To automatically scan the current files via ssh then update the database run the script

        ./db_commands.py

You can open the file and change the function call in main from load_books(dryrun=False) to 

       load_books(dryrun=True)

 to run the script without modifying the database. 
