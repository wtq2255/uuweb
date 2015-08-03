 # -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect,HttpResponse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.views.decorators.csrf import csrf_exempt

from uuweb.settings import STATIC_URL,MEDIA_URL,PAGE_SIZE
from models import Users,Pictures,Comments

from DjangoCaptcha import Captcha

import json,time,hashlib,os,random

#验证验证码
#GET方法获取验证码
#若正确返回 True; 若错误返回 False
def checkCaptcha(request):
	response = HttpResponse()
	_captcha = request.GET.get('captcha') or ''
	ca = Captcha(request)
	if ca.check(_captcha):
		callback = True
	else:
		callback = False
	response.write(json.dumps(callback))
	return response

#获取验证码
def captcha(request):
	ca =  Captcha(request)
	return ca.display()

#判断 session 中是否有'is_user'，返回 True 或 False
@csrf_exempt
def isUser(request):
	try:
		if ('is_user' in request.session) and (request.session['is_user'] == 1):
			is_user = True
		else:
			is_user = False
		return is_user
	except Exception:
		return HttpResponseRedirect('/')
	

#若session中有is_user，则将session中的is_user，user_name，user_id返回
def detailUser(request):
	is_user = isUser(request)
	if is_user:
		user_name = request.session['user_name']
		user_id = request.session['user_id']
	else:
		user_name = 0
		user_id = 0
	callback = {'is_user':is_user,'user_name':user_name,'user_id':user_id}
	return callback

#登录处理函数，
#若是POST方式提交，则对用户提交的消息和数据库验证，若存在用户则以JSON返回用户信息，若不存在则返回0
#若不是POST方式提交，则重定向到登录前的地址
@csrf_exempt
def login(request):
	login_from = request.META.get('HTTP_REFERER', '/')
	if request.method == "POST":
		response = HttpResponse()  
		response['Content-Type'] = "application/json"  
		email = request.POST.get('email','')
		password = get_md5_value(request.POST.get('password',''))
		remember = request.POST.get('remember','')
		try:
			user = Users.objects.get(user_email=email,user_password=password)
			user_id = user.id
			user_name = user.user_name
			user_client_ip = user.user_client_ip
			user_login_time = user.user_login_time.strftime('%Y-%m-%d %H:%M:%S')
		except Exception:
			user = 0
		if remember == '1':
			request.session.set_expiry(30*60*60*24)
		if user:
			try:
				Users(user_client_ip=request.META.get("REMOTE_ADDR",None))
			except Exception, e:
				raise e
			request.session['is_user'] = 1
			request.session['user_id'] = user_id
			request.session['user_email'] = email
			request.session['user_name'] = user_name
			request.session['user_client_ip'] = user_client_ip
			request.session['user_login_time'] = user_login_time
			data = [{'user_email':email,'user_name':user_name,'user_client_ip':user_client_ip,'user_login_time':user_login_time}]
			response.write(json.dumps(data))
		else:
			response.write(json.dumps(0))
		# print response
		return response
	else:
		if not login_from:
			login_from = "/"
		return HttpResponseRedirect(login_from)

#注册页面
@csrf_exempt
def register(request):
	if 'navstr' in request.session:
		navStr = request.session['navstr']
	else:
		navStr = 'home'
	return render_to_response("register.html", {'STATIC_URL': STATIC_URL, 'navStr': navStr, 'detailUser': detailUser(request)})

#注册提交处理函数
@csrf_exempt
def submit(request):
	if request.method == "POST":
		username = request.POST.get('username')
		email = request.POST.get('email')
		password = get_md5_value(request.POST.get('interPassword'))
		client_ip = request.META.get("REMOTE_ADDR",None)
		try:
			Users(user_name=username,user_email=email,user_password=password,user_client_ip=client_ip,user_rank=0).save()
			user = Users.objects.get(user_email=email)
			# print user.id
		except Exception, e:
			raise e
		request.session['is_user'] = 1
		request.session['user_id'] = user.id
		request.session['user_email'] = email
		request.session['user_name'] = username
		request.session['user_client_ip'] = client_ip
		request.session['user_login_time'] = user.user_login_time.strftime('%Y-%m-%d %H:%M:%S')
		return HttpResponseRedirect('/')
	else:
		return HttpResponseRedirect('/')

#验证用户注册的Email是否已经存在，若存在返回False，否则为True
@csrf_exempt
def emailUnique(request):
	if request.method == 'POST':
		response = HttpResponse()
		response['Content-Type'] = "application/json"
		email = request.POST.get('email')
		try:
			user = Users.objects.filter(user_email=email)
		except Exception:
			user = 0
		if user:
			callback = False
		else:
			callback = True
		response.write(json.dumps(callback))
		# print response
		return response
	else:
		return HttpResponseRedirect('/')

#注销用户请求，删除登录时存到session中的数据，并返回到请求注销用户的页面
def logout(request):
	logout_from = request.META.get('HTTP_REFERER', '/')
	try:
		del request.session['is_user']
		del request.session['user_email']
		del request.session['user_username']
		del request.session['user_client_ip']
		del request.session['user_login_time']
	except Exception:
		pass
	return HttpResponseRedirect(logout_from)

#若用户存在则返回“我的图库”页面
def myGallery(request,id,currentPage=1):
	if isUser(request):
		if 'navstr' in request.session:
			navStr = request.session['navstr']
		else:
			navStr = 'home'
		try:
			user = Users.objects.get(id=id)
			pics = user.pictures_set.all().order_by('-pic_add_time')
		except Exception:
			pics = 0
		return render_to_response("my_gallery.html", {'STATIC_URL': STATIC_URL, 'navStr': navStr, 'detailUser': detailUser(request), 'pics':dealPaginator(pics,currentPage)})

	else:
		return HttpResponseRedirect("/")

#用户修改图片处理方法
#该方法有两个形参，id是URL里传递的图片的id。
#它由POST方法请求，获取用户提交的 edit_pic_title、edit_pic_type、edit_pic_tab、edit_pic_edscribe 四个字符串，并将其保存在Pictures models中。
#保存完之后返回URL "/mygallery/id/"

#若没有 用户权限 或 不是POST请求，将返回网站根目录

@csrf_exempt
def userEditPic(request,id):
	if isUser(request):
		if request.method == "POST":
			edit_pic_title = request.POST.get('edit_pic_title','')
			edit_pic_type = request.POST.get('edit_pic_type','')
			edit_pic_tab = request.POST.get('edit_pic_tab_format','')
			edit_pic_describe = request.POST.get('edit_pic_describe','')
			try:
				picture = Pictures.objects.get(id=id)
				picture.pic_title = edit_pic_title
				picture.pic_type = edit_pic_type
				picture.pic_tab = edit_pic_tab
				picture.pic_describe = edit_pic_describe
				picture.save()
			except Exception, e:
				raise e
			return HttpResponseRedirect("/mygallery/" + str(picture.users.id) + "/")
		else:
			return HttpResponseRedirect("/")
	else:
		return HttpResponseRedirect("/")

@csrf_exempt
def delPic(request,id):
	if isUser(request):
		if request.method == "POST":
			try:
				pic_id = request.POST.get('del_pic_id','')
				pic = Pictures.objects.get(id=pic_id)
			except Exception, e:
				raise e
			if 'SERVER_SOFTWARE' in os.environ:
				try:
					from sae.storage import Bucket
					bucket = Bucket('media')
					pic_path = str(id) + '/' + pic.pic_src[pic.pic_src.rindex("/")+1:]
					bucket.delete_object(pic_path)
					pic.delete()
				except Exception, e:
					raise e
			else:
				try:
					os.remove(pic.pic_src[1:])
					# print pic.pic_src[1:pic.pic_src.rindex("/")+1]
					if not os.listdir(pic.pic_src[1:pic.pic_src.rindex("/")+1]):
						os.rmdir(pic.pic_src[1:pic.pic_src.rindex("/")+1])
					pic.delete()
				except Exception, e:
					raise e
			return HttpResponseRedirect("/mygallery/"+id+"/")
		else:
			return HttpResponseRedirect("/")
	else:
		return HttpResponseRedirect("/")

# 上传图片页面
def upload(request):
	if isUser(request):
		if request.method == "GET":
			return render_to_response("upload_pic.html",{'STATIC_URL': STATIC_URL,'detailUser':detailUser(request)})
	else:
		return HttpResponseRedirect("/")

# 上传图片提交页面
# 若用户使用sae提交，则将图片保存在Storage中‘media’doman下,路径为/media/用户ID/当前时间(格式为YYYYMMDDHHMMSS)_随机数(1－999999999).jpg
# 若用户在本地提交，则将图片保存在media文件夹下，路径为/media/用户ID/当前时间(格式为YYYYMMDDHHMMSS)_随机数(1－999999999).jpg
@csrf_exempt
def uploadPic(request, id):
	if isUser(request):
		if request.method == 'POST':
			response = HttpResponse()
			pic_title = request.POST.get("pic_title",'')
			pic_type = request.POST.get('pic_type','')
			pic_tab = request.POST.get('pic_tab_format','')
			pic_describe = request.POST.get('pic_describe','')
			pic_file = request.FILES['pic_file']
			pic_name = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time())) + '_' + str(random.randint(1,999999999)) + '.jpg'

			if 'SERVER_SOFTWARE' in os.environ:
				pic_path = str(id) + '/' + pic_name
				from sae.storage import Bucket
				bucket = Bucket('media')
				bucket.put_object(pic_path, pic_file)
				try:
					user = Users.objects.get(id=id)
					Pictures(pic_title=pic_title,pic_type=pic_type,pic_tab=pic_tab,pic_describe=pic_describe,pic_src=bucket.generate_url(pic_path),users=user).save()
				except Exception, e:
					response.write(False)
			else:
				path = MEDIA_URL + str(id) + '/'
				pic_path = path + pic_name
				if not os.path.exists(path[1:]):
					os.makedirs(path[1:])
				try:
					f = open(pic_path[1:],'ab')
					for chunk in pic_file.chunks():  
						f.write(chunk)  
					f.close()
					user = Users.objects.get(id=id)
					Pictures(pic_title=pic_title,pic_type=pic_type,pic_tab=pic_tab,pic_describe=pic_describe,pic_src=pic_path,users=user).save()
				except Exception, e:
					response.write(False)
			
			response.write(True)
			return response		
		else:
			return HttpResponseRedirect('/')
	else:
		return HttpResponseRedirect('/')

@csrf_exempt
def uploadPicForm(request):
	if isUser(request):
		if request.method == "POST":
			return render_to_response("upload_pic_form.html",{'detailUser':detailUser(request)})
		else:
			return HttpResponseRedirect('/')
	else:
		return HttpResponseRedirect

######## page view ###############

@csrf_exempt
def index(request):
	navStr = 'home'
	request.session['navstr'] = navStr
	try:
		hot_pics = Pictures.objects.order_by('-pic_hot')[0:3]
		superstar_pics = Pictures.objects.filter(pic_type="superstar").order_by('-pic_add_time')[0:4]
		food_pics = Pictures.objects.filter(pic_type="food").order_by('-pic_add_time')[0:4]
		cartoon_pics = Pictures.objects.filter(pic_type="cartoon").order_by('-pic_add_time')[0:4]
		travel_pics = Pictures.objects.filter(pic_type="travel").order_by('-pic_add_time')[0:4]
		photography_pics = Pictures.objects.filter(pic_type="photography").order_by('-pic_add_time')[0:4]
		design_pics = Pictures.objects.filter(pic_type="design").order_by('-pic_add_time')[0:4]
		funny_pics = Pictures.objects.filter(pic_type="funny").order_by('-pic_add_time')[0:4]
		car_pics = Pictures.objects.filter(pic_type="car").order_by('-pic_add_time')[0:4]
	except Exception:
		hot_pics = None
		superstar_pics = None
		food_pics = None
		cartoon_pics = None
		travel_pics = None
		photography_pics = None
		design_pics = None
		funny_pics = None
		car_pics = None
	return render_to_response("index.html", {'STATIC_URL': STATIC_URL, 'navStr': navStr, 'detailUser': detailUser(request), 'hot_pics':hot_pics, 'superstar_pics':superstar_pics, 'food_pics':food_pics, 'cartoon_pics':cartoon_pics, 'travel_pics':travel_pics, 'photography_pics':photography_pics, 'design_pics':design_pics, 'funny_pics':funny_pics, 'car_pics':car_pics})

@csrf_exempt
def superstar(request,currentPage=1):
	navStr = 'superstar'
	request.session['navstr'] = navStr
	try:
		superstar_pics = Pictures.objects.filter(pic_type="superstar").order_by('-pic_add_time')
	except Exception:
		superstar_pics = None
	return render_to_response("list.html", {'STATIC_URL': STATIC_URL, 'navStr': navStr, 'detailUser': detailUser(request), 'pics':dealPaginator(superstar_pics,currentPage)})

@csrf_exempt
def food(request,currentPage=1):
	navStr = 'food'
	request.session['navstr'] = navStr
	try:
		food_pics = Pictures.objects.filter(pic_type="food").order_by('-pic_add_time')
	except Exception:
		food_pics = None
	return render_to_response("list.html", {'STATIC_URL': STATIC_URL, 'navStr': navStr, 'detailUser': detailUser(request), 'pics':dealPaginator(food_pics,currentPage)})

@csrf_exempt
def cartoon(request,currentPage=1):
	navStr = 'cartoon'
	request.session['navstr'] = navStr
	try:
		cartoon_pics = Pictures.objects.filter(pic_type="cartoon").order_by('-pic_add_time')
	except Exception:
		cartoon_pics = None
	return render_to_response("list.html", {'STATIC_URL': STATIC_URL, 'navStr': navStr, 'detailUser': detailUser(request), 'pics':dealPaginator(cartoon_pics,currentPage)})

@csrf_exempt
def travel(request,currentPage=1):
	navStr = 'travel'
	request.session['navstr'] = navStr
	try:
		travel_pics = Pictures.objects.filter(pic_type="travel").order_by('-pic_add_time')
	except Exception:
		travel_pics = None
	return render_to_response("list.html", {'STATIC_URL': STATIC_URL, 'navStr': navStr, 'detailUser': detailUser(request), 'pics':dealPaginator(travel_pics,currentPage)})

@csrf_exempt
def photography(request,currentPage=1):
	navStr = 'photography'
	request.session['navstr'] = navStr
	try:
		photography_pics = Pictures.objects.filter(pic_type="photography").order_by('-pic_add_time')
	except Exception:
		photography_pics = None
	return render_to_response("list.html", {'STATIC_URL': STATIC_URL, 'navStr': navStr, 'detailUser': detailUser(request), 'pics':dealPaginator(photography_pics,currentPage)})

@csrf_exempt
def design(request,currentPage=1):
	navStr = 'design'
	request.session['navstr'] = navStr
	try:
		design_pics = Pictures.objects.filter(pic_type="design").order_by('-pic_add_time')
	except Exception:
		design_pics = None
	return render_to_response("list.html", {'STATIC_URL': STATIC_URL, 'navStr': navStr, 'detailUser': detailUser(request), 'pics':dealPaginator(design_pics,currentPage)})

@csrf_exempt
def funny(request,currentPage=1):
	navStr = 'funny'
	request.session['navstr'] = navStr
	try:
		funny_pics = Pictures.objects.filter(pic_type="funny").order_by('-pic_add_time')
	except Exception:
		funny_pics = None
	return render_to_response("list.html", {'STATIC_URL': STATIC_URL, 'navStr': navStr, 'detailUser': detailUser(request), 'pics':dealPaginator(funny_pics,currentPage)})

@csrf_exempt
def car(request,currentPage=1):
	navStr = 'car'
	request.session['navstr'] = navStr
	try:
		car_pics = Pictures.objects.filter(pic_type="car").order_by('-pic_add_time')
	except Exception:
		car_pics = None
	return render_to_response("list.html", {'STATIC_URL': STATIC_URL, 'navStr': navStr, 'detailUser': detailUser(request), 'pics':dealPaginator(car_pics,currentPage)})

@csrf_exempt
def detail(request, id):
	if 'navstr' in request.session:
		navStr = request.session['navstr']
	else:
		navStr = 'home'
	try:
		picture = Pictures.objects.get(id=id)
		user = picture.users
		# print user.user_name
		hot_id = "hot_"+id
		# print not(hot_id in request.session)
		# print request.session[hot_id] == id
		if not(hot_id in request.session):
			request.session[hot_id] = id
			request.session.set_expiry(30*60*60*3)
			picture.pic_hot = picture.pic_hot + 1
			picture.save()
		else:
			if (request.session[hot_id] != id):
				request.session[hot_id] = id
				request.session.set_expiry(30*60*60*3)
				picture.pic_hot = picture.pic_hot + 1
				picture.save()
		# print picture.pic_hot
		recommend_pic = Pictures.objects.filter(pic_type=picture.pic_type).order_by('-pic_hot')[0:1]
		# print recommend_pic[0].pic_title
	except Exception:
		picture = None
	return render_to_response("detail.html", {'MEDIA_URL':MEDIA_URL,'STATIC_URL': STATIC_URL, 'navStr': navStr, 'detailUser': detailUser(request), 'picture':picture,'user':user, 'recommend_pic':recommend_pic[0]})

@csrf_exempt
def commentsDisplay(request):
	if request.method == 'POST':
			response = HttpResponse()
			pid = request.POST.get('id','')
			try:
				picture = Pictures.objects.get(id=pid)
				comments = picture.comments_set.all()
			except Exception:
				comments = 0
			return render_to_response('comments.html',{'comments':comments,'MEDIA_URL':MEDIA_URL,'user':detailUser(request),'pid':pid})
	else:
		return HttpResponseRedirect('/')

@csrf_exempt
def comments(request, picId, userId):
	if request.method == "POST":
		response = HttpResponse()
		response['Content-Type'] = "application/json"
		if isUser(request):  
			comment_parent = request.POST.get('comm_parent','0')
			comment_owner = request.POST.get('comm_owner','0')
			comment_content = request.POST.get('comm_content','')
			print '================='
			print comment_parent
			print '-----------------'
			print comment_owner
			print '-----------------'
			print comment_content
			print '================='
			try:
				picture = Pictures.objects.get(id=picId)
				user = Users.objects.get(id=userId)
				comment = Comments(comm_pic=picture,comm_user=user,comm_content=comment_content).save()
			except Exception, e:
				print e
				callback = "False"
			callback = "True"
		else:
			callback = "noUser"
		response.write(json.dumps(callback))
		return response
	else:
		return HttpResponseRedirect("/")
@csrf_exempt
def commentsLike(request):
	if request.method == 'POST':
		response = HttpResponse()
		response['Content-Type'] = "application/json"
		if isUser(request):
			cid = request.POST.get('comment_like_id','')
			try:
				comment = Comments.objects.get(id=cid)
				print comment
				comment.comm_like += 1
				comment.comm_islike = 1
				callback = comment.comm_like
				comment.save()
				# callback = cid
			except Exception, e:
				raise e
				callback = "False"
			print "-------"
		else:
			callback = "noUser"
		response.write(json.dumps(callback))
		return response
	else:
		HttpResponseRedirect('/')

@csrf_exempt
def commentsUnlike(request):
	if request.method == 'POST':
		response = HttpResponse()
		response['Content-Type'] = "application/json"
		if isUser(request):
			cid = request.POST.get('comment_unlike_id','')
			try:
				comment = Comments.objects.get(id=cid)
				print comment
				comment.comm_like -= 1
				comment.comm_islike = 0
				callback = comment.comm_like
				comment.save()
				# callback = cid
			except Exception, e:
				raise e
				callback = "False"
			print "-------"
		else:
			callback = "noUser"
		response.write(json.dumps(callback))
		return response
	else:
		HttpResponseRedirect('/')

# 处理分页问题，传入 数据(django.db.models.query.QuerySet类型) 和 当前页(数字)
# 返回找到的当前页面的数据（django.core.paginator.Paginator类型）
def dealPaginator(pictures,currentPage):
	# print type(pictures)
	paginator = Paginator(pictures,PAGE_SIZE)
	# print type(paginator)
	try:
		p = int(currentPage)
		if p == 0:
			p = 1
	except Exception, e:
		p = 1
	try:
		pics = paginator.page(p)
	except (EmptyPage, InvalidPage):
		pics = paginator.page(paginator.num_pages)
	return pics


# deal md5 secrct
def get_md5_value(src):
	myMd5 = hashlib.md5()
	myMd5.update(src)
	myMd5_Digest = myMd5.hexdigest()
	return myMd5_Digest

