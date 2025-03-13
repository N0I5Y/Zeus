from django.urls import path
from .views import ResumeUploadView, JobDescriptionUploadView, ResumeEnhancementView

urlpatterns = [
    path('upload_resume/', ResumeUploadView.as_view(), name='upload_resume'),  # ✅ Correct path
    path('upload_jd/', JobDescriptionUploadView.as_view(), name='upload_jd'),
    path('enhance_resume/', ResumeEnhancementView.as_view(), name='enhance_resume'),
]
