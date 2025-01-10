from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def dashboard(request):
    template_name = "dashboard/dashboard.html"
    return render(request, template_name)