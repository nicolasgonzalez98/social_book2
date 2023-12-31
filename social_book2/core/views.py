from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Profile,Post,LikePost
# Create your views here.

@login_required(login_url='signin')
def index(request):
    user_object = User.objects.get(username = request.user.username)
    user_profile = Profile.objects.get(user = user_object)
    ctx = {
        'user_profile':user_profile
    }
    
    posts = Post.objects.all()
    ctx['posts'] = posts
    
    return render(request, 'index.html', ctx)

@login_required(login_url='signin')
def upload(request):
    if request.method == 'POST':
        user = request.user
        user_profile = Profile.objects.get(user=user)
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        new_post = Post.objects.create(user=user_profile, image=image, caption=caption)
        new_post.save()

        return redirect('/')
    else:
        return redirect('/')
@login_required(login_url='signin')
def like_post(request):
    post_id = request.GET.get('post_id')
    post = Post.objects.get(id = post_id)
    like = LikePost.objects.filter(post_id=post, username=request.user.username).first()
    
    if like == None:
        new_like = LikePost.objects.create(post_id=post, username=request.user.username)
        new_like.save()
        post.no_of_likes+=1
        post.save()
        return redirect(f'/#{post_id}')
    else:
        like.delete()
        post.no_of_likes-=1
        post.save()
        return redirect(f'/#{post_id}')
    

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email taken.')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username taken.')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)
                #Crear perfil
                user_model = User.objects.get(username= username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()

                return redirect('setting')
        else:
            messages.info(request, 'Password not matching.')
            return redirect('signup')
    else:
        return render(request, 'signup.html')


def signin(request):
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('signin')
    
    else:
        return render(request, 'signin.html')

@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')

@login_required(login_url='signin')
def settings(request):
    
    user_profile = Profile.objects.get(user = request.user)
    
    ctx = {'user_profile': user_profile}

    if request.method == 'POST':
        if request.FILES.get('image') == None:
            
            image = user_profile.profileimg
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.bio = bio
            user_profile.profileimg = image
            user_profile.location = location

            user_profile.save()
            
        else:
            
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.bio = bio
            user_profile.profileimg = image
            user_profile.location = location

            user_profile.save()
        return redirect('settings')
        
    return render(request, 'setting.html', ctx)

@login_required(login_url='signin')
def profile(request, username):
    ctx = {}
    user = User.objects.get(username=username)
    user_profile = Profile.objects.get(user = user)
    user_posts = Post.objects.filter(user=user_profile)
    ctx['user_profile'] = user_profile
    ctx['user_posts'] = user_posts
    ctx['length_posts'] = len(user_posts)
    
    return render(request, 'profile.html', ctx)