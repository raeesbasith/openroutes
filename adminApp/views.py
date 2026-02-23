from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.cache import cache_control
import csv
import json
from datetime import datetime
from django.utils import timezone
from .models import *
from django.db.models import Count, Sum
from operatorApp.models import Operator
from guestApp.models import login, TravellerProfile
from userApp.models import Booking

# Create your views here.
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def adminHome(request):
    if 'login_id' not in request.session:
        return redirect('/login/')
    
    # Dashboard Statistics
    travellers_count = TravellerProfile.objects.count()
    operators_count = Operator.objects.count()
    bookings_count = Booking.objects.count()
    verified_operators_count = Operator.objects.filter(status='approved').count()
    pending_operators_count = Operator.objects.filter(status='pending').count()
    
    # Calculate percentage of verified operators
    verified_percentage = 0
    if operators_count > 0:
        verified_percentage = int((verified_operators_count / operators_count) * 100)

    # Recent Data
    recent_bookings = Booking.objects.select_related('traveller', 'tour').order_by('-booking_date')[:5]
    recent_travellers = TravellerProfile.objects.order_by('-reg_date')[:5]

    # Analytics 1: Booking Status Distribution
    status_counts = Booking.objects.values('booking_status').annotate(count=Count('booking_id'))
    status_labels = [item['booking_status'].title().replace('_', ' ') for item in status_counts]
    status_data = [item['count'] for item in status_counts]

    # Analytics 2: Monthly Revenue (Current Year)
    today = timezone.now()
    current_year = today.year
    months_labels = []
    revenue_data_points = []
    
    # Initialize all months
    import calendar
    for i in range(1, 13):
        months_labels.append(calendar.month_abbr[i])
        revenue_data_points.append(0)

    start_of_year = datetime(current_year, 1, 1)
    revenue_bookings = Booking.objects.filter(
        booking_date__gte=start_of_year, 
        booking_status__in=['confirmed', 'completed', 'paid']
    )
    
    for booking in revenue_bookings:
        month_idx = booking.booking_date.month - 1
        revenue_data_points[month_idx] += booking.effective_total_amount # Using property from previous context

    # Additional Analytics: Operator Status Distribution
    op_status_counts = Operator.objects.values('status').annotate(count=Count('operator_id'))
    op_status_labels = [item['status'].title() for item in op_status_counts]
    op_status_data = [item['count'] for item in op_status_counts]

    context = {
        'travellers_count': travellers_count,
        'operators_count': operators_count,
        'bookings_count': bookings_count,
        'verified_percentage': verified_percentage,
        'pending_operators_count': pending_operators_count,
        'recent_bookings': recent_bookings,
        'recent_travellers': recent_travellers,
        'today': datetime.now().date(),
        'status_labels_json': json.dumps(status_labels),
        'status_data_json': json.dumps(status_data),
        'months_labels_json': json.dumps(months_labels),
        'revenue_data_json': json.dumps(revenue_data_points),
        'op_status_labels_json': json.dumps(op_status_labels),
        'op_status_data_json': json.dumps(op_status_data),
    }
    
    return render(request, 'adminT/index.html', context)
def distRegn(request):
    return render(request, 'adminT/districtRegn.html')

def distRegnInsert(request):
    if request.method == 'POST':
        district = request.POST.get('district')
        # check against the model field name (it's `name`, not `district`)
        if District.objects.filter(name=district).exists():
            return HttpResponse("<script>alert('Already exists!!!');window.location.href ='/distRegn/';</script>")
        dob = District()
        dob.name = district
        dob.save()
        return HttpResponse("<script>alert('District added successfully!!!');window.location.href ='/distRegn/';</script>")
    return HttpResponse("Invalid request")

def distView(request):
    districts = District.objects.all().order_by('name')
    return render(request, 'adminT/districtView.html', {'districts':districts})

def distDelete(request, id):
    district = District.objects.get(district_id=id)
    district.delete()
    return HttpResponse("<script>alert('District deleted successfully!!!');window.location.href ='/distView/';</script>")

def distEdit(request,id):
    if request.method=='POST':
        districtname=request.POST.get("districtname")
        dis = District.objects.get(district_id=id)
        dis.name = districtname
        dis.save()
        return HttpResponse("<script>alert('District updated successfully!!!');window.location.href ='/distView/';</script>")
    district = District.objects.get(district_id=id)
    return render(request,"adminT/districtEdit.html",{'district':district})

def locationRegn(request):
    districts = District.objects.all()
    return render(request, 'adminT/locationRegn.html', {'districts': districts})

def locationInsert(request):
    if request.method == "POST":
        district_id = request.POST.get("did")
        lname = request.POST.get("lname")
        lob = Location()
        lob.name = lname
        lob.district = District.objects.get(district_id=district_id)
        if Location.objects.filter(name=lname, district_id=district_id).exists():
            return HttpResponse("<script>alert('Already Exists..');window.location='locationRegn/';</script>")
        else:
            lob.save() 
            return HttpResponse("<script>alert('Location inserted successfully');window.location='/locationView/';</script>")
        
def locationView(request):
    districts = District.objects.all().order_by('name')
    locations = Location.objects.all().order_by('name')
    return render(request, 'adminT/locationView.html', {'districts': districts, 'locationdata': locations})

def locationDelete(request, id):
    location = Location.objects.get(location_id=id)
    location.delete()
    return HttpResponse("<script>alert('Location deleted successfully!!!');window.location.href ='/locationView/';</script>")

def locationEdit(request,id):
    if request.method == 'POST':
        locationname = request.POST.get("locationname")
        loc = Location.objects.get(location_id=id)
        loc.name = locationname
        loc.save()
        return HttpResponse("<script>alert('Location updated successfully!!!');window.location.href ='/locationView/';</script>")
    location = Location.objects.get(location_id=id)
    return render(request,"adminT/locationEdit.html",{'location':location})

def filllocation(request):
    try:
        did = int(request.POST.get("did"))
        location = Location.objects.filter(district_id=did).values('location_id', 'name')
        return JsonResponse(list(location), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def disabilityRegn(request):
    return render(request, 'adminT/disabilityRegn.html')
def disabilityInsert(request):
    if request.method == 'POST':
        disability = request.POST.get('disability')
        if Disability.objects.filter(disability_type=disability).exists():
            return HttpResponse("<script>alert('Already exists!!!');window.location.href ='/disabilityRegn/';</script>")
        dob = Disability()
        dob.disability_type = disability
        dob.save()
        return HttpResponse("<script>alert('Disability added successfully!!!');window.location.href ='/disabilityView/';</script>")
    return HttpResponse("Invalid request")

def disabilityView(request):
    disabilities = Disability.objects.all().order_by('disability_type')
    return render(request, 'adminT/disabilityView.html', {'disabilities':disabilities})

def disabilityDelete(request, id):
    disability = Disability.objects.get(disability_id=id)
    disability.delete()
    return HttpResponse("<script>alert('Disability deleted successfully!!!');window.location.href ='/disabilityView/';</script>")

def disabilityEdit(request,id):
    if request.method=='POST':
        disabilitytype=request.POST.get("disabilitytype")
        dis = Disability.objects.get(disability_id=id)
        dis.disability_type = disabilitytype
        dis.save()
        return HttpResponse("<script>alert('Disability updated successfully!!!');window.location.href ='/disabilityView/';</script>")
    disability = Disability.objects.get(disability_id=id)
    return render(request,"adminT/disabilityEdit.html",{'disability':disability})

def accessibilityRegn(request):
    return render(request, 'adminT/accessibilityRegn.html')

def accessibilityInsert(request):
    if request.method == 'POST':
        accessibility = request.POST.get('accessibility')
        if Accessibility.objects.filter(accessibility_feature=accessibility).exists():
            return HttpResponse("<script>alert('Already exists!!!');window.location.href ='/accessibilityRegn/';</script>")
        aob = Accessibility()
        aob.accessibility_feature = accessibility
        aob.save()
        return HttpResponse("<script>alert('Accessibility feature added successfully!!!');window.location.href ='/accessibilityView/';</script>")
    return HttpResponse("Invalid request")

def accessibilityView(request):
    accessibilities = Accessibility.objects.all().order_by('accessibility_feature')
    return render(request, 'adminT/accessibilityView.html', {'accessibilities':accessibilities})

def accessibilityDelete(request, id):
    accessibility = Accessibility.objects.get(accessibility_id=id)
    accessibility.delete()
    return HttpResponse("<script>alert('Accessibility feature deleted successfully!!!');window.location.href ='/accessibilityView/';</script>")

def accessibilityEdit(request,id):
    if request.method=='POST':
        accessibilityfeature=request.POST.get("accessibilityfeature")
        acc = Accessibility.objects.get(accessibility_id=id)
        acc.accessibility_feature = accessibilityfeature
        acc.save()
        return HttpResponse("<script>alert('Accessibility feature updated successfully!!!');window.location.href ='/accessibilityView/';</script>")
    accessibility = Accessibility.objects.get(accessibility_id=id)
    return render(request,"adminT/accessibilityEdit.html",{'accessibility':accessibility})

def operatorVerification(request):
    operators = Operator.objects.filter(status='requested').order_by('operator_id')
    return render(request, 'adminT/operatorVerification.html', {'operators': operators})

def licenseView(request, id):
    operator = Operator.objects.get(operator_id=id)
    return render(request, 'adminT/licenseView.html', {'operator': operator})

def operatorApprove(request, id):
    operator = Operator.objects.get(operator_id=id)
    lob = login.objects.get(login_id=operator.login_id)
    lob.status = 'active'
    operator.status = 'approved'
    operator.save() 
    lob.save()
    return HttpResponse("<script>alert('Operator approved!!!'); window.location.href = '/operator-verification/';</script>")

def operatorReject(request, id):
    operator = Operator.objects.get(operator_id=id)
    operator.status = 'rejected'
    operator.save()
    return HttpResponse("<script>alert('Operator rejected!!!'); window.location.href = '/operator-verification/';</script>")

def operatorsView(request):
    operators = Operator.objects.filter(status='approved').order_by('operator_id')
    return render(request, 'adminT/operators_view.html', {'operators': operators})

def operatorBlock(request, id):
    lob = login.objects.get(login_id=id)
    lob.status = 'blocked'
    lob.save()
    return HttpResponse("<script>alert('Operator blocked!!!'); window.location.href = '/operators-view/';</script>")

def operatorUnblock(request, id):
    lob = login.objects.get(login_id=id)
    lob.status = 'active'
    lob.save()
    return HttpResponse("<script>alert('Operator unblocked!!!'); window.location.href = '/operators-view/';</script>")

def operatorProfile(request, id):
    operator = Operator.objects.get(operator_id=id)
    return render(request, 'adminT/operator_profile.html', {'operator': operator})

def travellersView(request):
    travellers = TravellerProfile.objects.all().order_by('-reg_date')
    return render(request, 'adminT/traveller_view.html', {'travellers': travellers})

def travellerProfile(request, id):
    traveller = TravellerProfile.objects.get(traveller_id=id)
    return render(request, 'adminT/traveller_singleview.html', {'traveller': traveller})

def travellerBlock(request, id):
    lob = login.objects.get(login_id=id)
    lob.status = 'blocked'
    lob.save()
    return HttpResponse("<script>alert('Traveller blocked!!!'); window.location.href = '/travellers-view/';</script>")

def travellerUnblock(request, id):
    lob = login.objects.get(login_id=id)
    lob.status = 'active'
    lob.save()
    return HttpResponse("<script>alert('Traveller unblocked!!!'); window.location.href = '/travellers-view/';</script>")

def bookingsView(request):
    bookings = Booking.objects.all().order_by('-booking_date')
    return render(request, 'adminT/bookings_view.html', {'bookings': bookings})

def admin_datewise_report(request):
    bookings = None
    total_booking_amount = 0
    total_commission = 0
    payable_to_operators = 0
    
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date and end_date:
        bookings = Booking.objects.filter(
            booking_date__date__range=[start_date, end_date]
        ).order_by('-booking_date')
        
        # Calculate totals
        if bookings:
            financial_bookings = bookings.exclude(booking_status='cancelled')
            total_booking_amount = 0
            total_commission = 0
            payable_to_operators = 0
            for booking in financial_bookings:
                total_booking_amount += booking.effective_total_amount
                total_commission += booking.effective_commission_amount
                payable_to_operators += booking.net_amount
            
    return render(request, 'adminT/datewise_report.html', {
        'bookings': bookings,
        'total_booking_amount': total_booking_amount,
        'total_commission': total_commission,
        'payable_to_operators': payable_to_operators,
        'start_date': start_date,
        'end_date': end_date
    })

def admin_bookings_export(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    bookings = Booking.objects.all().order_by('-booking_date')
    
    if start_date and end_date:
        bookings = bookings.filter(booking_date__date__range=[start_date, end_date])
        
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="admin_bookings_report_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Booking ID', 'Operator', 'Customer', 'Tour', 'Date', 'Total Amount', 'Commission (10%)', 'Payable to Operator', 'Status'])
    
    for booking in bookings:
        realized_total = booking.effective_total_amount
        commission = booking.effective_commission_amount
        payable = booking.net_amount
        writer.writerow([
            booking.booking_id,
            booking.tour.operator.operator_name,
            booking.traveller.traveller_name,
            booking.tour.tour_name,
            booking.booking_date.strftime('%Y-%m-%d'),
            realized_total,
            commission,
            payable,
            booking.booking_status
        ])
        
    return response



