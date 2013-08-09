from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User, Group
from datetime import datetime
import thumbnailer.shadowbox
import thumbnailer.thumbnailer
import os
from django.conf import settings

class Post(models.Model):
    try:
        self.time
    except NameError:
        time = datetime.now()

    title = models.CharField(max_length=60,unique=True)
    thumbnail = models.CharField(max_length=60, blank=True, null=True)
    thumbnailpath = models.CharField(max_length=256, blank=True, null=True)
    body = models.TextField()
    created = models.DateTimeField(default=time)
    author = models.ForeignKey(User, related_name='author',default=User) 
    allow_html = models.BooleanField(default=False)
    ##only used internally, don't set
    body_rendered = models.TextField('Entry body as HTML', blank=True, null=True)


    def __unicode__(self):
        return self.title
    def save(self):
        #created the folder for that post if it doesn't exist
        directory = settings.MEDIA_ROOT+"uploads/" + self.title
        if not os.path.exists(directory):
            os.makedirs(directory)
        #Generates the thumbnail
        try:        
                #I hate names.
            self.thumbnailpath = thumbnailer.thumbnailer.thumbnail(settings.MEDIA_ROOT+"uploads/" + self.title + self.thumbnail,(200,200))[0]
        except:
            print("thumbnail failed")        

        import markdown
        #Markdownifies the post body, striping out any raw html
        if self.allow_html == False:
            renderedtext = markdown.markdown(self.body, safe_mode=True)
            self.body_rendered = thumbnailer.shadowbox.run(renderedtext, self.title)
            super(Post, self).save() # Call the "real" save() method.
        #mardownifies the body of the post, leaving any raw HTML intact.
        else:
            self.body_rendered = markdown.markdown(self.body)
            self.body_rendered = thumbnailer.shadowbox.run(renderedtext, self.title)
            super(Post, self).save() # Call the "real" save() method.
