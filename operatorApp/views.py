from django.shortcuts import render

# Create your views here.
def operator_home(request):
    return render(request, 'operator/operator_home.html')