import json 
import sys 
import urllib
import urllib2
import redis
import socket
from WeiboLogin import Login
import re
import xml.etree.ElementTree as ET
import time
class WeiboUser(object):
    'Weibo User class, attribute:uid,name,follow[],fans[],friends[],href(link_href),fans_sum,follow_sum,msg_sum'
    #User object constructor: uid, name, href are aquired
    def __init__(self,_uniqueid, _displayname, _href, follow = 0, fan = 0, msg = 0, sex = '', dir_txt =''):
        self.uid = _uniqueid
        self.name = _displayname
        self.follow = []
        self.fans = []
        self.friends = set([])
        self.fans_follow = []
        self.href = _href
        self.fans_sum = fan
        self.follow_sum = follow
        self.msg_sum = msg
        self.sex = sex
        self.dir_txt = dir_txt


    #print weibo_usr information
    def print_info(self):
        print self.uid, self.name, self.href, self.follow_sum, self.fans_sum, self.msg_sum, self.sex, self.dir_txt

    def turn_json(self):
        ret = {
                "uid": self.uid,
                "name": unicode(self.name,'utf-8'),
                "href": self.href,
                "follow_sum": self.follow_sum,
                "fans_sum" : self.fans_sum,
                "msg_sum" : self.msg_sum,
                "sex" : self.sex,
                "dir_txt" : unicode(self.dir_txt,'utf-8')
                }
        return ret
    #visit url, which used in other method in the WeiboUser class
    def visit_url(self,url):
        socket.setdefaulttimeout(10)
        print 'Visiting... %s' % url
        try:
            follow_data = urllib2.urlopen(url).read()
            type = sys.getfilesystemencoding()
            try:
                follow_data = follow_data.decode('utf-8').encode(type)
            except Exception, e:
                print 'decode failed!'
        except Exception, e:
            print 'Visiting url failed! Error %s' % e
            print 'Visiting... %s' % url
            follow_data = self.visit_url(url)
        return follow_data

    def get_self_fans_follow(self):
        self.fans_follow = []
        url = 'http://weibo.com/'+self.uid+'/follow?relate=fans_follow'
        follow_data = self.visit_url(url)
        pt = re.compile('<a [^>]* usercard=.?"id=([^>]*?).?" href=.?"([^>]*?).?" class=.?"W_f14 S_func1.?"[^>]+>([^<]*)<.?/a>')
        pt2 = re.compile('<div class=.?"connect.?">[^<]+<a [^>]+>([^<]*)<.?/a>[^<]+<i[^>]+>\|<.?/i>[^<]+<a [^>]+>([^<]*)<.?/a>[^<]+<i[^>]+>\|<.?/i>[^<]+<a [^>]+>([^<]*)<.?/a>[^<]+<.?/div>')
        usrlist = pt.findall(follow_data)
        infolist = pt2.findall(follow_data)
        #pt = re.compile('<a class=.?"W_f14 S_func1.?" [^>]* href=.?"([^>]*?).?" usercard=.?"id=([^>]*?).?" target="_blank">([^<]*)<.?/a>')
        #pt2 = re.compile('<div class=.?"connect.?">[^<]+<a [^>]+>([^<]*)<.?/a><i[^>]+>\|<.?/i>[^<]+<a [^>]+>([^<]*)<.?/a><i[^>]+>\|<.?/i>[^<]+<a [^>]+>([^<]*)<.?/a><.?/div>')
        #usrlist = pt.findall(follow_data)
        #infolist = pt2.findall(follow_data)
        num = len(usrlist)
        for i in range(num):
            tuser = WeiboUser(usrlist[i][0],usrlist[i][2],usrlist[i][1],infolist[i][0],infolist[i][1],infolist[i][2])
            self.fans_follow.append(tuser)



    #get all the fans of login user, the result is stored in self.fans[], uid must be initialized
    def get_self_fans(self):
        self.fans = []
        url = 'http://weibo.com/'+self.uid+'/fans'
        follow_data = self.visit_url(url)
        #print follow_data
        #get the first page of fans
        pt = re.compile('<a [^>]* usercard=.?"id=([^>]*?).?" title=.?"([^>]*?).?"[^>]*href=.?"([^>]*?).?" class=.?"W_f14 S_func1.?">')
        pt2 = re.compile('<div class=.?"connect.?">[^<]+<a [^>]+>([^<]*)<.?/a><i[^>]+>\|<.?/i>[^<]+<a [^>]+>([^<]*)<.?/a><i[^>]+>\|<.?/i>[^<]+<a [^>]+>([^<]*)<.?/a><.?/div>')
        usrlist = pt.findall(follow_data)
        infolist = pt2.findall(follow_data)
        num = len(usrlist)
        for i in range(num):
            tusr = WeiboUser(usrlist[i][0], usrlist[i][1], usrlist[i][2].replace('\\',''), infolist[i][0], infolist[i][1], infolist[i][2]) 
            self.fans.append(tusr)
        pt = re.compile('<a[^>]*href=.?"([^>]*?).?"[^>]*class=.?"page S_bg1.?"[^>]*>([^>]*)<.?/a>')
        sub_url_list = pt.findall(follow_data)
        #print sub_url_list
        page = 2
        #maxpage = int(sub_url_list[len(sub_url_list)-1][1])
        #print maxpage
        ssub_url = sub_url_list[0][0][:-1].replace('\\','')
        while True:
            sub_url = 'http://weibo.com'+ssub_url+str(page)
            page += 1
            #print sub_url
            follow_data = self.visit_url(sub_url)
        #	follow_data = urllib2.urlopen(sub_url).read()
            pt = re.compile('<a [^>]* usercard=.?"id=([^>]*?).?" title=.?"([^>]*?).?"[^>]*href=.?"([^>]*?).?" class=.?"W_f14 S_func1.?">')
            pt2 = re.compile('<div class=.?"connect.?">[^<]+<a [^>]+>([^<]*)<.?/a><i[^>]+>\|<.?/i>[^<]+<a [^>]+>([^<]*)<.?/a><i[^>]+>\|<.?/i>[^<]+<a [^>]+>([^<]*)<.?/a><.?/div>')
            usrlist = pt.findall(follow_data)
            infolist = pt2.findall(follow_data)
            num = len(usrlist)
            if num == 0:
                break
            for i in range(num):
                tusr = WeiboUser(usrlist[i][0], usrlist[i][1], usrlist[i][2].replace('\\',''), infolist[i][0], infolist[i][1], infolist[i][2]) 
                self.fans.append(tusr)
        self.fans_sum = len(self.fans)

    #get all the fans of user who is not the login user, the result is stored in self.fans[], uid must be initialized 
    def get_other_fans(self):
        self.fan = []
        self.get_other_content('/fans')

    #get all the follow of user who is not the login user, the result is stored in self.fans[], uid must be initialized 
    def get_other_follow(self):
        self.follow = []
        self.get_other_content('/follow')

    #get the corresponding content (fans or follow) based on the argument 'content'
    def get_other_content(self,content):
        url = 'http://weibo.com/'+self.uid+content
        follow_data = self.visit_url(url)
#		print follow_data
        self.get_info_action(follow_data)
        #get the first page of fans
        pt = re.compile('<a [^>]* usercard=.?"id=([^>]*?).?" href=.?"([^>]*?).?" class=.?"W_f14 S_func1.?" >([^<]*)<.?/a>')
        pt2 = re.compile('<div class=.?"connect.?">[^<]+<a[^>]+>([^<]*)<.?/a>[^<]+<i[^>]+>\|<.?/i>[^<]+<a[^>]+>([^<]*)<.?/a>[^<]+<i[^>]+>\|<.?/i>[^<]+<a[^>]+>([^<]*)<.?/a>')
        usrlist = pt.findall(follow_data)
        infolist = pt2.findall(follow_data)
        num = len(usrlist)
        for i in range(num):
            tusr = WeiboUser(usrlist[i][0], usrlist[i][2], usrlist[i][1].replace('\\',''), infolist[i][0], infolist[i][1], infolist[i][2]) 
            if content == '/fans' :
                self.fans.append(tusr)
            else:
                self.follow.append(tusr)
        pt = re.compile('<a[^>]*class=.?"page S_bg1.?"[^>]*href=.?"([^>]*?).?">([^>]*)<.?/a>')
        sub_url_list = pt.findall(follow_data)
        if len(sub_url_list) == 0:
            if content == '/fans':
                self.fans_sum = len(self.fans)
            else:
                self.follow_sum = len(self.follow)
            return
        maxpage = int(sub_url_list[len(sub_url_list)-1][1])
        ssub_url = sub_url_list[0][0][:-1].replace('\\','')
        page = 2
        while True:
            sub_url = url + '?page='+str(page)
            print sub_url
            follow_data = self.visit_url(sub_url)
            pt = re.compile('<a [^>]* usercard=.?"id=([^>]*?).?" href=.?"([^>]*?).?" class=.?"W_f14 S_func1.?" >([^<]*)<.?/a>')
            pt2 = re.compile('<div class=.?"connect.?">[^<]+<a[^>]+>([^<]*)<.?/a>[^<]+<i[^>]+>\|<.?/i>[^<]+<a[^>]+>([^<]*)<.?/a>[^<]+<i[^>]+>\|<.?/i>[^<]+<a[^>]+>([^<]*)<.?/a>')
            usrlist = pt.findall(follow_data)
            infolist = pt2.findall(follow_data)
            num = len(usrlist)
            if num == 0:
                break
            for i in range(num):
                tusr = WeiboUser(usrlist[i][0], usrlist[i][2], usrlist[i][1].replace('\\',''), infolist[i][0], infolist[i][1], infolist[i][2]) 
                if content == '/fans' :
                    self.fans.append(tusr)
                else:
                    self.follow.append(tusr)
            if content == '/follow' and page == maxpage:
                break
            page += 1
            if page > 10 :
                break
        if content == '/fans':
            self.fans_sum = len(self.fans)
        else:
            self.follow_sum = len(self.follow)

    #get all the follow of login user, the result is stored in self.follow[]
    def get_self_follow(self):
        self.follow = []
        url = 'http://weibo.com/'+self.uid+'/follow'
        follow_data = self.visit_url(url)
        #follow_data = urllib2.urlopen(url).read()
        pt = re.compile('<a [^>]* class=.?"S_func1.?" [^>]*>')
        #get the first page of fans
        usrlist = pt.findall(follow_data)
        #get the first page of follow
        for usr in usrlist:
            pt = re.compile('href=.?"(.*?).?" title=.?"(.*?).?" usercard=.?"id=(.*?).?"')
            content = pt.search(usr).groups()
            tusr = WeiboUser(content[2], content[1], content[0].replace('\\',''))
            self.follow.append(tusr)
        pt = re.compile('<a[^>]*class=.?"page S_bg1.?"[^>]*href=.?"([^>]*?).?">([^>]*)<.?/a>')
        sub_url_list = pt.findall(follow_data)
        #print sub_url_list
        page = 2
        maxpage = int(sub_url_list[len(sub_url_list)-1][1])
        #print maxpage
        ssub_url = sub_url_list[0][0][:-1].replace('\\','')
        while True:
            sub_url = ssub_url+str(page)
            follow_data = self.visit_url(sub_url)
            #follow_data = urllib2.urlopen(sub_url).read()
            pt = re.compile('<a [^>]* class=.?"S_func1.?" [^>]*>')
            usrlist = pt.findall(follow_data)
            for usr in usrlist:
                pt = re.compile('href=.?"(.*?).?" title=.?"(.*?).?" usercard=.?"id=(.*?).?"')
                content = pt.search(usr).groups()
                tusr = WeiboUser(content[2], content[1], content[0].replace('\\',''))
                self.follow.append(tusr)
            if page == maxpage:
                break
            page += 1
        self.follow_sum = len(self.follow)

    #get user friends, the result is stored in friends[]
    def get_friends(self,uidlist,r):
        flag = 0
        for uid in uidlist:
            uidstr = uid + "fdset"
            uid_fdset = r.smembers(uidstr)
            if flag == 0:
                self.friends = uid_fdset
                flag = 1
            else:
                self.friends = self.friends.intersection(uid_fdset)
    def get_friends_by_web_stable(self, uidlist):
        stable_friend_list = set([])
        self.get_friends_by_web(uidlist)
        len1 = len(self.friends)
        for uid in self.friends:
            stable_friend_list.add(uid)
        print len1
        s = 0
        while True:
            self.get_friends_by_web(uidlist)
            print len1, len(self.friends)
            if len1 == len(self.friends):
                return
            elif len1 > len(self.friends):
                self.friends = stable_friend_list
            else:
                len1 = len(self.friends)
                stable_friend_list.clear()
                for uid in self.friends:
                    stable_friend_list.add(uid)
            s += 1
            if s > 5:
                return



    def get_friends_by_web(self, uidlist):
        self.friends = set([])
        uidlist_str = ''
        flag = 0
        for uid in uidlist:
            if flag == 0:
                flag = 1
            else:
                uidlist_str += ','
            uidlist_str += uid
        base_url = 'http://s.weibo.com/friend/common?uids='+uidlist_str+'&type=com'
        follow_data = self.visit_url(base_url)
        pt = re.compile('<p class=.?"add_name.?"><a [^>]* href=.?"([^>]*?).?" title=.?"([^>]*?).?" usercard=.?"id=([^>]*?).?" [^>]*>')
        usrlist = pt.findall(follow_data)
        list_len = len(usrlist)
        for i in range(list_len):
            self.friends.add(usrlist[i][2])
        page = 2
        while True:
            url = base_url + "&page=" + str(page)
            follow_data = self.visit_url(url)
            pt = re.compile('<p class=.?"add_name.?"><a [^>]* href=.?"([^>]*?).?" title=.?"([^>]*?).?" usercard=.?"id=([^>]*?).?" [^>]*>')
            usrlist = pt.findall(follow_data)
            list_len = len(usrlist)
            if list_len == 0 :
                break
            for i in range(list_len):
                self.friends.add(usrlist[i][2])
            page += 1
        #print 'Getting %s friends....' % self.name

    #the main code in getting the WeiboUser infomation
    def get_info_action(self):
        url = "http://weibo.com/"+str(self.uid)
        if self.uid == '6667040':
            url = "http://weibo.com/317906660"
        data = self.visit_url(url).replace('\\','')
        #print data
        pt = re.compile('<span class="name">(.*?)</span>')
        if pt.search(data)==None : 
            return
        self.name = pt.search(data).group(1)
        pt = re.compile('<a [^>]* class="pf_lin S_link1">(.*?)</a>')
        self.href = pt.search(data).group(1).replace('\\','')
        pt = re.compile('<strong node-type="fans">(.*?)</strong>')
        self.fans_sum = int(pt.search(data).group(1))
        pt = re.compile('<strong node-type="follow">(.*?)</strong>')
        self.follow_sum = int(pt.search(data).group(1))
        pt = re.compile('<strong node-type="weibo">(.*?)</strong>')
        self.msg_sum = int(pt.search(data).group(1))
        pt = re.compile('<em class="W_ico12 (.*?)" [^>]*></em>')
        self.sex = pt.search(data).group(1)
        pt = re.compile('<em class="S_txt2"><a [^>]* title="(.*?)">[^<]*</a></em>')
        self.dir_txt = pt.search(data).group(1)
        #pt = re.compile('')

    #get the infomation of WeiboUser 
    def get_user_info(self):
        url = 'http://weibo.com/'+self.uid
        follow_data = self.visit_url(url)
        self.get_info_action(follow_data)
        print self.fans_sum, self.follow_sum, self.fans_sum


if __name__ == '__main__':

    newlogin = Login('dujun881228@sohu.com','dujun881228')
    newlogin.set_cookie()
    datastream = newlogin.login_action()
    print datastream
    uid, usrid, name = newlogin.get_loginuser_info(datastream)
    #weibo_usr = WeiboUser(uid,name,'')
    uid1 = '1994416314'
    uid2 = '2142928827'

    uidlist = []
    uidlist.append(uid1)
    uidlist.append(uid2)
    weibo_usr = WeiboUser('', '', '')
    weibo_usr.get_friends_by_web(uidlist)
    print len(weibo_usr.friends)
    for uid in weibo_usr.friends :
        print uid
    weibo_usr = WeiboUser(uid1,'','')
    weibo_usr.get_info_action()
    weibo_usr.print_info()
    ss =  weibo_usr.turn_json()
    ss = str(ss).replace("u'","'")
    ss = ss.replace("'",'"')
    res = json.loads(ss)
    print res['uid'], res['name']

