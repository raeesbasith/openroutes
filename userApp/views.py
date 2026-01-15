from django.shortcuts import render

# Create your views here.
def traveller_home(request):
    return render(request, 'traveller/traveller_home.html')