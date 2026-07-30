import secrets
import datetime
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from common.permissions import IsAdmin
from students.models import Student

User = get_user_model()

ALLOWED_REGISTRATION_ROLES = [User.Role.STUDENT, User.Role.INSTITUTE_OWNER]


def user_to_dict(user):
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'phone': user.phone,
        'role': user.role,
        'profile_image': user.profile_image.url if user.profile_image else None,
        'is_email_verified': user.is_email_verified,
        'is_phone_verified': user.is_phone_verified,
        'city': user.city,
        'state': user.state,
        'address': user.address,
        'pincode': user.pincode,
        'created_at': user.created_at.isoformat() if user.created_at else None,
        'updated_at': user.updated_at.isoformat() if user.updated_at else None,
    }


def student_to_dict(student):
    return {
        'id': student.id,
        'user': user_to_dict(student.user),
        'date_of_birth': str(student.date_of_birth) if student.date_of_birth else None,
        'learner_license_number': student.learner_license_number,
        'emergency_contact_name': student.emergency_contact_name,
        'emergency_contact_phone': student.emergency_contact_phone,
        'created_at': student.created_at.isoformat() if student.created_at else None,
        'updated_at': student.updated_at.isoformat() if student.updated_at else None,
    }


def generate_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {'access': str(refresh.access_token), 'refresh': str(refresh)}


class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        data = request.data
        email = data.get('email', '').strip()
        password = data.get('password', '')
        password_confirm = data.get('password_confirm', '')
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        phone = data.get('phone', '').strip()
        role = data.get('role', User.Role.STUDENT)

        errors = {}
        if not email:
            errors['email'] = 'This field is required.'
        if not password:
            errors['password'] = 'This field is required.'
        if not password_confirm:
            errors['password_confirm'] = 'This field is required.'
        if not first_name:
            errors['first_name'] = 'This field is required.'
        if not last_name:
            errors['last_name'] = 'This field is required.'

        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        if password != password_confirm:
            return Response({'password_confirm': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'email': 'A user with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        if role not in ALLOWED_REGISTRATION_ROLES:
            return Response({'role': 'You can only register as a student or institute owner.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(password)
        except ValidationError as e:
            return Response({'password': list(e.messages)}, status=status.HTTP_400_BAD_REQUEST)

        username = email.split('@')[0]
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f'{base_username}{counter}'
            counter += 1

        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role=role,
        )
        user.set_password(password)

        email_token = secrets.token_urlsafe(32)
        user.email_verification_token = email_token
        user.email_verification_sent_at = timezone.now()
        user.save()

        if role == User.Role.STUDENT:
            Student.objects.create(user=user)

        return Response({
            'user': user_to_dict(user),
            'tokens': generate_tokens(user),
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        email = request.data.get('email', '').strip()
        password = request.data.get('password', '')

        if not email or not password:
            return Response({'error': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.check_password(password):
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({
            'user': user_to_dict(user),
            'tokens': generate_tokens(user),
        })


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'error': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(user_to_dict(request.user))

    def put(self, request):
        return self._update(request)

    def patch(self, request):
        return self._update(request)

    def _update(self, request):
        data = request.data
        user = request.user
        updatable_fields = ['first_name', 'last_name', 'phone', 'city', 'state', 'address', 'pincode']

        for field in updatable_fields:
            if field in data:
                setattr(user, field, data[field])

        if 'profile_image' in request.FILES:
            user.profile_image = request.FILES['profile_image']

        user.save()
        return Response(user_to_dict(user))


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        old_password = data.get('old_password', '')
        new_password = data.get('new_password', '')
        new_password_confirm = data.get('new_password_confirm', '')

        if not old_password or not new_password or not new_password_confirm:
            return Response({'error': 'old_password, new_password, and new_password_confirm are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.check_password(old_password):
            return Response({'old_password': 'Old password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != new_password_confirm:
            return Response({'new_password_confirm': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(new_password, user=request.user)
        except ValidationError as e:
            return Response({'new_password': list(e.messages)}, status=status.HTTP_400_BAD_REQUEST)

        request.user.set_password(new_password)
        request.user.save()
        return Response({'detail': 'Password changed successfully.'})


class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip()

        if not email:
            return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'detail': 'Password reset link has been sent to your email.'})


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('token', '')
        new_password = request.data.get('new_password', '')

        if not token or not new_password:
            return Response({'error': 'token and new_password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(new_password)
        except ValidationError as e:
            return Response({'new_password': list(e.messages)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'detail': 'Password has been reset successfully.'})


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        token = request.query_params.get('token')

        if not token:
            return Response({'error': 'Token is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email_verification_token=token)
        except User.DoesNotExist:
            return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)

        if user.email_verification_sent_at and (timezone.now() - user.email_verification_sent_at).total_seconds() > 86400:
            return Response({'error': 'Token has expired. Please request a new verification email.'}, status=status.HTTP_400_BAD_REQUEST)

        user.is_email_verified = True
        user.email_verification_token = ''
        user.save()
        return Response({'detail': 'Email verified successfully.'})


class StudentProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == 'admin':
            id = request.query_params.get('pk')
            if id:
                try:
                    student = Student.objects.get(pk=id)
                except Student.DoesNotExist:
                    return Response({'error': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)
            else:
                students = Student.objects.all()
                return Response([student_to_dict(s) for s in students])
        else:
            student, _ = Student.objects.get_or_create(user=request.user)

        return Response(student_to_dict(student))

    def put(self, request):
        return self._update(request)

    def patch(self, request):
        return self._update(request)

    def _update(self, request):
        if request.user.role == 'admin':
            id = request.query_params.get('pk')
            if not id:
                return Response({'error': 'pk query parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                student = Student.objects.get(pk=id)
            except Student.DoesNotExist:
                return Response({'error': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            student, _ = Student.objects.get_or_create(user=request.user)

        data = request.data
        updatable_fields = ['date_of_birth', 'learner_license_number', 'emergency_contact_name', 'emergency_contact_phone']

        for field in updatable_fields:
            if field in data:
                setattr(student, field, data[field])

        student.save()
        return Response(student_to_dict(student))


class UserListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        users = User.objects.all()

        search = request.query_params.get('search', '').strip()
        if search:
            users = users.filter(
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(phone__icontains=search)
            )

        ordering = request.query_params.get('ordering', '-created_at')
        allowed_orderings = ['created_at', '-created_at', 'email', '-email', 'role', '-role']
        if ordering in allowed_orderings:
            users = users.order_by(ordering)

        return Response([user_to_dict(u) for u in users])


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, id):
        try:
            user = User.objects.get(pk=id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        return Response(user_to_dict(user))
