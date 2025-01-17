
# Tree for Life MVP

Tree for Life is a Django-based application designed to help plantation owners manage their plantations and provide visitors with an interactive way to explore them.

---

## Features

### For Visitors:
- **Browse Plantations**: View a list of plantations and their details.
- **Owner Information**: Visitors can view plantation owners' names, but sensitive details like emails are hidden.

### For Plantation Owners:
- **Authentication**: Owners can log in to view their profile and plantation details.
- **Personalized Dashboard**: Owners can see all plantations they own.
- **Email Visibility**: Owners can view their own email address, which remains hidden from visitors.

### For Admins:
- **User Management**: Add, edit, and delete users directly from the admin panel.
- **Plantation Management**: Manage plantations and their assigned owners through the admin interface.
- **Content Control**: Control over displayed data to ensure privacy and consistency.

---

## Installation Guide

### Prerequisites
- Python (>= 3.8)
- Git

### Steps to Set Up the Project
1. **Clone the Repository**  
   Clone the repository to your local machine:
   ```bash
   git clone https://github.com/rakeshptajlapur/treeforlife_mvp.git
   cd treeforlife_mvp
   ```

2. **Set Up a Virtual Environment**  
   Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**  
   Install the required dependencies using pip:
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply Migrations**  
   Set up the database by applying migrations:
   ```bash
   python manage.py migrate
   ```

5. **Start the Development Server**  
   Run the server locally:
   ```bash
   python manage.py runserver
   ```

6. **Access the Application**  
   Visit the application at `http://127.0.0.1:8000/`.

---

## Admin Panel Access

1. **Create a Superuser**  
   To access the Django admin panel, create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

2. **Log In to Admin Panel**  
   Log in to the admin panel at `http://127.0.0.1:8000/admin/` using the credentials you created.

---

## Contributing
Feel free to fork the repository and submit pull requests for enhancements or bug fixes.
Rakesh Kumar T
rakeshptajlapur@gmail.com