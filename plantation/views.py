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
import csv
from django.http import HttpResponse
from django.core.mail import send_mail
from .forms import VisitRequestForm
from .models import VisitRequest  
from django.conf import settings
from threading import Thread
from django.core.mail import send_mail, BadHeaderError
from django.db import DatabaseError
from django.urls import reverse
from django.http import JsonResponse
import time

def send_email_async(subject, message, recipient_list):
    """Send email in a separate thread to avoid blocking the request."""
    Thread(
        target=send_mail,
        args=(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list),
        kwargs={"fail_silently": False}
    ).start()



@login_required
def book_visit(request, plantation_id):
    """Handles visit booking form submission."""
    plantation = get_object_or_404(Plantation, id=plantation_id)
    plantation_url = request.build_absolute_uri()
    form = VisitRequestForm()

    if request.user != plantation.owner:
        messages.error(request, "❌ You are not authorized to book a visit for this plantation.")
        return render(request, 'plantation/book_visit.html', {'form': form, 'plantation': plantation, 'plantation_url': plantation_url})

    # ✅ Check if a pending visit request already exists
    if VisitRequest.objects.filter(plantation=plantation, owner=request.user, status="Pending").exists():
        messages.error(request, "🚨 You already have a pending visit request for this plantation!")
        return render(request, 'plantation/book_visit.html', {'form': form, 'plantation': plantation, 'plantation_url': plantation_url})

    if request.method == "POST":
        form = VisitRequestForm(request.POST)
        if form.is_valid():
            print("✅ Form is valid, saving data...")
            try:
                # ✅ Save visit request
                visit_request = form.save(commit=False)
                visit_request.plantation = plantation
                visit_request.owner = request.user
                visit_request.status = "Pending"
                visit_request.save()

                # ✅ Email notification to **site admin**
                admin_subject = f"🌱 New Visit Request for {plantation.name}"
                admin_message = f"""
A new visit request has been submitted.

🌱 **Plantation**: {plantation.name}
👤 **Visitor**: {request.user.username} ({request.user.email})
📞 **Phone**: {form.cleaned_data['phone_number']}
📅 **Check-in Date**: {form.cleaned_data['check_in_date']}
📆 **Check-out Date**: {form.cleaned_data['check_out_date']}
👥 **Number of Visitors**: {form.cleaned_data['visitors']}
✉️ **Message from Visitor**: {form.cleaned_data['message']}

🔗 View Plantation: {plantation_url}
                """

                try:
                    send_email_async(admin_subject, admin_message, [settings.ADMIN_EMAIL])
                except Exception as admin_email_error:
                    messages.error(request, f"⚠️ Failed to notify admin: {admin_email_error}")

                # ✅ Thank-you email to **plantation owner**
                if plantation.owner.email:
                    owner_subject = "🌱 Thank You for Your Visit Request"
                    owner_message = f"""
Dear {plantation.owner.username},

Thank you for submitting your visit request for **{plantation.name}**.  
Our team will review your request and get in touch with you shortly.

For any queries, feel free to reach out.

Best Regards,  
TreeForLife Team
                    """
                    try:
                        send_email_async(owner_subject, owner_message, [plantation.owner.email])
                    except Exception as owner_email_error:
                        messages.error(request, f"⚠️ Failed to send thank-you email: {owner_email_error}")

                messages.success(request, "✅ Your visit request has been submitted successfully!")

            except DatabaseError:
                messages.error(request, "❌ Database error: Unable to save visit request. Please try again.")
            except Exception as db_error:
                messages.error(request, f"❌ Unexpected error: {db_error}")

        else:
            messages.error(request, "⚠️ Please correct the errors in the form and try again.")

    return render(request, 'plantation/book_visit.html', {'form': form, 'plantation': plantation, 'plantation_url': plantation_url})



@login_required
def view_certificate(request, plantation_id):
    plantation = get_object_or_404(Plantation, id=plantation_id)
    
    # Access control: Only the owner may view the certificate.
    if plantation.owner != request.user:
        messages.error(request, "You are not authorized to view this certificate.")
        return redirect('plantation_details', id=plantation.id)  # or another appropriate view
    
    # Prepare the dynamic data for the certificate.
    context = {
        'owner_name': request.user.get_full_name() or request.user.username,
        'plantation_name': plantation.name,
        'plantation_date': plantation.plantation_date,
        'issuance_date': plantation.plantation_date,  # Assuming both dates are the same
        # Add any additional fields as needed.
    }
    
    return render(request, 'plantation/certificate.html', context)





@login_required
def download_import_template(request):
    # Check if the user is a corporate admin
    try:
        corporate = request.user.corporate_account
    except Corporate.DoesNotExist:
        return HttpResponseForbidden("You are not authorized to access this page.")

    # Create the CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="import_template.csv"'

    writer = csv.writer(response)
    # Write header row
    writer.writerow(['Plantation Name', 'User Email'])

    # Fetch plantations related to the corporate account
    plantations = Plantation.objects.filter(corporate=corporate).select_related('owner')

    # Write plantation data
    for plantation in plantations:
        writer.writerow([
            plantation.name,
            plantation.owner.email if plantation.owner else ''
        ])

    return response


@login_required
def export_plantations(request):
    # Check if the user is a corporate admin
    try:
        corporate = request.user.corporate_account
    except Corporate.DoesNotExist:
        return HttpResponseForbidden("You are not authorized to access this page.")

    # Create the CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="plantations.csv"'

    writer = csv.writer(response)
    # Write header row
    writer.writerow(['Plantation Name', 'Description', 'Date', 'Assigned User', 'User Email'])

    # Fetch plantations related to the corporate account
    plantations = Plantation.objects.filter(corporate=corporate).select_related('owner')

    for plantation in plantations:
        writer.writerow([
            plantation.name,
            plantation.description,
            plantation.plantation_date,
            plantation.owner.username if plantation.owner else 'Unassigned',
            plantation.owner.email if plantation.owner else 'Unassigned',
        ])

    return response

import csv
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect
from .models import Plantation, Corporate, Employee

@login_required
def import_plantations(request):
    # Check if the user is a corporate admin
    try:
        corporate = request.user.corporate_account
    except Corporate.DoesNotExist:
        return HttpResponseForbidden("You are not authorized to access this page.")

    if request.method == "POST":
        csv_file = request.FILES.get('csv_file')
        if not csv_file or not csv_file.name.endswith('.csv'):
            messages.error(request, "Invalid file format. Please upload a CSV file.")
            return redirect('manage_plantations')

        # Read CSV file
        data = csv.reader(csv_file.read().decode('utf-8').splitlines())
        next(data, None)  # Skip header row

        plantation_count = corporate.plantations.count()
        user_count = corporate.employees.count()
        new_user_count = 0
        rows_processed = 0
        errors = []

        for row in data:
            rows_processed += 1
            try:
                plantation_name, user_email = row

                # Validate plantation
                plantation = Plantation.objects.filter(name=plantation_name, corporate=corporate).first()
                if not plantation:
                    errors.append(f"Row {rows_processed}: Plantation '{plantation_name}' does not exist.")
                    continue

                # Prevent editing plantation details
                if plantation.description != plantation.description:
                    errors.append(f"Row {rows_processed}: Editing plantation details is not allowed.")
                    continue

                # Validate user
                user = User.objects.filter(email=user_email).first()
                if not user:
                    if user_count + new_user_count >= corporate.employee_credits:
                        errors.append(f"Row {rows_processed}: User limit exceeded. Cannot add new user '{user_email}'.")
                        continue
                    # Create new user
                    user = User.objects.create_user(username=user_email.split('@')[0], email=user_email)
                    Employee.objects.create(user=user, corporate=corporate)
                    new_user_count += 1

                # Assign plantation
                plantation.owner = user
                plantation.save()
            except ValueError:
                errors.append(f"Row {rows_processed}: Invalid data format.")
                continue

        # Feedback
        if errors:
            messages.error(request, f"Some rows could not be processed:\n{', '.join(errors)}")
        messages.success(request, f"{rows_processed - len(errors)} rows processed successfully.")

        return redirect('manage_plantations')

    return HttpResponseForbidden("Invalid request method.")


@login_required
def delete_employee(request, employee_id):
    try:
        corporate = request.user.corporate_account
    except Corporate.DoesNotExist:
        return HttpResponseForbidden("You are not a corporate admin.")
    
    # Fetch the employee object
    employee = get_object_or_404(Employee, id=employee_id, corporate=corporate)
    
    # Check if the employee is assigned to any plantations
    if employee.user.plantation_set.exists():
        messages.error(request, "Cannot delete employee: plantations are assigned.")
        return redirect('manage_employees')
    
    # If not assigned, delete the employee
    user = employee.user
    employee.delete()  # Remove the employee record
    user.delete()      # Remove the associated user record
    messages.success(request, "Employee deleted successfully.")
    return redirect('manage_employees')

@login_required
def export_employees(request):
    try:
        corporate = request.user.corporate_account
    except Corporate.DoesNotExist:
        return HttpResponseForbidden("You are not a corporate admin.")
    
    # Create the CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="employees.csv"'

    writer = csv.writer(response)
    writer.writerow(['Username', 'Email'])  # Headers

    # Write employee data
    for emp in corporate.employees.select_related('user'):
        writer.writerow([emp.user.username, emp.user.email])
    
    return response

@login_required
def import_employees(request):
    try:
        corporate = request.user.corporate_account
    except Corporate.DoesNotExist:
        return HttpResponseForbidden("You are not a corporate admin.")
    
    if request.method == "POST":
        csv_file = request.FILES.get('csv_file')
        if not csv_file or not csv_file.name.endswith('.csv'):
            messages.error(request, "Invalid file format. Please upload a CSV file.")
            return redirect('manage_employees')
        
        # Read CSV file
        data = csv.reader(csv_file.read().decode('utf-8').splitlines())
        next(data, None)  # Skip header row

        added_count = 0
        for row in data:
            if corporate.employees.count() >= corporate.employee_credits:
                messages.warning(request, "Employee limit reached. Some rows were skipped.")
                break
            
            try:
                username, email = row
                if not User.objects.filter(email=email).exists():
                    user = User.objects.create_user(username=username, email=email)
                    Employee.objects.create(user=user, corporate=corporate)
                    added_count += 1
            except ValueError:
                messages.error(request, "Invalid data format in file.")
                continue
        
        messages.success(request, f"{added_count} employees added successfully.")
        return redirect('manage_employees')

    return HttpResponseForbidden("Invalid request method.")

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

    # ✅ Get visit requests related to the owner
    visit_requests = VisitRequest.objects.filter(owner=owner).order_by('-created_at')

    # Hide email if the current user is not the owner
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
        'visit_requests': visit_requests,  # ✅ Pass visit requests to the template,
    })



def plantation_details(request, id):
    plantation = get_object_or_404(Plantation, id=id)
    timelines = plantation.timelines.order_by('-activity_date')
    breadcrumbs = [
        {'name': 'Home', 'url': reverse('homepage')},
        {'name': f"Plantation: {plantation.name}", 'url': None},
    ]

    # ✅ Ensure pending_request is always a boolean
    pending_request = False  # Default: No pending request

    if request.user.is_authenticated and request.user == plantation.owner:
        pending_request = VisitRequest.objects.filter(
            plantation=plantation,
            owner=request.user,
            status="Pending"
        ).exists()  # ✅ Always return True or False

    return render(request, "plantation/plantation_details.html", {
        'plantation': plantation,
        'timelines': timelines,
        'breadcrumbs': breadcrumbs,
        'pending_request': pending_request,  # ✅ Pass boolean
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



