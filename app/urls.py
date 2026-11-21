"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from questions import views
from core import views as core_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('question/<int:question_id>/', views.question, name='question'),
    path('question/<int:question_id>/vote/', views.vote_question, name='vote_question'),
    path('answer/<int:answer_id>/vote/', views.vote_answer, name='vote_answer'),
    path(
    'answer/<int:answer_id>/correct/',
    views.toggle_correct_answer,
    name='toggle_correct_answer'
    ),
    path('hot/', views.hot, name='hot'),
    path('tag/<slug:tag_name>/', views.tag, name='tag'),
    path('ask/', views.ask, name='ask'),
    path('login/', core_views.UserLoginView.as_view(), name='login'),
    path('logout/', core_views.UserLogoutView.as_view(), name='logout'),
    path('signup/', core_views.SignupView.as_view(), name='signup'),
    path('profile/', core_views.ProfileView.as_view(), name='profile'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )

    from debug_toolbar.toolbar import debug_toolbar_urls
    urlpatterns += debug_toolbar_urls()