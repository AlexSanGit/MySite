from Blog.views import *
from django.urls import path, re_path


urlpatterns = [
    path('', HomePage.as_view(), name='home'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('post/<slug:post_slug>/', PostDetail.as_view(), name='post'),
    path('category/<slug:cat_slug>/', CategoryPosts.as_view(), name='category'),
    path('about/', about, name='about'),
    path('addpage/', AddPost.as_view(), name='add_page'),
    path('contact/', contact, name='contact'),
    # path('category/<slug:cat_slug>/', PartCarCategory.as_view(), name='category'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    # path(r'^comment/(?P<article_id>[0-9]+)/$', AddComments.as_view(), name='add_comments'),
    # path('<int:pk>', AddComments.as_view(), name='add_comments'),
    # url(r'^(?P<article_id>[0-9]+)/$', views.EArticleView.as_view(), name='article'),
    # url(r'^comment/(?P<article_id>[0-9]+)/$', views.add_comment, name='add_comment'),

]