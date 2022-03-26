"""restaurant URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.conf.urls.static import static
from django.conf import settings

from main.views import home
from main.views import main
from main.views import cart
from main.views import checkout
from main.views import updateItem
from main.views import processOrder
from main.views import loginPage
from main.views import register
from main.views import logoutPage

from main.views import customerProfile
from main.views import restaurantOwnerProfile

from main.views import customerInfoUpdate
from main.views import customerOrderCancel

from main.views import deleteRestaurantProduct
from main.views import updateRestaurantProduct
from main.views import addRestaurantProduct
from main.views import updateRestaurantOrder

from main.views import detailedProductView
from main.views import addProductReview

from main.views import contactus

from main.views import category_based_display_items


urlpatterns = [

    path('register/', register, name='register'),
    path('login/', loginPage, name='login'),
    path('logout/', logoutPage, name='logout'),
    path('',home,name='home'),
    path('main/',main,name='main'),
    path('cart/',cart,name='cart'),
    path('checkout/',checkout,name='checkout'),
    path('update_item/',updateItem,name='updateItem'),
    path('process_order/', processOrder,name='processOrder'),

    path('user_profile/',customerProfile,name='customerProfile'),
    path('restaurantOwnerProfile/',restaurantOwnerProfile,name='restaurantOwnerProfile'),
    path('personal_update/',customerInfoUpdate,name='customerInfoUpdate'),
    path('cancel_order/',customerOrderCancel,name='customerOrderCancel'),
    path('deleteRestaurantProduct/',deleteRestaurantProduct,name='deleteRestaurantProduct'),
    path('updateRestaurantProduct',updateRestaurantProduct, name='updateRestaurantProduct'),

    path('addRestaurantProduct',addRestaurantProduct,name='addRestaurantProduct'),
    path('updateRestaurantOrder/',updateRestaurantOrder,name='updateRestaurantOrder'),

    path('detailedProductView/',detailedProductView,name='detailedProductView'),
    path('addProductReview',addProductReview,name='addProductReview'),


    path('contactus',contactus,name='contactus'),

    path('category_based_display_items',category_based_display_items,name='category_based_display_items'),
    
    path('admin/', admin.site.urls),

]

urlpatterns+= static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
