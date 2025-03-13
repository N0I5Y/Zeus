import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "resume_project.settings")  # ✅ Fix this if incorrect

application = get_asgi_application()