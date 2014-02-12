import urllib
import urllib2
import cookielib
import rsa
import base64
import re
import json
import hashlib
import binascii
class Login(object):
	postdata = {
			'entry': 'weibo',
			'gateway': '1',
			'from': '',
			'savestate': '7',
			'userticket': '1',
			'ssosimplelogin': '1',
			'vsnf': '1',
			'vsnval': '',
			'su': '',
			'service': 'miniblog',
			'servertime': '',
			'nonce': '',
			'pwencode': 'wsse',
			'sp': '',
			'encoding': 'UTF-8',
			'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
			'returntype': 'META',
			'pubkey': '',
			'pcid': '',
			'rsakv': '',
			'exectime': '',
			'sinaSSOEncoder': '',
			'pwencode': 'rsa2'
			}
	
	def __init__(self,username,password):
		self.usrname = username
		self.passwd = password
		self.servertime = ''
		self.nonce = ''
		self.pcid = ''
		self.exectime = ''
		self.pubkey = ''
		self.rsakv = ''

	def __del__(self):
		print 'Login object deleted'
	
	def set_cookie(self):
		cookiejar = cookielib.LWPCookieJar()
		cookie_support = urllib2.HTTPCookieProcessor(cookiejar)
		opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
		urllib2.install_opener(opener)
	
	def get_servertime(self):
		url = 'http://login.sina.com.cn/sso/prelogin.php?entry=sso&callback=sinaSSOController.preloginCallBack&su=&client=ssologin.js(v.1.4.4)&rsakt=mod&_=1358327569490' 
		
		headers = {
				'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.52 Safari/537.17'
				}
		req = urllib2.Request(url=url,headers=headers)
		data = urllib2.urlopen(req).read()
		p = re.compile('\((.*)\)')
		try:
			json_data = p.search(data).group(1)
			data = json.loads(json_data)
			self.servertime = str(data['servertime'])
			self.nonce = data['nonce']
			self.pcid = data['pcid']
			self.pubkey = data['pubkey']
			self.rsakv = data['rsakv']
			self.exectime = data['exectime']
		except:
			print 'Get servertime error!'
	
	def get_pwd(self):
		rsaPublickey = int(self.pubkey,16)
		key = rsa.PublicKey(rsaPublickey,65537)
		message = str(self.servertime) + '\t' + str(self.nonce) + '\n' + str(self.passwd)
		self.passwd = rsa.encrypt(message,key)
		self.passwd = binascii.b2a_hex(self.passwd)
		return self.passwd

	def get_usrname(self):
		username_ = urllib.quote(self.usrname)
		username = base64.encodestring(username_)[:-1]
		self.usrname = username
		return username
	
	def login_action(self):
		url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.5)'
		try:
			self.get_servertime()
		except:
			return
		print self.servertime, self.nonce
		self.postdata['servertime'] = self.servertime
		self.postdata['nonce'] = self.nonce
		self.postdata['su'] = self.get_usrname()
		self.postdata['sp'] = self.get_pwd()
		self.postdata['pcid'] = self.pcid
		self.postdata['exectime'] = self.exectime
		self.postdata['rsakv'] = self.rsakv
		self.postdata = urllib.urlencode(self.postdata)
		headers = {
				'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.52 Safari/537.17'
				}
		req = urllib2.Request(url=url,data=self.postdata,headers=headers)
		result = urllib2.urlopen(req)
		text = result.read()
		p = re.compile('location\.replace\("(.*?)"\)')
		try:
			login_url = p.search(text).group(1)
			
			datastream=urllib2.urlopen(login_url).read()
			print 'Login success!!'
			return datastream
		except:
			print 'Login error!'
			return None
	
	def get_loginuser_info(self, datastream):
		pt = re.compile('feedBackUrlCallBack\((.*)\)')
		json_data = json.loads(pt.search(datastream).group(1))
		user_info = json_data['userinfo']
		return user_info['uniqueid'], user_info['userid'], user_info['displayname']

if __name__ == '__main__':
	new_login = Login('dujun881228@sohu.com','dujun881228')
	new_login.set_cookie()
	datastream = new_login.login_action()
	usrid,uid,name = new_login.get_loginuser_info(datastream)
	print usrid, uid, name
