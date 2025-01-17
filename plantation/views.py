from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Plantation  # Ensure this import is added
from django.http import JsonResponse
from django.urls import reverse


def homepage(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        search_query = request.GET.get('search', '').strip()  # Get and sanitize input
        
        # Filter plantations by name
        plantations = Plantation.objects.filter(
            name__icontains=search_query
        ).select_related('owner')  # Use select_related for efficiency

        # Format the response data
        results = [
            {
                'id': plantation.id,
                'name': plantation.name,
                'owner_name': plantation.owner.username,
            }
            for plantation in plantations
        ]

        return JsonResponse({'results': results})
    
    # Default: Show all plantations
    plantations = Plantation.objects.all().select_related('owner')
    return render(request, "plantation/homepage.html", {'plantations': plantations})


    # Show all plantations by default
    plantations = Plantation.objects.all().select_related('owner')
    return render(request, "plantation/homepage.html", {'plantations': plantations})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Redirect dynamically to owner details
            return redirect('owner_details', username=user.username)
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('homepage')


#@login_required
#def owner_details(request, username):
 #   owner = get_object_or_404(User, username=username)
  #  plantations = Plantation.objects.filter(owner=owner)

    # If the user is authenticated and it's their own page, show the email
   # email = owner.email if request.user.is_authenticated and request.user == owner else "Hidden"

    #return render(request, "plantation/owner_details.html", {
     #   'owner': owner,
      #  'plantations': plantations,
       # 'email': email,
    #})

def owner_details(request, username):
    owner = get_object_or_404(User, username=username)
    plantations = Plantation.objects.filter(owner=owner)

    # Display email conditionally based on the user
    if request.user.is_authenticated and request.user == owner:
        email = owner.email  # Show email to the owner
    else:
        email = "Hidden"  # Hide email for visitors

    return render(request, "plantation/owner_details.html", {
        'owner': owner,
        'plantations': plantations,
        'email': email,
    })


def plantation_details(request, id):
    plantation = get_object_or_404(Plantation, id=id)
    return render(request, "plantation/plantation_details.html", {'plantation': plantation})
