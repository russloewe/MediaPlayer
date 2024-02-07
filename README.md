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
