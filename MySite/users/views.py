from Blog.menu import menu
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render, get_object_or_404
from users.choices.city_choices import CITY_CHOICES
from users.choices.welcome_code import VALID_ACTIVATION_CODES
from users.forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from users.models import Profile


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            city = form.cleaned_data.get('city')
            # Проверка кода активации
            welcome_code = str(form.cleaned_data.get('welcome_code'))
            # Проверяем, существует ли уже пользователь с таким именем
            if User.objects.filter(username=username).exists():
                return render(request, 'users/register.html', {'form': form, 'error_message': 'Уже есть такой пользователь'})

            if welcome_code in VALID_ACTIVATION_CODES:
                pass
            else:
                print(welcome_code)
                # form.add_error('welcome_code', 'Неверный код активации')
                return render(request, 'users/register.html', {'form': form, 'city_choices': CITY_CHOICES,
                                                               'error_message': 'Неверный код активации'})

            user = form.save()
            # Проверяем, существует ли профиль для данного пользовател
            profile, created = Profile.objects.get_or_create(user=user)
            # Обновляем поля профиля, если был создан новый профиль
            if created:
                profile.time_glybinie = '00:00'
                profile.city = city
                profile.save()
            login(request, user)
            messages.success(request, f'Ваш аккаунт создан.')
            return redirect('home')
    else:
        form = UserRegisterForm()

    return render(request, 'users/register.html', {'form': form, 'city_choices': CITY_CHOICES})


@login_required
def profile(request, user_id):

    user = get_object_or_404(User, id=user_id)
    prof = get_object_or_404(Profile, user=user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
             # Обновление фото
            if 'image' in request.FILES:
                prof.image = request.FILES['image']
            # Обновление поля city
            first_name = u_form.cleaned_data.get('first_name')
            last_name =  u_form.cleaned_data.get('last_name')
            city = request.POST.get('city', '')
            prof.city = city
            # u_form.save()
            p_form.save()
            # Обновление статуса is_seller
            is_seller = request.POST.get('is_seller', False)
            prof.is_seller = bool(is_seller)
            # Обновление полей first_name и last_name в модели User
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            prof.save()
            messages.success(request, f'Ваш профиль успешно обновлен.')
            return redirect(f'/profile/{user_id}')

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
