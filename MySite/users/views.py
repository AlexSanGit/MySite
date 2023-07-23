from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import redirect, render, get_object_or_404

from Blog.utils import menu
from users.choices.city_choices import CITY_CHOICES
from users.forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from users.models import Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            username = form.cleaned_data.get('username')
            form.save()
            login(request, user)
            messages.success(request, f'Ваш аккаунт создан.')
        return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html',  {'form': form, 'city_choices': CITY_CHOICES})


@login_required
def profile(request, user_id):

    user = get_object_or_404(User, id=user_id)
    prof = get_object_or_404(Profile, user=user)

    if request.method == 'POST':
        # u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        # profile.is_seller = 'is_seller' in request.POST
        # if u_form.is_valid() and p_form.is_valid():
        if p_form.is_valid():
            # Обновление фото
            if 'image' in request.FILES:
                prof.image = request.FILES['image']
            # Обновление поля city
            city = request.POST.get('city', '')
            prof.city = city
            # u_form.save()
            p_form.save()
            # Обновление статуса is_seller
            is_seller = request.POST.get('is_seller', False)
            prof.is_seller = bool(is_seller)
            prof.save()
            messages.success(request, f'Ваш профиль успешно обновлен.')
            return redirect(f'/profile/{user_id}')

    else:
        # u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    user = get_object_or_404(User, id=user_id)
    prof = get_object_or_404(Profile, user=user)
    context = {
        # 'u_form': u_form,
        'p_form': p_form,
        'menu': menu,
        'profile': prof

    }

    return render(request, 'users/profile.html', context)
