from django.urls import path
from . import views

#A view is a place where we put the "logic" of our application.
# 1.Receive the request information as well as parameters parsed from the url.
# 2.Fetch the information from the model, probably adding some logic.
# 3.Create a response by filling a template with the fetched info.

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
]