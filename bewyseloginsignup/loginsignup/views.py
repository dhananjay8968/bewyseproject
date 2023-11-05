from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods
import firebase_admin
from firebase_admin import credentials, auth
from profiles.models import UserProfile
# Initialize Firebase Admin SDK with your service account credentials
cred = credentials.Certificate("./bewyseproject-firebase-adminsdk-56zq8-b5a7693f50.json")
firebase_admin.initialize_app(cred)

@csrf_exempt
@require_POST
def register(request):
    try:
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        if not email or not password:
            return JsonResponse({"error": "Email and password are required"}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "A user with that username already exists"}, status=400)

        if len(password) < 8:
            return JsonResponse({"error": "This password is too short. It must contain at least 8 characters"}, status=400)

        if len(username) > 100 or len(email) > 100 or (first_name is not None and len(first_name) > 100) or (last_name is not None and len(last_name) > 100):
            return JsonResponse({"error": "Only 100 characters are allowed for a field."}, status=400)

        # Create a user with Firebase Authentication
        user = auth.create_user(
            email=email,
            password=password,
            display_name=username  # Set the username as the display name
        )

        # Associate additional user data with the Django User model
        user_db = User.objects.create_user(username, email, password)
        user_db.first_name = first_name
        user_db.last_name = last_name
        user_db.save()


        profile = UserProfile(user=user_db, first_name=first_name, last_name=last_name)
        profile.save()

        register_api_response = {
            "username": user_db.username,
            "email": user_db.email
        }
        return JsonResponse(register_api_response)
    except Exception as e:
        return JsonResponse({"error": "An error occurred during registration: " + str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET", "POST"])
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
    elif request.method == 'GET':
        username = request.GET.get('username')
        password = request.GET.get('password')

    if username and password:
        try:
            # Get the user's email based on the username
            user = User.objects.filter(username=username).first()
            if user:
                email = user.email

                # Authenticate the user using Firebase
                user_in_firebase = auth.get_user_by_email(email)
                custom_token = auth.create_custom_token(user_in_firebase.uid)
                # Return the custom token in the response
                return JsonResponse({"custom_token": str(custom_token)})
            else:
                return JsonResponse({"error": "Username or password is invalid"}, status=401)
        except Exception as e:
            return JsonResponse({"error": "An error occurred while authenticating: " + str(e)}, status=500)
    else:
        return JsonResponse({"error": "Username and password are required"}, status=400)
