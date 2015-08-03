 # -*- coding: utf-8 -*-
from django import forms


PIC_TYPE = (
	('superstar','明星'),
	('food','美食'),
	('cartoon','动漫'),
	('travel','旅游'),
	('photography','摄影'),
	('design','设计'),
	('funny','搞笑'),
	('car','汽车')
	)

class UploadForm(forms.Form):
	pic_title = forms.CharField(max_length=255)
	pic_type = forms.CharField(max_length=11,widget=forms.Select(choices=PIC_TYPE))
	pic_tab = forms.CharField(max_length=255)
	pic_file_path = forms.ImageField()
	pic_describe =  forms.CharField(widget=forms.Textarea)

class EditPicForm(forms.Form):
	pic_title = forms.CharField(max_length=255)
	pic_type = forms.CharField(max_length=11,widget=forms.Select(choices=PIC_TYPE))
	pic_tab = forms.CharField(max_length=255)