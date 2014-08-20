import sys
import thread
from WeiboUser import WeiboUser
from WeiboLogin import Login
#from __future__ import division
import redis
import json
import re

usr_dict = dict([])
black_dict = dict([])
usr_list = dict([])
finish_dict = dict([])
#def read_black_dict():
#    global black_dict
#    w = open('black_dict.txt',"r")
#    ss=w.readlines()
#    for sub_str in ss:
        #print sub_str[:-1]
#        black_dict[sub_str[:-1]] = 1

def Process_Single_User(r, weibo_usr, flag):
    global usr_dict 
    global usr_list 
    global black_dict
    global finish_dict
    weibo_usr.print_info()
    r.rpush('res_list3',weibo_usr.turn_json())
    uid = weibo_usr.uid
    ulist = list([])
    ulist.append(uid)
    fd_set = uid + 'fdset'
    if flag == 1:
        r.delete(fd_set)
    fdset = r.smembers(fd_set)
    print len(fdset)
    if len(fdset) == 0:
        weibo_usr.get_friends_by_web_stable(ulist)
        for uuid in weibo_usr.friends:
            if uuid not in black_dict:
                r.sadd(fd_set,uuid)
    else:
        weibo_usr.friends.clear()
        for uuid in fdset:
            if uuid not in black_dict:
                weibo_usr.friends.add(uuid) 
    for uuid in weibo_usr.friends:
        if uuid in black_dict:
            continue
        if uuid in usr_dict:
            usr_dict[uuid] += 1
        else:
            usr_dict[uuid] = 1
        if uuid not in usr_list:
            usr_list[uuid] = set([])
        usr_list[uuid].add(uid)
        usr_list[uid].add(uuid)
    weibo_usr.get_self_fans_follow()
    cnt = 0
    for tu in weibo_usr.fans_follow:
        cnt += 1
        #if cnt > 5:
        #    break
        #tu.print_info()
        if tu.uid not in black_dict:
            if tu.uid in usr_dict:
                usr_dict[tu.uid] += 1
            else:
                usr_dict[tu.uid] = 1
            if tu.uid not in usr_list:
                usr_list[tu.uid] = set([])
            usr_list[tu.uid].add(uid)
            usr_list[uid].add(tu.uid)

def WeiboClassSearch(r,flag,uidlist):
    global dict_lock
    global usr_dict
    global black_dict
    global finish_dict
    global usr_list
#    read_black_dict()
    usr_dict.clear()
    usr_list.clear()
    finish_dict.clear()
    que = []
    uidset = set([])
    r.delete('res_list3')
    for uid in uidlist:
        print uid
        weibo_usr = WeiboUser(uid,'','')
        weibo_usr.get_info_action()
        usr_dict[uid] = 1
        usr_list[uid] = set([])
        Process_Single_User(r,weibo_usr,flag)
        finish_dict[uid] = 1
    print finish_dict
    while True:
        max_sum = 0
        max_cnt = 0
        tmp_uid = -1
        for uid in usr_dict:
            tmp_sum = 0
            tmp_cnt = 0
            for list_uid in usr_list[uid]:
                tmp_sum += usr_dict[list_uid]
                tmp_cnt += 1
            if uid not in finish_dict:
                if max_cnt < tmp_cnt:
                    max_cnt = tmp_cnt
                    max_sum = tmp_sum
                    tmp_uid = uid
                elif max_cnt == tmp_cnt and tmp_sum > max_sum:
                    max_sum = tmp_sum
                    tmp_uid = uid
                #max_sum = tmp_sum
                #tmp_uid = uid
        weibo_usr = WeiboUser(tmp_uid,'','')
        weibo_usr.get_info_action()
        finish_dict[tmp_uid] = 1
        if weibo_usr.fans_sum < 3500 and weibo_usr.href != '':
            print "max_sum: %d max_cnt: %d" % (max_sum, max_cnt)
            Process_Single_User(r, weibo_usr, flag)

if __name__ == '__main__':
    newlogin = Login('dujun881228@sohu.com','dujun881228');
    newlogin.set_cookie()
    datastream = newlogin.login_action()
    #print datastream

    pool = redis.ConnectionPool(host='localhost',port=6379,db=0)
    r = redis.Redis(connection_pool=pool)
    #read_black_dict()
    uidlist = []
    uidlist = raw_input('Please input the some\'s Weibo uids in the group(separated by space, at least 4):').split()
    if len(uidlist) < 4:
        print 'not enough infomation for search!!!'
    else:
        WeiboClassSearch(r, 1, uidlist)
