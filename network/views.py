from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render,redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404

import json

from .models import User, Post

def index(request):
    post_list = Post.objects.order_by("-timestamp").all()

    pagination_data = pagination(request, post_list)

    if request.method == "POST":
        user = request.user
        text = request.POST["text"]
        cleaned_text = text.strip()
        if not text:
            return JsonResponse({
                "error": "can't post empty text."
             }, status=400)
            
        post = Post(user=user , text=text)
        post.save()
        return HttpResponseRedirect(reverse("index"))

    return render(request, "network/index.html", {
        "post_list" : post_list,
        "pagination_data": pagination_data
    })



def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

def profile_page(request, user_name):
    user_profile = User.objects.get(username=user_name)
    current_user = request.user

    if request.method == "POST":
        follow = request.POST["follow"]
        if follow == "Follow":
            user_profile.followers.add(current_user)
        elif follow == "UnFollow":
            user_profile.followers.remove(current_user)
        else:
            pass

    follow_button_visibility = request.user.is_authenticated and request.user.username != user_name

    if current_user in user_profile.followers.all():
        follow_txt = "UnFollow"
    else :
        follow_txt = "Follow"

    followers_count = user_profile.count_followers()
    following_count = user_profile.count_following()
    post_list = Post.objects.filter(user__username=user_name).order_by("-timestamp").all()
    pagination_data = pagination(request, post_list)

    return render(request, "network/profile_page.html", {
        "user_name" : user_name,
        "followers_count" : followers_count,
        "following_count" : following_count,
        "posts" : post_list,
        "follow_button_visibility" : follow_button_visibility,
        "follow_txt" : follow_txt,
        "pagination_data" : pagination_data
    })

def following(request):
    followed_users = User.objects.filter(followers=request.user)
    posts_by_followed = Post.objects.filter(user__in=followed_users)

    pagination_data = pagination(request, posts_by_followed)

    return render(request, "network/following.html", {
        "posts": posts_by_followed,
        "pagination_data":pagination_data
    })

def pagination(request, post_list):
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'paginator': paginator.num_pages > 1,
        'page_obj': page_obj,
    }

@csrf_exempt
def edit_post(request, post_id):
    if request.method == "POST":
        post_to_edit = get_object_or_404(Post, id=post_id)
        read_json = json.loads(request.body)
        post_to_edit.text = read_json['edited_text']
        post_to_edit.save()
        return JsonResponse({'success': True, 'edited_text': post_to_edit.text})

    return HttpResponse(status=404)


@csrf_exempt
def toggle_like(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        user = request.user 
        if user in post.likes.all():
            post.likes.remove(user)
            liked = False
        else:
            post.likes.add(user)
            liked = True
        post.save()
        return JsonResponse({'liked': liked, 'like_count': post.likes.count()})
    return HttpResponseNotAllowed(['POST'])