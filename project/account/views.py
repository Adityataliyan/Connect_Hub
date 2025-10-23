from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .models import Comment
from .models import Profile

def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Check for password match
        if password1 != password2:
            return render(request, 'account/signup.html', {'error': 'Passwords do not match'})

        # Check if username exists
        if User.objects.filter(username=username).exists():
            return render(request, 'account/signup.html', {'error': 'Username already exists'})

        # Create the user
        user = User.objects.create_user(username=username, password=password1, email=email)
        user.save()

        # Optionally store phone number in session or profile model if you add one later
        return redirect('login')

    return render(request, 'account/signup.html')



def login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            auth_login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'account/login.html', {'error': 'Invalid credentials'})
    return render(request, 'account/login.html')

@login_required(login_url='login')
def dashboard(request):
    if request.method == "POST":
        text = request.POST['comment']
        Comment.objects.create(user=request.user, text=text, status='Draft')
    
    comments = Comment.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'account/dashboard.html', {
        'comments': comments,
        'username': request.user.username   # ✅ Always fetch from session
    })

def logout(request):
    auth_logout(request)
    request.session.flush()   # ✅ Clears all old session data
    return redirect('login')


@login_required(login_url='login')
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        gender = request.POST.get('gender')
        address = request.POST.get('address')
        profession = request.POST.get('profession')

        # Update User info
        request.user.first_name = full_name
        request.user.email = email
        request.user.save()

        # Update Profile info
        profile.phone = phone
        profile.gender = gender
        profile.address = address
        profile.profession = profession
        profile.save()

        return render(request, 'account/edit_profile.html', {'profile': profile, 'message': 'Profile updated successfully!'})

    return render(request, 'account/edit_profile.html', {'profile': profile})



@login_required(login_url='login')
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    if request.method == "POST":
        new_text = request.POST.get('comment')
        comment.text = new_text
        comment.save()
        return redirect('dashboard')
    return render(request, 'account/edit_comment.html', {'comment': comment})

@login_required(login_url='login')
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    comment.delete()
    return redirect('dashboard')