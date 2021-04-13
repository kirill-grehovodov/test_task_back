from django.urls import path

from api.views import FollowerView, UserCountryView, UserTagView, PostListView, PostView, CreateCommentView, UserView, \
    CreatePostView, like, dislike, CountryView

urlpatterns = [
    path('follower/<int:pk>/', FollowerView.as_view()),
    path('tagfollower/<int:pk>/', UserTagView.as_view()),
    path('countryfollower/<str:code>/', UserCountryView.as_view()),
    path('posts/', PostListView.as_view()),
    path('post/<int:pk>/', PostView.as_view()),
    path('<int:pk>/comment/create/', CreateCommentView.as_view()),
    path('post/create/', CreatePostView.as_view()),
    path('user/<int:pk>/', UserView.as_view()),
    path('post/<int:pk>/like/', like),
    path('post/<int:pk>/dislike/', dislike),
    path('country/<str:code>', CountryView.as_view()),
]