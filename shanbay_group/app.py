# -*- coding:utf-8 -*-
from flask import Flask
from flask import jsonify
from flask import render_template
from flask import send_from_directory
from flask import redirect
from flask import url_for
from flask import request
from shanbay import shanbay
from update import update
import json
import os
import webbrowser
import time
from update import version

app = Flask(__name__)

shan = shanbay()

@app.route('/')
def home():
	return render_template('login.html')

@app.route('/login', methods = ['POST'])
def login():
	if request.method == 'POST':
		logindata = request.form.to_dict()
		if 'captcha' not in logindata:
			s = shan.__login_default__(logindata['account'], logindata['password'])
		else:
			s = shan.__login__(logindata['captcha'])
		if s == '验证码错误':
			return jsonify(shan.__get_captcha__())
		elif s == 'SUCCESS':
			shan.log_status = True
			return jsonify({'status': 'SUCCESS'})
		else:
			return jsonify({'status': s})

@app.route('/index')
def index():
	if shan.log_status == True:
		table_content = table_generator(shan.database)
		return render_template("index.html", table_content = table_content)
	else:
		return render_template('login.html')

@app.route('/data/check_maxpage')
def maxpage():
	if shan.log_status == True:
		shan.database.clear()
		return str(shan.check())

@app.route('/data/<page>')
def each_page(page):
	time.sleep(2)
	current_page_list = shan.__parser__(page)
	return jsonify({'page': page, 
					'content': table_generator(current_page_list)})

@app.route('/sort/<method>')
def sort(method):
	attr, rev = method.split('-')
	if rev == 'up':
		rev = False
	else:
		rev = True
	shan.database.sort(key = lambda x: getattr(x, attr), reverse = rev)
	table_content = table_generator(shan.database)
	return render_template("index.html", table_content = table_content)

@app.route('/kick_out')
def kick_out():
	return jsonify({'data': list(set([i.realname for i in shan.database if i.status == '未打卡' and i.days < 30]))})
	
def table_generator(member_list):
	html = ''
	url = ['https://www.shanbay.com/team/manage/?page=', '#p1']
	for i in member_list:
		if (i.status == '未打卡' and i.days < 30) :
			html += '<tr class="danger"><td>' + '</td><td>'.join(['<a href="'+str(i.realname).join(url)+'" target="_blank">'+i.user+'</a>', 
			str(i.points), 
			str(i.days), 
			str(i.checkin_rate), 
			i.status, 
			str(i.average_point)]) + '</td></tr>'
		elif i.checkin_rate < 98.5:
			html += '<tr class="warning"><td>' + '</td><td>'.join(['<a href="'+str(i.realname).join(url)+'" target="_blank">'+i.user+'</a>', 
			str(i.points), 
			str(i.days), 
			str(i.checkin_rate), 
			i.status, 
			str(i.average_point)]) + '</td></tr>'
		else:
			html += '<tr><td>' + '</td><td>'.join(['<a href="'+str(i.realname).join(url)+'" target="_blank">'+i.user+'</a>', 
				str(i.points), 
				str(i.days), 
				str(i.checkin_rate), 
				i.status, 
				str(i.average_point)]) + '</td></tr>'
	return html

@app.context_processor
def override_url_for():
	return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
	if endpoint == 'static':
		filename = values.get('filename', None)
		if filename:
			file_path = os.path.join(app.root_path,
									 endpoint, filename)
			values['q'] = int(os.stat(file_path).st_mtime)
	return url_for(endpoint, **values)

if __name__ == '__main__':
	print('当前版本:', version)
	webbrowser.open('http://localhost:5000/')
	app.run()
