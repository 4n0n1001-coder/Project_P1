"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.contrib import admin, auth
from django.urls import path, include
from django.contrib.auth.views import LogoutView
#from django.contrib.auth.views import LoginView    # [2] Uncomment to import the django auth LoginView
from src.pages.views import Login

urlpatterns = [
    path('admin/', admin.site.urls),
	#path('login/', LoginView.as_view(template_name='pages/login.html')),   # [2] Always use internal frameworks if possible
    path('login/', Login),
	path('logout/', LogoutView.as_view(next_page='/')),
	path('', include('src.pages.urls'))
]

# SALT: pbkdf2_sha256