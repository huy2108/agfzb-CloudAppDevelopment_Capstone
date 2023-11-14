from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
# from .restapis import related methods
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
from .restapis import get_dealers_from_cf, get_request, get_dealer_reviews_from_cf,post_request
from .models import CarModel, CarMake, CarDealer, DealerReview
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

def static_template(request):
    # context = {}
    return render(request,'djangoapp/static_template.html')


# Create an `about` view to render a static about page
def about(request):
    return render(request,'djangoapp/about.html')

# Create a `contact` view to return a static contact page
def contact(request):
    return render(request,'djangoapp/contact_us.html')

# Create a `login_request` view to handle sign in request
def login_request(request):
    if (request.method == "POST"):
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request,user)
            return redirect('djangoapp:index')
        else:
            logger.debug('This username is not existed')
            return render(request,'djangoapp/index.html')
    else:
        return render(request,'djangoapp/index.html')


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    
    logout(request)
    return redirect('djangoapp:index')


def signup(request):
    return render(request,'djangoapp/registration.html')


# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == "POST":
        username=request.POST['username']
        password=request.POST['password']
        firstname=request.POST['firstname']
        lastname=request.POST['lastname']
        exist = False
        try:
            user= User.objects.get(username=username)
            exist = True
        except:
            logger.debug("{} not exist".format(username))

        if not exist:
            user= User.objects.create_user(username=username,password=password,first_name=firstname,last_name=lastname)
            return redirect('djangoapp:index')
    return 0

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://lequanghuy21-3000.theiadocker-2-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        context['dealership_list'] = dealerships
        # Return a list of dealer short name
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    context = {}
    url = "https://lequanghuy21-5000.theiadocker-2-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/get_reviews"
    dealer_reviews = get_dealer_reviews_from_cf(url,id = dealer_id)
    context["dealer_reviews"] = dealer_reviews
    return render(request,'djangoapp:dealer_details', context)


# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    if request.method == "GET":
        context = {}
        car = CarDealer.objects.all()
        context["dealer_id"] = dealer_id
        context["cars"] = car
        return render(request,'djangoapp:add_review',context)

    if request.method == "POST":
        if request.user.is_authenticated:
            username = request.user.username
            url = "https://lequanghuy21-5000.theiadocker-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/post_review"
            payload = dict()
            review = dict()
            review["time"] = datetime.utcnow().isoformat()
            review["name"] = username
            review["dealership"] = dealer_id
            review["review"] = request.POST["review"]
            review["purchase"] = False

            payload["review"] = review

            respone = post_request(url, payload, dealerId=dealer_id)



