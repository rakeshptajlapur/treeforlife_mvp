
# Plantation Management System

## Project Overview

The Plantation Management System is a web application designed to help plantation owners manage their plantations, activities, and timelines. The system allows plantation owners to view and manage their plantations, track activities, and interact with timelines through comments. Admins can manage users, plantations, and timelines from the backend.

## Key Features

### Admin Management:
- Admins can manage users (plantation owners), plantations, and timelines through the Django admin panel.
- Admins can assign plantation owners to plantations.

### Plantation Owners:
- Plantation owners can view their plantations in a list.
- Owners can view details of their own plantations and timelines.
- Owners can view comments on timelines and add new comments to them.
- Only plantation owners or admins can add comments on timelines.
- Plantation owners must log in to the system to manage their plantations and timelines.

### Visitors:
- Visitors can view plantation details and owner details (with sensitive details hidden).
- Visitors can view comments on timelines but cannot add comments.

### Timeline Management:
- Plantation owners can view the timeline of their plantations.
- Admins can manage timelines via the backend.

### Search Filter:
- Users can search for plantations by name.

### Backend Admin Features:
- Admins can add, update, and delete plantations, timelines, and comments from the Django admin interface.
- Admins can manage plantation ownership assignments.

## Features Breakdown

- **Plantation Overview**: Plantation owners can view a list of plantations assigned to them, and visitors can search plantations by name.
- **Timeline Details**: Owners can see their plantation's timeline and interact with the comments section. Visitors can only see the comments but cannot add them.
- **Admin Control**: Admins have full control over the system, including managing plantation owners, plantations, timelines, and comments.
- **Search and Filter**: The system provides a search filter for users to find plantations by name easily.
- **Login for Plantation Owners**: Plantation owners are required to log in before accessing their plantation details and managing timelines and comments.


## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/rakeshptajlapur/plantation-management.git
   ```

2. Navigate to the project directory:
   ```bash
   cd plantation-management
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python manage.py runserver
   ```

5. Open the application in your browser at `http://127.0.0.1:8000/`.

## Contact

For support, inquiries, or collaboration, feel free to reach out to me at:

- **Email**: rakesh@codesiddhi.com
- **GitHub**: [rakeshptajlapur](https://github.com/rakeshptajlapur)
- **LinkedIn**: [rakeshptajlapur](https://linkedin.com/in/rakeshptajlapur)
- **Website**: [codesiddhi.agency](https://codesiddhi.agency)
