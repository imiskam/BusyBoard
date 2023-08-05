"""
URL configuration for busyboard_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    # globals
    path('admin/', admin.site.urls),
    path('captcha/', include('captcha.urls')),

    # landing page
    path('', views.landing, name='home'),
    path('contact_us', views.contact_us, name='contact_us'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('sign_in/', views.sign_in, name='sign_in'),
    path('reset_password/',
         auth_views.PasswordResetView.as_view(template_name='busyboard_landing/password_reset_form.html'),
         name='reset_password'),
    path('reset_password_sent/',
         auth_views.PasswordResetDoneView.as_view(template_name='busyboard_landing/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='busyboard_landing/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset_password_complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='busyboard_landing/password_reset_complete.html'),
         name='password_reset_complete'),

    # main app
    path('settings/', views.settings, name='settings'),
    path('my_boards/', views.my_boards, name='my_boards'),
    path('my_boards/create/', views.create_board, name='create_board'),
    path('edit_board/<int:board_id>/', views.edit_board, name='edit_board'),
    path('save_board_changes/<int:board_id>/', views.save_board_changes, name='save_board_changes'),
    path('my_boards/<slug:slug>/', views.board_details, name='board_details'),
    path('my_boards/<slug:slug>/invite/', views.invite_to_board, name='invite_to_board'),
    path('my_boards/<slug:slug>/leave/', views.leave_board, name='leave_board'),
    path('my_boards/<slug:slug>/remove_user/', views.remove_user_from_board, name='remove_user_from_board'),
    path('delete_board/<int:board_id>/', views.delete_board, name='delete_board'),
    path('create_card/', views.create_card, name='create_card'),
    path('update_card_status/', views.update_card_status, name='update_card_status'),
    path('get_card_details/<int:card_id>/', views.get_card_details, name='get_card_details'),
    path('edit_card/<int:card_id>/', views.edit_card, name='edit_card'),
    path('save_card_changes/<int:card_id>/', views.save_card_changes, name='save_card_changes'),
    path('delete_card/<int:card_id>/', views.delete_card, name='delete_card'),
    path('export_board/<int:board_id>/', views.export_board_to_json, name='export_board_to_json'),
    path('sign_out/', views.sign_out, name='sign_out'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
