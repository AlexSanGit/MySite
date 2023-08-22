from django.urls import path
from Blog import views
from Blog.views import *

urlpatterns = [
    path('', HomePage.as_view(), name='home'),
    path('post/<slug:post_slug>/', PostDetail.as_view(), name='post'),
    path('category/<slug:cat_slug>/', CategoryPosts.as_view(), name='category'),
    path('about/', about, name='about'),
    path('addpage/', AddPost.as_view(), name='add_page'),
    path('contact/', contact, name='contact'),
    path('notifications/', views.show_notifications, name='show_notifications'),
    path('clear_notifications/', views.clear_notifications, name='clear_notifications'),
    path('post/<int:pk>/update/', PostEditView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', DeletePostView.as_view(), name='post-delete'),
    path('comments/<int:pk>/', comment_detail_view, name='comment_detail'),



]