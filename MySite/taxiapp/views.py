from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render, redirect

from django.shortcuts import render
from taxiapp.forms import TaxiForm, OrderForm

from .models import City, User, Driver, Taxi


def home(request):
    cities = City.objects.all()
    return render(request, 'taxiapp/home.html', {'cities': cities})


def select_city(request):
    if request.method == 'POST':
        city_id = request.POST.get('city')
        city = City.objects.get(id=city_id)
        user_type = request.POST.get('user_type')
        user_name = request.POST.get('user_name')

        user = User.objects.create(name=user_name, city=city, user_type=user_type)
        if user.user_type == User.DRIVER:
            drive = Driver.objects.create(user=user, balance=0, driver_status=Driver.FREE)
            return render(request, 'taxiapp/driver.html', {'driver': drive})
        else:
            return render(request, 'taxiapp/passenger.html', {'user': user})

    cities = City.objects.all()
    return render(request, 'taxiapp/select_city.html', {'cities': cities})


def select_taxi(request):
    if request.method == 'POST':
        driver_id = request.POST.get('driver')
        try:
            driver_ = Driver.objects.get(id=driver_id)
            taxi = Taxi.objects.create(driver=driver_)
            driver_.driver_status = Driver.BUSY
            driver_.save()
            return render(request, 'taxiapp/booking_success.html', {'taxi': taxi})
        except ObjectDoesNotExist:
            return HttpResponse('Водитель не найден')

    drivers = Driver.objects.filter(driver_status=Driver.FREE)
    return render(request, 'taxiapp/select_taxi.html', {'drivers': drivers})


def driver(request):
    drivers = Driver.objects.all()
    return render(request, 'taxiapp/driver.html', {'drivers': drivers})


def passenger(request):
    return render(request, 'taxiapp/passenger.html')


def booking_success(request):
    return render(request, 'taxiapp/booking_success.html')


# c другого чата
@login_required
def choose_taxi(request):
    if request.user.is_driver:
        return redirect('driver_dashboard')
    if request.method == 'POST':
        form = TaxiForm(request.POST)
        if form.is_valid():
            taxi_id = form.cleaned_data['id']
            taxi = Taxi.objects.get(id=taxi_id)
            taxi.is_available = False
            taxi.save()
            return redirect('order', taxi_id=taxi_id)
    else:
        form = TaxiForm(queryset=Taxi.objects.filter(is_available=True))
    return render(request, 'choose_taxi.html', {'form': form})


@login_required
def order(request, taxi_id):
    if request.user.is_driver:
        return redirect('driver_dashboard')
    taxi = Taxi.objects.get(id=taxi_id)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            pickup_location = form.cleaned_data['pickup_location']
            dropoff_location = form.cleaned_data['dropoff_location']
            taxi_id = form.cleaned_data['taxi']
            taxi = Taxi.objects.get(id=taxi_id)
            # send notification to driver
            return redirect('order_confirmation')
    else:
        form = OrderForm()
    return render(request, 'order.html', {'form': form, 'taxi': taxi})


@login_required
def order_confirmation(request):
    if request.user.is_driver:
        return redirect('driver_dashboard')
    return render(request, 'order_confirmation.html')