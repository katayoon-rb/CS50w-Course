from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
import json

from .models import User, Post, Follow, Like


def remove_like(request, post_id):
    post = Post.objects.get(pk=post_id)
    user = User.objects.get(pk=request.user.id)
    like = Like.objects.filter(user=user, post=post)
    like.delete()
    return JsonResponse({"message": "Like removed!"})

def add_like(request, post_id):
    post = Post.objects.get(pk=post_id)
    user = User.objects.get(pk=request.user.id)
    new_like = Like(user=user, post=post)
    new_like.save()
    return JsonResponse({"message": "Like added!"})


def edit(request, post_id):
    if request.method == "POST":
        data = json.loads(request.body)
        editPost = Post.objects.get(pk=post_id)
        editPost.content = data['content']
        editPost.save()
        return JsonResponse({
            "message": "Change successful!",
            "data": data['content']   
        })
        

def index(request):
    allPosts = Post.objects.all().order_by('id').reverse()
    
    paginator = Paginator(allPosts, 10)
    pageNumber = request.GET.get('page')
    postsPerPage = paginator.get_page(pageNumber)
    
    allLikes = Like.objects.all()
    whoYouLiked = []
    try:
        for like in allLikes:
            if like.user.id == request.user.id:
                whoYouLiked.append(like.post.id)
    except:
        whoYouLiked = []

    
    return render(request, "network/index.html", {
        "allPosts": allPosts,
        "postsPerPage": postsPerPage,
        "whoYouLiked": whoYouLiked
    })


def new_post(request):
    if request.method == "POST":
        content = request.POST['content']
        user = User.objects.get(pk=request.user.id)
        post = Post(content=content, user=user)
        post.save()
        return HttpResponseRedirect(reverse(index))


def profile(request, user_id):
    user = User.objects.get(pk=user_id)
    allPosts = Post.objects.all().filter(user=user).order_by('id').reverse()
    
    following = Follow.objects.filter(user=user)
    followers = Follow.objects.filter(followed_user=user)
    
    try:
        checkFollow = followers.filter(user=User.objects.get(pk=request.user.id))
        if len(checkFollow) != 0:
            isFollowing = True
        else: 
            isFollowing = False
    except:
        isFollowing = False
    
    paginator = Paginator(allPosts, 10)
    pageNumber = request.GET.get('page')
    postsPerPage = paginator.get_page(pageNumber)
    
    return render(request, "network/profile.html", {
        "userProfile": user,
        "allPosts": allPosts,
        "postsPerPage": postsPerPage,
        "username": user.username,
        "following": following,
        "followers": followers,
        "isFollowing": isFollowing
    })


def follow(request):
    followedUser = request.POST['followed_user']
    currentUser = User.objects.get(pk=request.user.id)
    userFollowData = User.objects.get(username=followedUser)
    f = Follow(user=currentUser, followed_user=userFollowData)
    f.save()
    user_id = userFollowData.id
    return HttpResponseRedirect(reverse("profile", kwargs={'user_id': user_id}))

def unfollow(request):
    followedUser = request.POST['followed_user']
    currentUser = User.objects.get(pk=request.user.id)
    userFollowData = User.objects.get(username=followedUser)
    f = Follow.objects.get(user=currentUser, followed_user=userFollowData)
    f.delete()
    user_id = userFollowData.id
    return HttpResponseRedirect(reverse("profile", kwargs={'user_id': user_id}))


def following(request):
    currentUser = User.objects.get(pk=request.user.id)
    followingPeople = Follow.objects.filter(user=currentUser)
    allPosts = Post.objects.all().order_by('id').reverse()
    
    followingPosts = []
    for post in allPosts:
        for person in followingPeople:
            if person.followed_user == post.user:
                followingPosts.append(post)
                
    paginator = Paginator(followingPosts, 10)
    pageNumber = request.GET.get('page')
    postsPerPage = paginator.get_page(pageNumber)
    
    return render(request, "network/following.html", {
        "postsPerPage": postsPerPage,
    })
    

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

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

        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

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
