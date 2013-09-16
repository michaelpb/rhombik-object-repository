from django.shortcuts import get_object_or_404, render_to_response
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest

##from multiuploader.models import MultiuploaderImage
from django.core.files.uploadedfile import UploadedFile

#importing json parser to generate jQuery plugin friendly json response
from django.utils import simplejson

#for generating thumbnails
#sorl-thumbnails must be installed and properly configured
#from sorl.thumbnail import get_thumbnail

from django.views.decorators.csrf import csrf_exempt

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

import thumbnailer.thumbnailer as thumbnailer

import logging
log = logging

import os.path
from multiuploader.forms import MultiuploaderImage
from post.models import *
from filemanager.models import fileobject, thumbobject


@csrf_exempt
def multiuploader_delete(request, pk):
    """
    View for deleting photos with multiuploader AJAX plugin.
    made from api on:
    https://github.com/blueimp/jQuery-File-Upload
    """
    image = get_object_or_404(fileobject, pk=pk)
    post=Post.objects.filter(fileobject__pk=image.pk)[0]
    if request.method == 'POST' and str(post.author) == str(request.user):
        log.info('Called delete image. image id='+str(pk))
        image.delete()
        log.info('DONE. Deleted photo id='+str(pk))
        return HttpResponse(str(pk))
    elif request.method == 'POST' and str(post.author) != str(request.user):
        log.info("user "+str(request.user)+" tried to delete object "+str(pk)+" which doesn't belong to them")
        return HttpResponse(status=403)
    else:
        log.info('Received not POST request to delete image view')
        return HttpResponseBadRequest('Only POST accepted')

@csrf_exempt
def multiuploader(request,pk):

    post=Post.objects.filter(pk=pk)[0]
    """
    Main Multiuploader module.
    Parses data from jQuery plugin and makes database changes.
    """
    if request.method == 'POST' and str(post.author) == str(request.user):
        log.info('received POST to main multiuploader view')
        if request.FILES == None:
            return HttpResponseBadRequest('Must have files attached!')

        #getting file data for farther manipulations
        postfiles = fileobject()
        postfiles.post = post
        postfiles.filename = request.FILES[u'files[]']
        postfiles.save()
        print (postfiles)
        log.info ('Got file: "%s"' % str(postfiles.filename.name))


        #settings imports
        try:
            file_delete_url = settings.MULTI_FILE_DELETE_URL+'/'
        except AttributeError:
            file_delete_url = 'multi_delete/'
        print("postfiles is "+str(postfiles.filename.url))
       #from thumbnailer import thumbnailer2
       #try:
        thumburl = thumbobject.objects.get_or_create( fileobject = postfiles, filex=64, filey=64 )[0]
       #except:
       #    thumburl = thumbnailer2.thumbnailify(postfiles, [64,64])[0]
        print("thumburl is "+str(thumburl)) 
        #generating json response array
        result = []
        result.append({"name":postfiles.subfolder+os.path.split(str(postfiles.filename.name))[1], 
                       "size":postfiles.filename.size, 
                       "url":str(postfiles.filename.url),
                       "thumbnail_url":"/media/"+str(thumburl.filename),
                       "delete_url":"/multi_delete/"+str(postfiles.pk)+"/", 
                       "delete_type":"POST",})
        response_data = simplejson.dumps(result)
        
        #checking for json data type
        #big thanks to Guy Shapiro
        if "application/json" in request.META['HTTP_ACCEPT_ENCODING']:
            mimetype = 'application/json'
        else:
            mimetype = 'text/plain'
        return HttpResponse(response_data, mimetype=mimetype)
    else: #GET
        print("multiuploader getting images!")
        postfiles = fileobject.objects.filter(post=post)
  
        file_delete_url = settings.MULTI_FILE_DELETE_URL+'/'
        result = []
        for image in postfiles:
           #try:
            print(image.filename.url)
            thumburl =  thumbobject.objects.get_or_create( fileobject = image, filex=64, filey=64 )[0].filename.url
            print(thumburl) 
           #except:
           #    thumburl = ""
            ##json stuff
            result.append({"name":image.subfolder+os.path.split(image.filename.name)[1],
                       "size":image.filename.size,
                       "url":"/preview/"+str(image.filetype)+str(image.filename.url),
                       "thumbnail_url":thumburl,
                       "delete_url":"/multi_delete/"+str(image.pk)+"/",
                       "delete_type":"POST",})
        response_data = simplejson.dumps(result)

        if "application/json" in request.META['HTTP_ACCEPT_ENCODING']:
            mimetype = 'application/json'
        else:
            mimetype = 'text/plain'
        return HttpResponse(response_data, mimetype=mimetype)


