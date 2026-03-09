from django.contrib.auth import authenticate, login
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Achievement, UserProfile
from .serializers import (
    AchievementWithUnlockSerializer,
    LeaderboardSerializer,
    UserProfileSerializer,
)


class ProfileView(RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile


class LeaderboardView(ListAPIView):
    serializer_class = LeaderboardSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return UserProfile.objects.select_related("user").order_by("-xp")[:20]


class AchievementsView(ListAPIView):
    serializer_class = AchievementWithUnlockSerializer
    permission_classes = [IsAuthenticated]
    queryset = Achievement.objects.all()


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            return Response(
                {"error": "Username and password required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {"error": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        login(request, user)
        return Response({"username": user.username, "id": user.id})


DEMO_ROLES = {
    "demo": "Lernende",
    "anna": "Top-Lernende",
    "marco": "Fortgeschritten",
}


class DemoUsersView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        demo_usernames = list(DEMO_ROLES.keys())
        profiles = UserProfile.objects.select_related("user").filter(
            user__username__in=demo_usernames
        )
        result = []
        for profile in profiles:
            user = profile.user
            result.append(
                {
                    "username": user.username,
                    "display_name": f"{user.first_name} {user.last_name}",
                    "avatar_color": profile.avatar_color,
                    "role": DEMO_ROLES.get(user.username, "Lernende"),
                }
            )
        return Response(result)
