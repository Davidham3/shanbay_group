# -*- coding:utf-8 -*-
import requests
import json
from bs4 import BeautifulSoup
import zipfile
import os
import shutil
import sys

headers = {
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
}
version = 1.52
class update:
	def __init__(self, version):
		self.version = version
		self.s = requests.Session()

	def check(self):
		data = {'account': 'Davidham3', 'password': 'Davidham/*-1995$'}
		r = self.s.post('http://tobethebest-dworkspace.rhcloud.com/', headers = headers, data = data)
		soup = BeautifulSoup(r.text, 'lxml')
		filelist = json.loads(soup.text)
		directory = 'http://tobethebest-dworkspace.rhcloud.com/static/main/'
		if 'version' not in filelist:
			return 0
		r = self.s.get(directory+'version', headers = headers)
		version = r.text.split('=')[1]
		if self.version < float(version):
			if self.download() == 1:
				print('更新完成!')
		else:
			print('当前为最新版本')

	def download(self):
		r = self.s.get('http://tobethebest-dworkspace.rhcloud.com/static/main/tobethebest.zip', headers = headers)
		with open('tobethebest.zip', 'wb') as f:
			f.write(r.content)
		print('下载完成，准备安装')
		sys.stdout.flush()
		return self.install()

	def install(self):
		z = zipfile.ZipFile('tobethebest.zip', 'r')
		os.mkdir('tobethebest2')
		print('正在抽取文件')
		sys.stdout.flush()
		for file in z.namelist():
		    z.extract(file, 'tobethebest2/')
		z.close()
		for i in os.listdir(os.path.split(os.path.realpath(__file__))[0]):
			try:
				shutil.rmtree('tobethebest/'+i)
			except:
				os.remove('tobethebest/'+i)
		for i in os.listdir('tobethebest2'):
			shutil.move('tobethebest2/'+i, 'tobethebest/'+i)
		os.rmdir('tobethebest2')
		os.remove('tobethebest.zip')
		return 1

if __name__ == '__main__':
	try:
		update(version).check()
	except:
		pass