import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "resume_project.settings")  # ✅ Fix this if incorrect

application = get_wsgi_application()
