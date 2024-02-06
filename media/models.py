from django.db import models
from django.contrib.auth.models import User
import urllib.parse
from django.utils.text import slugify

MEDIATYPE_CHOICES = (
    ('audio', 'Audio'),
    ('video', 'Video'),
)

class Series(models.Model):
    title =  models.CharField(max_length=250)
    slug = models.SlugField(max_length=255, unique=True, default='')

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return(f'{self.id} {self.title}')    

class MediaItem(models.Model):
    title =  models.CharField(max_length=250)
    local_path = models.CharField(max_length=250) # on disk path relative to /var/www/media
    mediatype = models.CharField(max_length=20, choices=MEDIATYPE_CHOICES)
    series = models.ForeignKey(Series, on_delete=models.CASCADE, null=True, blank=True)
    episode = models.IntegerField(default=0)
    slug = models.SlugField(max_length=255, unique=True, default='')

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return(f'{self.title} {self.local_path}')    

        
class PlayerTime(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    mediaitem = models.ForeignKey(MediaItem, on_delete=models.PROTECT, null=True, blank=True)
    local_path = models.CharField(max_length=250, null=True, blank=True) # this is used to fix playertimes after media items are reloaded in db
    position = models.CharField(max_length=250)
   
    def __str__(self):
        return(f'{self.id} {self.local_path} {self.mediaitem}')    
