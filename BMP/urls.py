"""
URL configuration for BMP project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from v0.views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', landing_page, name="landing_page"),
    path('home/', Home_page, name='Home_page'),
    path("auth/", Login_sign, name="Login_sign"),
    path('login/',Login, name="Login"),
    path('list_plot/', list_plot, name="list_plot"),
    path('plot_page/<int:id>/', plot_page, name='plot_page'),
    path('search_plots/', search_plots, name='search_plots'),
    path("profile_page/", profile_page, name="profile_page"),
    path('payout_page', payout_page, name="payout_page"),
    path('imadmin/', imadmin, name="imadmin"),
    path('del_user/', del_user, name="del_user"),
    path('del_plot/', del_plot, name="del_plot"),
    path('success_payment/', success_payment, name="success_payment"),
    path('exclusive/', exclusive_page, name="exclusive_page"),
    path('buy/', buy_page, name="buy_page"),
    path('rent/', rent_page, name="rent_page"),
    path('about/', about, name="about"),
    path('contact/', contact, name="contact"),
    path('terms/', terms, name="terms"),
    path('policy/', policy, name="policy"),
    path('sell/', sell_page, name = "sell_page"),
    path('reset/', reset, name = "reset"),
    path('otp/', otp, name = "otp"),
    path('forget/', forget, name = "forget"),
    path('for_reset/', for_reset, name="for_reset"),
    # path('otp/', otp, name="otp"),
    path('logout/', custom_logout, name='custom_logout'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
