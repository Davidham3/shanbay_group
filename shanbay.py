# -*- coding:utf-8 -*-
import requests
import re
import json
from bs4 import BeautifulSoup
from collections import deque
import threading
import time

headers = {
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
	'Cache-Control': 'max-age=0',
	'Connection': 'keep-alive',
	'Host': 'www.shanbay.com',
	'Origin': 'https://www.shanbay.com',
	'Referer': 'https://www.shanbay.com/accounts/login/',
	'Upgrade-Insecure-Requests': '1',
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
}

class member:
	def __init__(self, user, points, days, checkin_rate, status, average_point, realname):
		(self.user, self.points, self.days, 
		 self.checkin_rate, self.status, self.average_point, self.realname) = (user, points, days, 
		 checkin_rate, status, average_point, realname)

class shanbay:
	def __init__(self):
		self.site = 'https://www.shanbay.com'
		self.s = requests.Session()
		r = self.s.get('https://www.shanbay.com/accounts/login/', headers = headers)
		data = {"referrer": "https://www.shanbay.com/",
				"page_path": "/web/account/login/",
				"params": ""}
		r = self.s.post('https://www.shanbay.com/api/v2/blink/analytics/pageview/', headers = headers, data = data)
		self.database = []
		self.unchecked = 0
		self.log_status = False

	def __login_default__(self, account, password):
		self.account = account
		self.password = password
		data = {}
		data['username'] = self.account
		data['password'] = self.password
		r = self.s.put('https://www.shanbay.com/api/v1/account/login/web/', headers = headers, data = data)
		print(r.text)
		self.s.get('https://www.shanbay.com/', headers = headers)
		return json.loads(r.text)['msg']

	def __get_captcha__(self):
		r = self.s.get('https://www.shanbay.com/api/v1/account/captcha/', headers = headers)
		dict1 = json.loads(r.text)
		if dict1['msg'] == 'SUCCESS':
			image_url = dict1['data']['image_url']
			self.key = dict1['data']['key']
		return {'status': 'captcha_needed',
				'image_url': image_url, 
				'account': self.account,
				'password': self.password}

	def __login__(self, captcha):
		data = {}
		data['key'] = self.key
		data['username'] = self.account
		data['password'] = self.password
		r = self.s.put('https://www.shanbay.com/api/v1/account/login/web/', headers = headers, data = data)
		print(r.text)
		self.s.get('https://www.shanbay.com/', headers = headers)
		return json.loads(r.text)['msg']

	def __logout__(self):
		self.s.get('https://www.shanbay.com/accounts/logout/', headers = headers)

	def check(self):
		'''return the maxpage number'''
		self.unchecked = 0
		#r = self.s.get('https://www.shanbay.com/team/members/?page=1#p1')
		r = self.s.get('https://www.shanbay.com/team/manage/#p1', headers = headers)
		soup = BeautifulSoup(r.text, 'lxml')
		maxpage = max([int(i.text) for i in soup.find_all('a', class_ = "endless_page_link", text = re.compile("\d+"))])
		print('maxpage:', maxpage)
		return maxpage

	def __parser__(self, page):
		'''parse each page'''
		url = 'https://www.shanbay.com/team/manage/?page=' + str(page) + '#p1'
		t = time.time()
		current_page_list = []
		member_page = self.s.get(url, headers = headers)
		soup = BeautifulSoup(member_page.text, 'lxml')
		for i in soup.find_all('tr', class_ = re.compile("member")):
			status = i.find_all('td', class_ = re.compile('checked'))[1].text.strip()
			if status == '未打卡':
				self.unchecked += 1
			user = i.find('td', class_ = 'user').find('a', class_ = 'nickname').text
			points = int(i.find('td', class_ = 'points').text)
			days = int(i.find('td', class_ = 'days').text.split(' ')[0])
			rate = float(i.find('td', class_ = 'rate').text.strip()[:-1])
			if days > 0:
				average_point = round(points/days, 2)
			else:
				average_point = 0
			newmember = member(user, points, days, rate, status, average_point, page)
			self.database.append(newmember)
			current_page_list.append(newmember)
		print(time.time()-t)
		return current_page_list

	def show_members_info(self, key, reverse):
		'''sort by parameter key
		   reture [i.user, i.points, i.days, i.checkin_rate, i.status, i.average_point, i.realname]
		'''
		list1 = [[i.user, i.points, i.days, 
		i.checkin_rate, i.status, i.average_point, i.realname] for i in self.database]
		list1.sort(key = key, reverse = reverse)
		return list1

	def send_mail(self, recipient, subject, body):
		data = {
			'recipient': recipient,
			'subject': subject,
			'body': body
		}
		r = self.s.post('https://www.shanbay.com/api/v1/message/', data = data, headers = headers)
		dict1 = json.loads(r.text)
		#print(dict1)
		if dict1['msg'] == 'SUCCESS':
			return 1
		else:
			return 0

	def group_send_mail(self, memberlist, subject, body):
		newbody = body
		faillist = []
		count = 1
		for i in memberlist:
			print(count)
			count += 1
			newbody = body.replace('{{name}}', i[1]).replace('{{days}}', str(i[2]))
			if not self.send_mail(i[0], subject, newbody):
				faillist.append(i[0])
			else:
				print(i[0])
				with open('C:/Users/song1/Desktop/sendlist.txt','a') as f:
					f.write(i[0] + '\n')
		if len(faillist):
			print(faillist)
			print(len(faillist))
		else:
			print('全部发送完毕！')

	def myteam(self):
		r = self.s.get('https://www.shanbay.com/home/', headers = headers)
		soup = BeautifulSoup(r.text, 'lxml')
		my_team_url = soup.find('a', text = re.compile("我的小组")).get('href')
		r = self.s.get(self.site + my_team_url, headers = headers)
		soup = BeautifulSoup(r.text, 'lxml')
		team_icon = soup.find('div', class_ = 'team-emblem span').find('img').get('src')
		x = soup.find('div', class_ = 'team-stat')
		rank = x.find('div', 'stat rank').find('h2').text.strip()
		rate = x.find('div', 'stat rate').find('h2').text.strip()
		member_num = x.find('div', 'stat size').find('h2').text.strip()
		return team_icon, rank, rate, member_num

if __name__ == '__main__':
	a = shanbay()
	s = a.__login_default__('Davidham3', 'Davidham3')
	if s == 'SUCCESS':
		print(a.check())
		x = a.__parser__(1)
		print(len(x))
		print(x)
	else:
		print(s)