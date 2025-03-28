import os
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plant_booking.settings")
import django
django.setup()

# Set UTF-8 encoding for output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from django.core.management import call_command
from django.core.serializers.json import DjangoJSONEncoder
import json

# Create dumps in specific order
models = [
    ('auth.user', 'users.json'),
    ('admin_interface', 'admin_interface.json'),
    ('plantation.corporate', 'corporate.json'),
    ('plantation.plantation', 'plantations.json'),
    ('plantation.employee', 'employees.json'),
    ('plantation.timeline', 'timelines.json'),
    ('plantation.comment', 'comments.json'),
    ('plantation.visitrequest', 'visitrequests.json'),
]

for model, filename in models:
    print(f"Dumping {model} to {filename}")
    try:
        # Use custom dump with UTF-8 encoding
        with open(filename, 'w', encoding='utf-8') as f:
            call_command('dumpdata', model, indent=2, format='json', stdout=f)
        print(f"Successfully dumped {model}")
    except Exception as e:
        print(f"Error dumping {model}: {e}")