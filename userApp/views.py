from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from adminApp.models import District, Location, Accessibility
from operatorApp.models import Tour
# Create your views here.
def traveller_home(request):
    return render(request, 'traveller/traveller_home.html')

def tour_packages_view(request):
    Districts = District.objects.all()
    accessibilities = Accessibility.objects.all()
    # Base queryset
    Tour_list = Tour.objects.all().order_by('-tour_id')

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


def filllocation(request):
    did = request.POST.get('did')
    locations = Location.objects.filter(district_id=did).values('location_id', 'name')
    return JsonResponse(list(locations), safe=False)

def tour_detail(request, tid):
    tour = get_object_or_404(Tour, tour_id=tid)
    return render(request, 'traveller/tour_detail.html', {'tour': tour})
