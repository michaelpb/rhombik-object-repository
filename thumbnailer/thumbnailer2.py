
#TRISTAN, this will not work. It's only for reference. Be afraid.
#class renderstl(basefile, size):
#  from selenium import webdriver
#  from django.conf import settings

#  driver = webdriver.PhantomJS()
#  driver.set_window_size(size) # not optional
#  driver.get(settings.URL+"/thumbs/stl/"+basefile.url)
#  imagedata = driver.get_screenshot_as_base64() # save a screenshot as base64 string, the only format phantom supports that isn't disk.

#  import base64
#  from io import BytesIO
#  #converts the base64 encoded image data into a python file object
#  imagedata = Image.open(BytesIO(base64.b64decode(imagedata)))
#  return(jsc3d, imagedata)


from io import StringIO, BytesIO

def thumbnailify(filebit, sizebit):
  from PIL import Image
  from os.path import splitext
  from django.http import HttpResponseRedirect, HttpResponse
  from io import BytesIO
  from django.core.files.uploadedfile import UploadedFile
  import sys
  from django.core.files.base import ContentFile 

  browser_kind = [  ".png",".jpg",".gif" ]
  jsc3d_kind = [  ".stl",".obj" ]
  text_kind = [".md",".txt"]
# text_kind = [ ".txt" ]
  ##ext os the file extension, forced into lowercase becouse people are insane.
  ext = str(splitext(str(filebit.filename))[1].lower())
  response = HttpResponse(mimetype="image/png")

  if ext in browser_kind:
    import StringIO
    stream = StringIO.StringIO(filebit.filename.read())
    print(str(stream.len)+" stream length")
    img = Image.open(stream)
    img.convert('RGB')
    img.thumbnail(sizebit, Image.ANTIALIAS)
    backround = Image.new('RGBA', sizebit, (255, 255, 255, 0))  #with alpha
    backround.paste(img,((sizebit[0] - img.size[0]) / 2, (sizebit[1] - img.size[1]) / 2))
    # Create a file-like object to write thumb data (thumb data previously created
    # using PIL, and stored in variable 'img')
    # using PIL, and stored in variable 'thumb')
#    thumb_io = BytesIO()
    thumb_io = BytesIO()
#    print(str(thumb_io)+" thumb_io !")
    backround.save( thumb_io, format='png')
#    print(str(thumb_io.read())+" filled thumb_io !")

    thumb_file = ContentFile(thumb_io.getvalue())
    thumb_file.name = str(sizebit)+"-"+str(filebit.filename)+".png"
#    print(thumb_file.read(3))
# Once you have a Django file-like object, you may assign it to your ImageField
    # and save.
    return(thumb_file, "browser")

  if ext in jsc3d_kind:
    from selenium import webdriver
    from django.conf import settings
    #How much to antialias by.
    rendermul = 2
    driver = webdriver.PhantomJS()
    driver.set_window_size(sizebit[0]*rendermul,sizebit[1]*rendermul) # not optional
    driver.get(settings.URL+"/thumbs/jsc3d/"+str(filebit.pk))
    imagedata = driver.get_screenshot_as_base64() # save a screenshot as base64 string, the only format phantom supports that isn't disk.

    import base64
    from io import BytesIO
    #converts the base64 encoded image data into a python file object
    img = Image.open(BytesIO(base64.b64decode(imagedata)))
    img = img.convert('RGB')
    img.thumbnail(sizebit, Image.ANTIALIAS)
    thumb_io = BytesIO()
    img.save(thumb_io, format='png')

    thumb_file = ContentFile(thumb_io.getvalue())
    thumb_file.name = str(sizebit)+"-"+str(filebit.filename)+".png"

    return(thumb_file, "jsc3d")

  if ext in text_kind:
    return(None, "text")

  return(None, "norender") 
