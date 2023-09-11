from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from users.serializers import UserSerializer, TokenAuthSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

User = get_user_model()


# Create your views here.
class CreateUserView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenAuthView(TokenObtainPairView):
    serializer_class = TokenAuthSerializer

