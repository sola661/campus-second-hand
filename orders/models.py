from django.db import models
from django.contrib.auth.models import User #导入django自带的用户表模型；
# from goods.models import Goods

class Orders(models.Model):
    order_sn = models.CharField(max_length=50,unique=True,verbose_name='订单编号')
    price = models.DecimalField(max_digits=8,decimal_places=2,verbose_name='订单金额')
    status = models.CharField(max_length=20,choices=(('pending','待付款'),('paid','已付款'),('success','交易成功'),('cancelled','已取消订单')),default='pending',verbose_name='订单状态')
    create_time = models.DateTimeField(auto_now_add=True,verbose_name='创建时间',db_index=True)
    goods = models.ForeignKey(to='goods.Goods',on_delete=models.CASCADE,verbose_name='下单商品')
    user = models.ForeignKey(to='auth.User',on_delete=models.CASCADE,verbose_name='下单用户')

    class Meta:
        db_table='orders'
        verbose_name='订单'
        verbose_name_plural = '订单'



