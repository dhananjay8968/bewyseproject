from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET,require_POST
import firebase_admin
from firebase_admin import credentials, auth
from profiles.models import UserProfile
from profiles.serializers import UserProfileSerializer



@csrf_exempt
@require_GET
def view_profile(request):
    custom_token = request.META.get('HTTP_AUTHORIZATION')
    custom_token = custom_token.replace("Bearer ","")
    username = request.GET.get('username')
    try:
        decoded_token = auth.verify_id_token(custom_token)
        uid = decoded_token['uid']

        user = auth.get_user(uid)
        email = user.email
        profile = UserProfile.objects.get(user__username=username)
        serializer = UserProfileSerializer(profile)
        profile_data = {
            "username": username,
            "email": email,
            "full_name": serializer.data['full_name']
        }
        return JsonResponse(profile_data)
    except auth.ExpiredIdTokenError:
        return JsonResponse({"error": "Token has expired"},status=401)
    except Exception as e:
        return JsonResponse({"error": "An error occured while fetching the profile: " + str(e)},status=401)

@csrf_exempt
@require_POST
def edit_profile(request):
    custom_token = request.META.get('HTTP_AUTHORIZATION')
    custom_token = custom_token.replace("Bearer ","")
    try:
        decoded_token = auth.verify_id_token(custom_token)
        uid = decoded_token['uid']

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        user = auth.get_user(uid)

        try:
            profile = UserProfile.objects.get(user__username=user.display_name)
            profile.user.first_name = first_name
            profile.user.last_name = last_name
            profile.user.save()
            profile.save()
        except UserProfile.DoesNotExist:
            # If the user doesn't have a profile, create one
            user_profile = UserProfile(user=user)
            user_profile.save()
            user.user.first_name = first_name
            user.user.last_name = last_name
            user.user.save()

        # Fetch the updated data
        profile = UserProfile.objects.get(user__username=user.display_name)
        serializer = UserProfileSerializer(profile)
        profile_data = {
            "username": user.display_name,
            "email": user.email,
            "full_name": serializer.data['full_name']
        }

        return JsonResponse(profile_data)
    except auth.ExpiredIdTokenError:
        return JsonResponse({"error": "Token has expired"}, status=401)
    except Exception as e:
        return JsonResponse({"error": "An error occurred while updating the profile: " + str(e)}, status=401)
