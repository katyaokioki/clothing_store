from rest_framework import generics, permissions
from .models import User
from .serializers import UserSerializer

class SignupAPIView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        password = data.pop('password', None)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.create_user(
            email=serializer.validated_data['email'],
            name=serializer.validated_data.get('name',''),
            phone=serializer.validated_data.get('phone',''),
            password=password
        )
        out = UserSerializer(user).data
        from rest_framework.response import Response
        return Response(out, status=201)
