Plant Booking Django Application – Overview and Key Points


1. Project Overview
This Django application is a Plantation Management System designed to serve two types of users:

Corporate Users (Corporate Admins):

Corporate admins manage a corporate account, which includes multiple employees and plantations.
They have dedicated dashboards and tools to handle bulk operations (such as CSV import/export) and enforce credit limits (both for plantations and employees).
Individual Plantation Owners:

These users are not associated with a corporate account.
They can manage their own plantations, view plantation details, and access public plantation information from the homepage.
Their functionality is streamlined compared to corporate admins.

2. Directory Structure
Below is a sample directory structure for the project:
plant_booking/         # Project root
├── db.sqlite3
├── manage.py
├── media/
│   ├── admin-interface/
│   │   ├── favicon/
│   │   └── logo/
│   └── plantation_images/
├── plant_booking/       # Main project folder
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── plantation/        # Main app
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── context_processors.py
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   ├── ... (other migration files)
│   ├── models.py
│   ├── resources.py
│   ├── templatetags/
│   │   ├── __init__.py
│   │   └── form_extras.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── static/
│   ├── css/
│   │   ├── styles.css
│   │   └── images/
│   │       ├── favicon.ico
│   │       └── treeforlifelogo.png
└── README.md


3. Key Models and Their Relationships
Corporate
Fields:
admin_user (OneToOne with User)
name
plantation_credits
employee_credits
Purpose: Represents a corporate account with assigned credits and a designated admin user.
Employee
Fields:
user (OneToOne with User)
corporate (ForeignKey to Corporate)
Purpose: Links a User to a Corporate account.
Plantation
Fields:
name, plantation_date, image, description, created_at, updated_at
owner (ForeignKey to User)
corporate (ForeignKey to Corporate, optional)
Purpose: Stores details about plantations.
Validation:
Uses the clean() method (and overridden save()) to enforce that the number of plantations for a corporate account does not exceed its plantation_credits. This is also enforced in the Django Admin via a custom form.
Timeline & Comment
Timeline:
Tracks activities related to a plantation.
Comment:
Allows users to comment on timeline activities.


4. Core Features & Functionality
Corporate Dashboard
For Corporate Admins:
Displays a welcome message, company name, and key statistics (employee credits, plantation credits).
Provides quick actions (e.g., manage employees, manage plantations, export reports).
Manage Employees
UI:
Lists employees (username, email) with extra columns:
Plantation Status: Indicates if an employee is assigned to any plantations (clickable link for details).
Action: A delete icon that's active only if the employee is unassigned.
Import/Export:
Export: Downloads a CSV file of current employees.
Import: Accepts a CSV file (with Username and Email columns) to add new employees, respecting the employee credit limit.
Manage Plantations
UI:
Displays plantations with details (name, owner, and an assign/reassign button).
Import/Export:
Export: Downloads a CSV file with plantation details, including the assigned user’s information.
Import: Accepts a CSV file with two columns:
Plantation Name: Must match an existing plantation for the corporate account.
User Email: Used to assign/reassign the plantation.
Download Import Template: A link allows downloading a prepopulated CSV template that includes current plantation names and user emails, which can then be edited before re-uploading.
Validation:
Ensures that plantation details (other than the user assignment) cannot be modified via the import.
Enforces plantation and employee credit limits during import.
Individual Plantation Owners
For Non-Corporate Users:
Users who are not part of a corporate account can manage their own plantations.
They can view public plantation details on the homepage and manage their assigned plantations via their profile.


5. Django Admin Customizations
Custom User Admin
Extended the default UserAdmin using ImportExportMixin to allow bulk operations and display key user details (username, email, etc.).
Custom Plantation Admin
Uses a custom admin form (PlantationAdminForm) that overrides clean() to enforce plantation credit limits.
Prevents adding a new plantation via the admin if it would exceed the corporate account’s plantation_credits.


6. Additional Technical Details
Templates:

The base template is located at plantation/templates/plantation/base.html and provides a common layout for all pages.
Corporate-specific templates (dashboard, manage employees, manage plantations) are located under plantation/templates/corporate/.
Registration templates (e.g., login) are under plantation/templates/registration/.
Static Files:

CSS and images are stored under static/css/ and static/css/images/.
Third-Party Apps:

import_export is used for CSV import/export operations.
admin_interface and colorfield improve the admin UI.
Settings:

The project uses SQLite as the database.
Custom context processors are used to tailor the UI (e.g., displaying corporate dashboard links for corporate admins).
