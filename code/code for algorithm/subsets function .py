# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 20:22:55 2021

@author: Yepu Wang
"""
import  copy
def subsets(l,left,right):
    lists=[]
    if left>right:
        empty_list=[]
        lists.append(empty_list)
        print("subsets of l",left ,right,"have",len(lists),"subsets")
        return lists
    list1=subsets(l,left+1,right)
    lists=copy.deepcopy(list1)
    for s in list1:
        s.append(l[left])
        lists.append(s)
    
    return lists

data=[20,30.40,50,60,70,80]
lists=subsets(data,0,len(data)-1)
for s in lists:
    print (s)