from django.core.paginator import Paginator, InvalidPage, EmptyPage

from django.shortcuts import render_to_response, render, redirect
from django.contrib.auth.models import User
from django.template import RequestContext, loader

from project.models import Project
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect, csrf_exempt

from userProfile.models import userProfile
from userProfile.forms import *
from django.contrib.auth.forms import PasswordChangeForm

from filemanager.models import fileobject

from project.views import project_list_get



### This Is the view for the user edit page.
#it obviously ~~doesn't~~ Works... ~~But it's a good base to work from.~~
@csrf_exempt
def edit(request):
    
    # data is the users userdata.
    data = request.user

    ## redirect to login if not logged in.
    try:
        profile = userProfile.objects.filter(user=data)[0]
    except:
        return redirect("/register/")


    ##  User submitting profile data.
    if request.method == 'POST':

        #get data from the forms
        profileform = UserProfileForm(request.POST)
        pictureform = UserPictureForm(request.POST, request.FILES)

        ## puts the users stuff in the database if it is valid.
        if profileform.is_valid() and pictureform.is_valid():

            ###Create user's profile
            profile.bio = profileform.cleaned_data["bio"]

            #Create users picture.
            if pictureform.cleaned_data["filename"]:
                
                  ## if they don't have a userpic yet we can't delete it.
                try:
                    profile.userpic.delete()
		except:
                    pass

                thumbiwumbi = fileobject(parent=profile)
                thumbiwumbi.filename = request.FILES["filename"]
                thumbiwumbi.save()
                profile.userpic = thumbiwumbi

            profile.save()
            return redirect("/userProfile/"+str(data.pk))

        #returns form with error messages.
        else:
            return render_to_response('editProfile.html', dict( user=request.user, form2=profileform, form3=pictureform))


    ## Initializes the page with the forms.
    else:
        #form = PasswordChangeForm(data)
        profileform = UserProfileForm({'bio':profile.bio})
        pictureform = UserPictureForm()#{"filename":profile.})
        return render_to_response('editProfile.html', dict( user=request.user, form2=profileform, form3=pictureform))





def index(request, pk):
    
    """bleh blebh bhel bleh, IM GOING INSANE.... I mean; user profile display stuff."""
    #I hate this vampire head ~alex
    """THE VAMPIRE HEAD FIXES ALL OF YOUR BROKEN CODE!!!, that is to say, as long as you never look at this code, it could be anything. We guarantee that whatever you imaging is better written then what actually is written."""

    # userdata is the user data who's page we are viewing.
    userdata=User.objects.filter(pk = pk).get()

    profile = userProfile.objects.filter(user=userdata)[0]

    projects=Project.objects.filter(author=userdata).order_by("-created") #'''~this needs to get the users projects.... not just you know, all the projects.... and now it does!''' YAY!  And now it gets no projects? wtf.. ok, so it is getting the list.. it is just not getting displayed...

    #  paginator is neat!
    # It takes the list of projects and breaks them up into different pages.
    # Kinda obvious huh?
    paginator = Paginator(projects, 3*3)

    try: page = int(request.GET.get("page", '1'))
    except ValueError: page = 1

    try:
        projects = paginator.page(page)
    except (InvalidPage, EmptyPage):
        projects = paginator.page(paginator.num_pages)

    listdata = project_list_get(projects)

    try:
        thumbpic = [profile.userpic.get_thumb(512,512)]
    except:
        thumbpic = False

    c = RequestContext(request, dict(thumbpic=thumbpic, user=request.user, owner=userdata, listdata = listdata))
    return render(request, "userProfile/index.html", c)





### simple logout view, redirects users to the login page.
def logout_user(request):
    logout(request)
    return redirect("/register")





### This Is the view for the registration page.
@csrf_exempt
def register(request):
    
    from django.contrib.auth.forms import UserCreationForm

    ## This if loop is true when user clicks the register button.
    if request.method == 'POST':

        #get data from the forms
        form = UserCreationForm(request.POST)
        email = UserEmail(request.POST)

        ###Create the user if the for is valid
        if form.is_valid() and email.is_valid():

            data = User();
            data.username = form.cleaned_data["username"]

            if email.cleaned_data["email"]:
                data.email = email.cleaned_data["email"]

           #data.password = form.cleaned_data["password"]###this is NOT how you set a password! Passwords are hashed.
            data.set_password(form.cleaned_data["password1"])# Yes. Good.
            data.save()

            ###Create user's profile
            profile = userProfile()
            profile.user = data
            profile.save()


            user = authenticate(username=form.cleaned_data["username"], password=form.cleaned_data["password1"])
            login(request, user)
            return redirect("/editProfile/")

        #returns register form with error messages.
        else:
            return render_to_response('register.html', dict( user=request.user, form=form, email=email))
    
    ## redirect to legister.
    else:
        return redirect("/legister/")




### Login page.
@csrf_exempt
def login_user(request):

    state = "Please log in below..."##hmm... you can never see this message.
    username = password = ''

    if request.POST:

        # get data from form
        usernamedata = request.POST.get('username')
        passworddata = request.POST.get('password')

	# authenticate that user!
        user = authenticate(username=usernamedata, password=passworddata)
        if user is not None:
            if user.is_active:
                login(request, user)
                state = "You're success'd the log in!"# this message is also never seen...:(
                ### right now logging in redirects you to home.
                ### it would be nice to have it redirect to where a user was going.
                ### like to the create page.
                ### for example.
                return redirect("/")

            ## Right now accounts are active by default. So it is unlikely a user will ever encounter this.
            else:
                state = "Your account is not active, please contact the site admin. Also... I have no idea how that could have happened... so ... Good Job!"
                return render_to_response('auth.html', {'state':state, 'username': usernamedata})

        # if some data doesn't check out, let the user know they failed.
        else:
            state = "Your username and/or password were incorrect."
            return render_to_response('auth.html', {'state':state, 'username': usernamedata})

    # redirect to legister
    else:
        return redirect("/legister/")




### Register/login page.
@csrf_exempt ## <-- because alex is a terrible person
def legister(request):

    from django.contrib.auth.forms import UserCreationForm
    form = UserCreationForm()
    email = UserEmail()
    return render_to_response('legister.html', dict( user=request.user, form=form, email=email))



