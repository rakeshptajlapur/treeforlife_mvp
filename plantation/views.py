from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.contrib import messages
from .models import Corporate, Employee, Plantation, Timeline, Comment

def homepage(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        search_query = request.GET.get('search', '').strip()
        plantations = Plantation.objects.filter(name__icontains=search_query).select_related('owner')
        results = [
            {
                'id': plantation.id,
                'name': plantation.name,
                'owner_name': plantation.owner.username,
            }
            for plantation in plantations
        ]
        return JsonResponse({'results': results})
    
    plantations = Plantation.objects.all().select_related('owner')
    breadcrumbs = [{'name': 'Home', 'url': reverse('homepage')}]
    return render(request, "plantation/homepage.html", {
        'plantations': plantations,
        'breadcrumbs': breadcrumbs,
    })

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Check if this user is a corporate admin
            try:
                # If this succeeds, the user has a corporate_account
                user.corporate_account
                # Redirect to corporate dashboard
                return redirect('corporate_dashboard')
            except Corporate.DoesNotExist:
                # If we land here, user is not a corporate admin
                return redirect('owner_details', username=user.username)
    else:
        form = AuthenticationForm()

    # For breadcrumbs or extra context:
    breadcrumbs = [
        {'name': 'Home', 'url': reverse('homepage')},
        {'name': 'Login', 'url': None}
    ]
    return render(request, 'registration/login.html', {'form': form, 'breadcrumbs': breadcrumbs})

def logout_view(request):
    logout(request)
    return redirect('homepage')

def owner_details(request, username):
    owner = get_object_or_404(User, username=username)
    plantations = Plantation.objects.filter(owner=owner)
    email = owner.email if request.user.is_authenticated and request.user == owner else "Hidden"
    breadcrumbs = [
        {'name': 'Home', 'url': reverse('homepage')},
        {'name': f"Owner: {owner.username}", 'url': None}
    ]
    return render(request, "plantation/owner_details.html", {
        'owner': owner,
        'plantations': plantations,
        'email': email,
        'breadcrumbs': breadcrumbs,
    })

def plantation_details(request, id):
    plantation = get_object_or_404(Plantation, id=id)
    timelines = plantation.timelines.order_by('-activity_date')
    breadcrumbs = [
        {'name': 'Home', 'url': reverse('homepage')},
        {'name': f"Plantation: {plantation.name}", 'url': None},
    ]
    return render(request, "plantation/plantation_details.html", {
        'plantation': plantation,
        'timelines': timelines,
        'breadcrumbs': breadcrumbs,
    })

@login_required
def add_comment(request, plantation_id, timeline_id):
    timeline = get_object_or_404(Timeline, id=timeline_id)
    plantation = timeline.plantation

    if not (request.user == plantation.owner or request.user.is_staff):
        raise Http404("You are not authorized to comment on this timeline.")

    if request.method == "POST":
        text = request.POST.get("text")
        if text:
            new_comment = Comment.objects.create(timeline=timeline, user=request.user, text=text)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    "status": "success",
                    "comment": {
                        "user": request.user.username,
                        "text": new_comment.text,
                        "created_at": new_comment.created_at.strftime('%Y-%m-%d %H:%M'),
                    }
                })
            messages.success(request, "Your comment has been added successfully!")
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"status": "error", "message": "Comment cannot be empty!"}, status=400)
            messages.error(request, "Comment cannot be empty!")

    return redirect("timeline_details", plantation_id=plantation.id, timeline_id=timeline.id)

#@login_required
def timeline_details(request, plantation_id, timeline_id):
    plantation = get_object_or_404(Plantation, id=plantation_id)
    timeline = get_object_or_404(Timeline, id=timeline_id, plantation=plantation)
    comments = timeline.comments.all()
    can_add_comment = plantation.owner == request.user or request.user.is_staff

    # Use an alternative field or fallback for the timeline breadcrumb
    timeline_name = getattr(timeline, 'name', 'Timeline Details')

    breadcrumbs = [
        {'name': 'Home', 'url': reverse('homepage')},
        {'name': f"Plantation: {plantation.name}", 'url': reverse('plantation_details', args=[plantation.id])},
        {'name': timeline_name, 'url': None},
    ]

    return render(request, 'plantation/timeline_details.html', {
        'plantation': plantation,
        'timeline': timeline,
        'comments': comments,
        'can_add_comment': can_add_comment,
        'breadcrumbs': breadcrumbs,
    })

def timeline_details_ajax(request, plantation_id, timeline_id):
    plantation = get_object_or_404(Plantation, id=plantation_id)
    timeline = get_object_or_404(Timeline, id=timeline_id)
    comments = timeline.comments.all()
    is_owner = plantation.owner == request.user

    return render(
        request,
        'plantation/timeline_detail_content.html',
        {
            'timeline': timeline,
            'comments': comments,
            'is_owner': is_owner,
        }
    )


@login_required
def corporate_dashboard(request):
    # Check if the current user is actually a corporate admin
    try:
        corporate = request.user.corporate_account
    except Corporate.DoesNotExist:
        return HttpResponseForbidden("You are not a corporate admin.")

    # Collect data to display
    total_employees = corporate.employees.count()
    total_plantations = corporate.plantations.count()

    context = {
        'corporate': corporate,
        'total_employees': total_employees,
        'total_plantations': total_plantations,
    }
    return render(request, 'corporate/dashboard.html', context)


@login_required
def manage_employees(request):
    try:
        corporate = request.user.corporate_account
    except Corporate.DoesNotExist:
        return HttpResponseForbidden("You are not a corporate admin.")

    # Fetch employees
    employees = corporate.employees.select_related('user')

    context = {
        'corporate': corporate,
        'employees': employees,
    }
    return render(request, 'corporate/manage_employees.html', context)


@login_required
def add_employee(request):
    try:
        corporate = request.user.corporate_account
    except Corporate.DoesNotExist:
        return HttpResponseForbidden("You are not a corporate admin.")

    # Check credits
    if corporate.employees.count() >= corporate.employee_credits:
        messages.error(request, "You have reached your employee limit.")
        return redirect('manage_employees')

    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')

        # Basic checks
        if not username or not email:
            messages.error(request, "Please fill in all fields.")
            return redirect('add_employee')

        # Create the user (no password set yet, or set a default)
        user = User.objects.create_user(username=username, email=email)
        # Optionally set a default password or send an invite email
        # user.set_password("some-default-password")
        # user.save()

        # Link user to Employee model
        Employee.objects.create(user=user, corporate=corporate)
        messages.success(request, "Employee added successfully!")
        return redirect('manage_employees')

    return render(request, 'corporate/add_employee.html')


#for corporate admins to manage plantations list
@login_required
def manage_plantations(request):
    try:
        corporate = request.user.corporate_account
    except Corporate.DoesNotExist:
        return HttpResponseForbidden("You are not a corporate admin.")

    # List ONLY the plantations that belong to this corporate
    plantations = Plantation.objects.filter(corporate=corporate).select_related('owner')

    context = {
        'corporate': corporate,
        'plantations': plantations
    }
    return render(request, 'corporate/manage_plantations.html', context)

@login_required
def assign_plantation(request, plantation_id):
    try:
        corporate = request.user.corporate_account
    except Corporate.DoesNotExist:
        return HttpResponseForbidden("You are not a corporate admin.")

    plantation = get_object_or_404(Plantation, id=plantation_id, corporate=corporate)
    # Make sure this plantation actually belongs to the corporate admin

    if request.method == "POST":
        employee_id = request.POST.get('employee_id')
        if employee_id:
            employee = get_object_or_404(Employee, id=employee_id, corporate=corporate)
            # Update the plantation owner
            plantation.owner = employee.user
            plantation.save()
        return redirect('manage_plantations')

    # GET request: show a form with a dropdown of employees
    employees = corporate.employees.select_related('user')
    context = {
        'plantation': plantation,
        'employees': employees
    }
    return render(request, 'corporate/assign_plantation.html', context)
