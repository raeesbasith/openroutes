from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from adminApp.models import District, Location, Accessibility
from operatorApp.models import Tour, TourAccessibility
from userApp.models import *
from guestApp.models import *
# Create your views here.
def traveller_home(request):
    return render(request, 'traveller/traveller_home.html')

def tour_packages_view(request):
    Districts = District.objects.all()
    accessibilities = Accessibility.objects.all()
    # Base queryset
    Tour_list = Tour.objects.all().order_by('price')

    # Apply filters from GET params
    district = request.GET.get('district')
    location = request.GET.get('location')
    access_list = request.GET.getlist('accessibility')

    if district:
        Tour_list = Tour_list.filter(location__district__district_id=district)

    if location:
        Tour_list = Tour_list.filter(location__location_id=location)

    # If accessibilities selected, require tours that have ALL selected features
    # (chaining filters reduces to intersection)
    for acc in access_list:
        if acc:
            Tour_list = Tour_list.filter(touraccessibility__accessibility__accessibility_id=acc)

    paginator = Paginator(Tour_list.distinct(), 10)  # 10 tours per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'traveller/tour_packages.html', {
        'Districts': Districts,
        'accessibilities': accessibilities,
        'Tour': page_obj
    })

# Removed duplicate view `tour_details` to avoid confusion; use `tour_detail` below.

def filllocation(request):
    did = request.POST.get('did')
    locations = Location.objects.filter(district_id=did).values('location_id', 'name')
    return JsonResponse(list(locations), safe=False)

def tour_detail(request, tour_id):
    tour = get_object_or_404(Tour, tour_id=tour_id)
    return render(request, 'traveller/tour_detail.html', {'tour': tour})

def booking(request, tour_id):
    tour = Tour.objects.get(tour_id=tour_id)
    accessibilities = TourAccessibility.objects.filter(tour=tour_id)
    return render(request, 'traveller/booking.html', {'tour': tour, 'accessibilities': accessibilities})

def calculate_booking_amount(tour, total_people, accessibility_selections_per_person):
    base_amount = tour.price * total_people
    acc_cost = 0

    # accessibility_selections_per_person is a list of lists of accessibility IDs
    for person_selections in accessibility_selections_per_person:
        for acc in person_selections:
            try:
                ta = TourAccessibility.objects.get(tour=tour, accessibility_id=acc)
                acc_cost += ta.extra_cost_per_acc
            except TourAccessibility.DoesNotExist:
                continue

    total_amount = base_amount + acc_cost
    return base_amount, acc_cost, total_amount

def booking_confirm(request, tour_id):
    if request.method == 'POST':
        login_id = request.session.get('login_id')
        if not login_id:
            return HttpResponse("<script>alert('Error: User session expired. Please log in again.');window.location.href='/login/';</script>")
        
        try:
            traveller = TravellerProfile.objects.get(login=login_id)
        except TravellerProfile.DoesNotExist:
            return HttpResponse("<script>alert('Error: Traveller profile not found. Please ensure you are logged in as a traveller.');window.location.href='/login/';</script>")
        
        tour = Tour.objects.get(tour_id=tour_id)
        total_persons = int(request.POST.get('total_persons'))
        persons_needing_accessibility = int(request.POST.get('persons_needing_accessibility', 0))
        caregiver_gender = request.POST.get('caregiver_gender_preference', None)
        tour_date = request.POST.get('tour_date')

        # Collect accessibility selections per person based on the count provided
        accessibility_selections_per_person = []
        if persons_needing_accessibility > 0:
            for i in range(1, persons_needing_accessibility + 1):
                selections = request.POST.getlist(f'accessibilities_person_{i}')
                if selections:
                    accessibility_selections_per_person.append(selections)

        base_amount, acc_amount, total_amount = calculate_booking_amount(
            tour,
            total_persons,
            accessibility_selections_per_person
        )
        booking = Booking()
        booking.traveller = traveller
        booking.tour = tour
        booking.tour_date = tour_date
        booking.total_persons = total_persons
        booking.persons_needing_accessibility = persons_needing_accessibility
        booking.caregiver_gender_preference = caregiver_gender
        booking.base_amount = base_amount
        booking.accessibility_amount = acc_amount
        booking.total_amount = total_amount
        booking.save()

        # Save selected accessibilities per person (one record per person-accessibility pair)
        for person_selections in accessibility_selections_per_person:
            for acc in person_selections:
                booking_acc = BookingAccessibility()
                booking_acc.booking = booking
                booking_acc.accessibility = Accessibility.objects.get(accessibility_id=acc)
                booking_acc.save()
        return HttpResponse("<script>alert('Booking confirmed successfully!');window.location.href='/tour-packages/';</script>")    