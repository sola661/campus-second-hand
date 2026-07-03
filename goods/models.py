from django.db import models
from django.contrib.auth.models import User #导入django自带的用户表模型；

class Goods(models.Model):
    title = models.CharField(max_length=100,verbose_name='商品标题') #商品标题；
    description = models.TextField(verbose_name='商品描述') #商品描述；
    image = models.ImageField(upload_to='goods/',verbose_name='商品图片',null=True,blank=True)#null和blank的作用是用户可以先发布商品，之后再补传图片
    price = models.DecimalField(max_digits=8, decimal_places=2,default=0.00,verbose_name='商品价格')
    create_time = models.DateTimeField(auto_now_add=True,verbose_name='上架时间') #记录商品上架时间；
    is_active = models.BooleanField(default=True,verbose_name='是否上架')  #商品是否上架,默认已经上架；
    category = models.ForeignKey(to='Category',on_delete=models.CASCADE,null=True,blank=True)
    user = models.ForeignKey(to='auth.User',on_delete=models.CASCADE) #关联的是用户表；to后面必须是'auth.User'

    class Meta:
        db_table = 'goods'
        verbose_name = '商品'
        verbose_name_plural = '商品'

class Category(models.Model):
    name = models.CharField(max_length=50,verbose_name='分类名称',unique=True)
    desc = models.CharField(max_length=100,verbose_name='分类描述',null=True,blank=True)
    create_time = models.DateTimeField(auto_now_add=True,verbose_name='上架时间')

    class Meta:
        db_table = 'category'
        verbose_name = '商品分类'
        verbose_name_plural = '商品分类'