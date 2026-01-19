from django.shortcuts import redirect, render
from django.core.exceptions import ValidationError

# Create your views here.
def operator_home(request):
    return render(request, 'operator/operator_home.html')

def validate_pdf(file):
    if not file.name.endswith('.pdf'):
        raise ValidationError("Only PDF files are allowed.")
    
def tour_regn_view(request):
    return render(request, 'operator/tour_regn.html')