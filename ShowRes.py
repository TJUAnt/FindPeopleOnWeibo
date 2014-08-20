#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
import redis
import json
import re
black_dict = dict([])
def read_black_dict():
    global black_dict
    w = open('black_dict.txt',"r")
    ss=w.readlines()
    for sub_str in ss:
        black_dict[sub_str[:-1]] = 1
if __name__ == '__main__':
    pool = redis.ConnectionPool(host='localhost',port=6379,db=0)
    r = redis.Redis(connection_pool=pool)
    res_que = r.lrange('res_list3', 0, -1)
    #w = open("../project/result3.html","w")
    #sstr = "<head><title>Some little people on Weibo</title><meta http-equiv=\"pragma\" content=\"no-cache\"><meta http-equiv=\"cache-control\" content=\"no-cache\"><meta http-equiv=\"expires\" content=\"0\"><meta http-equiv=\"content-type\" content=\"text/html; charset=UTF-8\" /><link rel=\"stylesheet\" type=\"text/css\" href=\"/css/template.css\"><link rel=\"stylesheet\" type=\"text/css\" href=\"/css/common.css\"></head>"
    #w.write(sstr.encode('utf-8')+'\n')
    sstr = "<body><div id = \"swap\"><div id = \"middle\"><div id = \"m_bar\"><div id = \"m_b_left\"></div><div id=\"m_b_content\"><div class = \"m_b_item\"><a href=\"#\">Some little people and their friends on Weibo</a></div><div id = \"m_text\">just a test</div></div><div id=\"m_b_right\"></div><p class=\"clear\"></p></div>"
    #w.write(sstr.encode('utf-8')+'\n')
    res_sum = 0
    #read_black_dict()
    sstr = "<div id = \"m_c\"><div id = \"m_c_list\">\n"
    #w.write(sstr.encode('utf-8')+'\n')
    for ss in res_que:
        ss = str(ss).replace("u'", "'");
        #print ss
        ss = ss.replace("'",'"')
        #print ss
        ss = json.loads(ss)
        #print ss
        if ss['uid'] in black_dict:
            continue
        if ss['href'] != '':
            sstr = "<div class=\"m_c_item\"><div class=\"m_c_item_title\"><center><a href=\""+ss['href']+"\" target=\"_blank\">"+ss['name']+"</a></center></div><div class=\"m_c_item_date\">"+ss['sex']+"</div><div class=\"m_c_people_limit\"> fans: "+str(ss['fans_sum'])+" / follow: "+str(ss['follow_sum'])+"</div><div class=\"m_c_cost\"> message: "+str(ss['msg_sum'])+"</div><div class=\"m_c_leader\"><center><span>"+ss['dir_txt']+"</span></center></div></div>"
    #        w.write(sstr.encode('utf-8'))
            print sstr
        #    w.write(sstr)
        #if int(ss['fans_sum']) + int(ss['follow_sum']) < 2500 and ss['href'] != '':
            print ss['name'], ss['uid'], ss['href'], ss['sex'], ss['dir_txt'], ss['fans_sum'], ss['follow_sum']
            res_sum += 1
    print res_sum
    sstr = "<p class=\"clear\"></p></div></div>Total: "+str(res_sum)+"</div><div id =\"buttom\"></div></div></body></html>" 
    #w.write(sstr.encode('utf-8'))
    #print len(res_que)
    #w.flush()
    #w.close()
