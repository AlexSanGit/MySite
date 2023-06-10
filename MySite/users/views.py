from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render, get_object_or_404

from Blog.utils import menu
from users.choices.city_choices import CITY_CHOICES
from users.forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from users.models import Profile


# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if request.method == 'POST':
            form = UserRegisterForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password1']
                city = form.cleaned_data['city']

                # Проверка наличия пользователя с таким именем
                if User.objects.filter(username=username).exists():
                    return render(request, 'registration.html',
                                  {'form': form, 'error_message': 'Username already exists'})

                # Создание пользователя
                user = User.objects.create_user(username=username, password=password)

                # Создание профиля пользователя
                # profile = Profile(user=user, city=city)
                # profile.save()
            login(request, user)
            messages.success(request, f'Ваш аккаунт создан: можно войти на сайт.')
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html',  {'form': form, 'city_choices': CITY_CHOICES})


# @login_required
# def profile(request):
#     context = {'profile': profile, 'menu': menu}
#     return render(request, 'users/profile.html', context)


@login_required
def profile(request, user_id):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Ваш профиль успешно обновлен.')
            # return redirect('profile')
            redirect(f'/profile/{user_id}')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    user = get_object_or_404(User, id=user_id)
    prof = get_object_or_404(Profile, user=user)
    context = {
        'u_form': u_form,
        'p_form': p_form,
        'menu': menu,
        'profile': prof

    }

    return render(request, 'users/profile.html', context)
