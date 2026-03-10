from django.urls import path

from . import views

urlpatterns = [
    path("paths/", views.LearningPathListView.as_view(), name="path-list"),
    path("paths/<slug:slug>/", views.LearningPathDetailView.as_view(), name="path-detail"),
    path(
        "paths/<slug:slug>/certificate/",
        views.CertificateView.as_view(),
        name="path-certificate",
    ),
    path("lessons/<slug:slug>/", views.LessonDetailView.as_view(), name="lesson-detail"),
    path(
        "lessons/<slug:slug>/complete/",
        views.LessonCompleteView.as_view(),
        name="lesson-complete",
    ),
]
