from django.urls import path
from . import views
app_name = 'goods'
urlpatterns = [
    path('category/list/',views.category_list,name='category_list'),
    path('goods/list/',views.goods_list,name='goods_list'),
    path('goods/',views.goods,name='goods'),
    path('publish/',views.publish,name='publish'),
    path('category/<int:good_id>/', views.category, name='category'),
    path('deactivate/<int:good_id>/', views.deactivate, name='deactivate'),
    path('image/<int:good_id>/', views.serve_image, name='serve_image'),
]