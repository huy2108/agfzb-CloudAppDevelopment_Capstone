from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
# from .restapis import related methods
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
from .restapis import get_dealers_from_cf, get_request, get_dealer_reviews_from_cf,post_request,get_dealer_by_id_from_cf
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
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successfully!")
            return redirect('djangoapp:index')
        else:
            messages.warning(request, "Invalid username or password.")
            return redirect("djangoapp:index")



# Create a `logout_request` view to handle sign out request
def logout_request(request):
    
    logout(request)
    return redirect('djangoapp:index')


# def signup(request):
#     return render(request,'djangoapp/registration.html')


# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            pass
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            user.is_superuser = True
            user.is_staff=True
            user.save()  
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return redirect("djangoapp:registration")

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://lequanghuy21-3000.theiadocker-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        context['dealership_list'] = dealerships
        # Return a list of dealer short name
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, id):
    if request.method == "GET":
        context = {}
        dealer_url = "https://lequanghuy21-3000.theiadocker-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
        dealer = get_dealer_by_id_from_cf(dealer_url, id=id)
        context["dealer"] = dealer

        review_url = "https://lequanghuy21-5000.theiadocker-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/get_reviews"
        reviews = get_dealer_reviews_from_cf(review_url, id=id)
        print(reviews)
        context["reviews"] = reviews
        
        return render(request, 'djangoapp/dealer_details.html', context)


# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    
    if request.method == "GET":
        context = {}
        car = CarModel.objects.all()
        context["dealer_id"] = dealer_id
        context["cars"] = car
        return render(request,'djangoapp:add_review',context)

    if request.method == "POST":
        if request.user.is_authenticated:
            username = request.user.username
            url = "https://lequanghuy21-5000.theiadocker-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/post_review"
            payload = dict()
            review = dict()
            car = request.POST["car"]
            review["time"] = datetime.utcnow().isoformat()
            review["name"] = username
            review["dealership"] = dealer_id
            review["review"] = request.POST["content"]
            review["purchase"] = False
            if "purchasecheck" in request.POST:
                if request.POST["purchasecheck"] == 'on':
                    payload["purchase"] = True
            review["purchase_date"] = car.year.strftime("%Y")
            review["car_make"] = car.make.name
            review["car_model"] = car.name

            payload["review"] = review

            respone = post_request(url, payload, dealerId=dealer_id)

            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)



