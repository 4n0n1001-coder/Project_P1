from django.contrib import admin, auth
from django.urls import path, include
from django.contrib.auth.views import LogoutView

from src.pages.views import Login

# [FIX 1] Importing the safe login view
#from django.contrib.auth.views import LoginView    

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', Login),
    
    # [FIX 1] Replacing the vulnerable LoginView with Djangos' own framework
	#path('login/', LoginView.as_view(template_name='pages/login.html')),
 
	path('logout/', LogoutView.as_view(next_page='/')),
	path('', include('src.pages.urls'))
]

# SALT: pbkdf2_sha256