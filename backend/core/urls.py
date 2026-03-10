from django.urls import path

from . import views

urlpatterns = [
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("leaderboard/", views.LeaderboardView.as_view(), name="leaderboard"),
    path("achievements/", views.AchievementsView.as_view(), name="achievements"),
    path("analytics/", views.AnalyticsView.as_view(), name="analytics"),
    path("auth/login/", views.LoginView.as_view(), name="login"),
    path("auth/demo-users/", views.DemoUsersView.as_view(), name="demo-users"),
    path(
        "email-preview/<str:template_name>/",
        views.EmailPreviewView.as_view(),
        name="email-preview",
    ),
]
