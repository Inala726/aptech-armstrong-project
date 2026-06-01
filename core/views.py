from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Profile, Address, Attempt, Feedback
from .utils import is_armstrong, find_armstrong_in_range


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """User registration with name, email, contact, username, password."""
    data = request.data
    required = ['first_name', 'last_name', 'email', 'username', 'password', 'contact_number']
    
    for field in required:
        if not data.get(field):
            return Response({'error': f'{field} is required.'}, status=400)

    if User.objects.filter(username=data['username']).exists():
        return Response({'error': 'Username already taken.'}, status=400)

    if User.objects.filter(email=data['email']).exists():
        return Response({'error': 'Email already registered.'}, status=400)

    user = User.objects.create_user(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        first_name=data['first_name'],
        last_name=data['last_name'],
    )
    Profile.objects.create(user=user, contact_number=data['contact_number'])

    return Response({'message': 'Registration successful.'}, status=201)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Returns JWT access + refresh tokens on successful login."""
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Invalid credentials.'}, status=401)

    refresh = RefreshToken.for_user(user)
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }
    })


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user

    if request.method == 'GET':
        profile = user.profile
        return Response({
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'contact_number': profile.contact_number,
        })

    elif request.method == 'PUT':
        data = request.data
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.email = data.get('email', user.email)
        user.save()
        user.profile.contact_number = data.get('contact_number', user.profile.contact_number)
        user.profile.save()
        return Response({'message': 'Profile updated.'})

    elif request.method == 'DELETE':
        user.delete()
        return Response({'message': 'Account deleted.'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_address(request):
    data = request.data
    address = Address.objects.create(
        user=request.user,
        street=data.get('street', ''),
        city=data.get('city', ''),
        state=data.get('state', ''),
        country=data.get('country', ''),
        zip_code=data.get('zip_code', ''),
    )
    return Response({'message': 'Address added.', 'id': address.id}, status=201)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_single(request):
    """Check if a single number is an Armstrong number."""
    number = request.data.get('number')

    if number is None:
        return Response({'error': 'number is required.'}, status=400)

    try:
        number = int(number)
        if number < 0:
            raise ValueError
    except (ValueError, TypeError):
        return Response({'error': 'Provide a valid non-negative integer.'}, status=400)

    result = is_armstrong(number)

    # Save to Attempt history
    Attempt.objects.create(
        user=request.user,
        mode='single',
        input_number=number,
        is_armstrong=result,
    )

    return Response({
        'number': number,
        'is_armstrong': result,
        'message': 'It is an Armstrong Number' if result else 'Not an Armstrong Number',
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_range(request):
    """Find all Armstrong numbers between min and max."""
    min_val = request.data.get('min')
    max_val = request.data.get('max')

    if min_val is None or max_val is None:
        return Response({'error': 'Both min and max are required.'}, status=400)

    try:
        min_val = int(min_val)
        max_val = int(max_val)
    except (ValueError, TypeError):
        return Response({'error': 'min and max must be integers.'}, status=400)

    if min_val < 0:
        return Response({'error': 'min must be non-negative.'}, status=400)
    if min_val > max_val:
        return Response({'error': 'min must be less than or equal to max.'}, status=400)
    if max_val - min_val > 10_000_000:
        return Response({'error': 'Range too large. Keep it under 10 million.'}, status=400)

    results = find_armstrong_in_range(min_val, max_val)

    Attempt.objects.create(
        user=request.user,
        mode='range',
        range_min=min_val,
        range_max=max_val,
        armstrong_numbers_found=results,
        count_found=len(results),
    )

    return Response({
        'min': min_val,
        'max': max_val,
        'armstrong_numbers': results,
        'count': len(results),
    })



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def attempt_history(request):
    """Return all attempts made by the logged-in user."""
    attempts = Attempt.objects.filter(user=request.user).order_by('-attempted_at')
    data = []
    for a in attempts:
        data.append({
            'id': a.id,
            'mode': a.mode,
            'input_number': a.input_number,
            'is_armstrong': a.is_armstrong,
            'range_min': a.range_min,
            'range_max': a.range_max,
            'armstrong_numbers_found': a.armstrong_numbers_found,
            'count_found': a.count_found,
            'attempted_at': a.attempted_at,
        })
    return Response({'total_attempts': len(data), 'attempts': data})



@api_view(['POST'])
@permission_classes([AllowAny])
def submit_feedback(request):
    data = request.data
    if not data.get('name') or not data.get('email') or not data.get('message'):
        return Response({'error': 'name, email, and message are required.'}, status=400)

    Feedback.objects.create(
        user=request.user if request.user.is_authenticated else None,
        name=data['name'],
        email=data['email'],
        message=data['message'],
    )
    return Response({'message': 'Feedback submitted. Thank you!'}, status=201)



@api_view(['GET'])
@permission_classes([AllowAny])
def contact_us(request):
    return Response({
        'organization': 'Lehman Educational Services',
        'email': 'contact@lehman.edu',
        'phone': '+1-800-000-0000',
        'address': '123 Education Blvd, New York, NY 10001',
    })