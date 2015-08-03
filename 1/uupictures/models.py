from django.db import models

class Users(models.Model):
	user_email = models.EmailField()
	user_password = models.CharField(max_length=255)
	user_name = models.CharField(max_length=255)
	user_client_ip = models.IPAddressField()
	user_login_time = models.DateTimeField(auto_now=True)
	user_register_time = models.DateTimeField(auto_now_add=True)
	user_rank = models.IntegerField()
	user_head_src = models.CharField(max_length=255,default="/media/1.png")

class Pictures(models.Model):
	pic_title = models.CharField(max_length=255)
	pic_type = models.CharField(max_length=100)
	pic_hot = models.IntegerField(default=0)
	pic_tab = models.CharField(max_length=255)
	pic_describe = models.TextField()
	pic_src = models.CharField(max_length=255)
	pic_add_time = models.DateTimeField(auto_now_add=True)
	users = models.ForeignKey(Users)

class Comments(models.Model):
	comm_pic = models.ForeignKey(Pictures)
	comm_user = models.ForeignKey(Users)
	comm_parent = models.IntegerField(default=0)
	comm_owner = models.IntegerField(default=0)
	comm_content = models.TextField()
	comm_like = models.IntegerField(default=0)
	comm_add_time = models.DateTimeField(auto_now_add = True)
	comm_edit_time = models.DateTimeField(auto_now = True)
	comm_islook = models.IntegerField(default=0)
	comm_islike = models.IntegerField(default=0)

	class Meta:
		ordering = ['comm_add_time']