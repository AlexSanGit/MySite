from Blog import views
from django.urls import path, include
from Blog import views
from Blog.views import *

urlpatterns = [
    path('', HomePage.as_view(), name='home'),
    # path('register/', RegisterUser.as_view(), name='register'),
    path('post/<slug:post_slug>/', PostDetail.as_view(), name='post'),
    path('category/<slug:cat_slug>/', CategoryPosts.as_view(), name='category'),
    path('about/', about, name='about'),
    path('addpage/', AddPost.as_view(), name='add_page'),
    path('contact/', contact, name='contact'),
    # path('user/<int:user_id>/', user_detail, name='user_detail'),
    # path('get_child_categories/<int:parent_category_id>/', views.get_child_categories, name='get_child_categories'),
    path('post/<int:pk>/update/', PostEditView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', DeletePostView.as_view(), name='post-delete'),
    # path('login/', LoginUser.as_view(), name='login'),
    # path('logout/', logout_user, name='logout'),


]