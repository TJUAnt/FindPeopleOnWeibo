import json 
import sys 
import redis
reload(sys)
sys.setdefaultencoding('utf-8')
import urllib
import urllib2
import socket
from WeiboLogin import Login
import re
import xml.etree.ElementTree as ET
import time
class WeiboUser(object):
    'Weibo User class, attribute:uid,name,follow[],fans[],friends[],href(link_href),fans_sum,follow_sum,msg_sum'
    #User object constructor: uid, name, href are aquired
    def __init__(self,_uniqueid, _displayname, _href,  follow = 0, fan = 0, msg = 0, sex = '', dir_txt ='', _long_id =
            None):
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
        self.msg_list = []
        self.zz_list = []
        self.page_sum = -1
        self.long_id = _long_id


    #print weibo_usr information
    def print_info(self):
        print self.uid, self.long_id, self.name, self.href, self.follow_sum, self.fans_sum, self.msg_sum, self.sex, self.dir_txt

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
        socket.setdefaulttimeout(100)
        print 'Visiting... %s' % url
        time.sleep(1)
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
        if follow_data.strip() == '':
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
            tmplen = len(self.friends)
            if abs(len1 - tmplen) * 10 < len1:
                return
            if len1 > len(self.friends):
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
        pt = re.compile('<li class="pftb_itm S_line1">(.*?)</li>')
        tmpdata = pt.search(data).groups()
        print tmpdata
        pt = re.compile('href="/p/(.*?)/home.*"')
        self.long_id = pt.search(tmpdata[0]).group(1)
        #pt = re.compile('')

    #get the infomation of WeiboUser 
    def get_user_info(self):
        self.get_info_action()
        print self.fans_sum, self.follow_sum, self.fans_sum

    def get_user_msg_page_sum(self, follow_data):
        ptn = re.compile('<a bpfilter="page" action-type="feed_list_page_more" action-data="currentPage=(.*?)&countPage=(.*?)"[^>]*>', re.UNICODE)
        return ptn.findall(follow_data)

    def get_user_msg_info(self, follow_data):
        ptn = re.compile('<div class="WB_text" node-type="feed_list_content">(.*?)</div>')
        return ptn.findall(follow_data)

    def get_user_first_msg_list(self, page_id):
        url = 'http://weibo.com/p/%s/weibo?page=%s' % (self.long_id, page_id)
        data = self.visit_url(url).replace('\\','')
        ptn = re.compile('<div class="WB_text" node-type="feed_list_content" [^>]*>n(.*?)</div>')
        self.msg_list += ptn.findall(data)
        ptn2 = re.compile('<div class="WB_text" node-type="feed_list_reason">[^<]*<em>(.*?)</em>[^<]</div>')
        self.zz_list += ptn2.findall(data)
        return

    def get_user_bar_msg_list_by_page(self, page_id):
        for pagebar_id in range(2):
            url = "http://weibo.com/p/aj/mblog/mbloglist?domain=100306&pre_page=%s&page=%s&count=15&pagebar=%s&max_msign=&filtered_min_id=&pl_name=Pl_Official_LeftProfileFeed__23&id=%s&script_uri=/p/%s/weibo&feed_type=0" % (page_id, page_id, pagebar_id, self.long_id, self.long_id) 
            data = json.loads(self.visit_url(url))
            data = data['data']
            ptn = re.compile('<div class="WB_text" node-type="feed_list_content" [^>]*>\n(.*?)</div>',re.UNICODE)
            self.msg_list += ptn.findall(data)
            ptn2 = re.compile('<div class="WB_text" node-type="feed_list_reason">\n.*<em>(.*?)</em>\n.*</div>',re.UNICODE)
            self.zz_list += ptn2.findall(data)
            if pagebar_id == 1:
                ll = self.get_user_msg_page_sum(data)[0]
                if not ll:
                    return False
                if len(ll) == 2 and int(ll[0]) == int(ll[1]):
                    return False
                elif len(ll) > 0:
                    ll = ll[0]
        return True

    def get_user_msg_list(self, r=None):
        i = 0
        if r:
            self.msg_list = r.lrange(self.long_id+"_msg_list", 0, -1)
        else:
            self.msg_list = None
        if not self.msg_list or len(self.msg_list)==0:
            self.msg_list = []
        else:
            return 
        while True:
            i = i + 1
            self.get_user_first_msg_list(i)
            if not self.get_user_bar_msg_list_by_page(i):
                break
        for msg in self.msg_list:
            r.rpush(self.long_id+"_msg_list", msg)
        return

    def get_key_words(self, r):
        self.get_user_msg_list(r)
        chinese_text = ''
        final_res = {}
        for msg in self.msg_list:
            chinese_text = msg
            _SEGMENT_BASE_URL = 'http://www.xunsearch.com/scws/api.php'
            payload = urllib.urlencode([('data', chinese_text), ('respond', 'json')])
            url = _SEGMENT_BASE_URL
            try:
                result = urllib2.urlopen(url, data=payload).read()
            except:
                print 'url open fail!!'
           
            result = json.loads(result)
            wordslist =  result['words']
            words_list_len = len(wordslist) if len(wordslist) < 5 else 5
            for i in xrange(words_list_len):
                if wordslist[i]['word'] in final_res:
                    final_res[wordslist[i]['word']] += wordslist[i]['idf']
                else:
                    final_res[wordslist[i]['word']] = wordslist[i]['idf']
        w = open('result','w')
        for key, value in sorted(final_res.items(), key=lambda d:d[1]):
            if len(key) < 2:
                continue
            w.write(key + " " + str(value)+"\n")
            print key, value
        w.flush()
        w.close()
        



if __name__ == '__main__':
    uid = sys.argv[1]
    newlogin = Login('dujun881228@sohu.com','dujun881228')
    newlogin.set_cookie()
    datastream = newlogin.login_action()
    pool = redis.ConnectionPool(host='localhost',port=6379,db=0)
    r = redis.Redis(connection_pool=pool)
    weibo_usr = WeiboUser(uid, '', '')
    weibo_usr.get_info_action()
    weibo_usr.get_user_msg_list(r)
    for msg in weibo_usr.msg_list:
        print msg
    #weibo_usr.get_user_msg_list()
    #weibo_usr.get_key_words(r) 

