
import numpy as np
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





def Knapsack (weights, values, weight_capacity):
    ObjNumbers=[]
    for i in range(0,len(weights)):
        ObjNumbers.append(i)
    list=subsets(ObjNumbers,0,len(ObjNumbers)-1)
    y=0
    for j in list:
        v=0
        w=0
        for i in j:
            w=w+weights[i]
            v=v+values[i]
        if v>y and w<=weight_capacity:
            y=v
            l=j
    print(y)
    print(l)
            
    
weights=[1,2,3,4,7]
values=[11,15,19,30,50]
weight_capacity=14

Knapsack (weights, values, weight_capacity)
            
weight_capacity=5
Knapsack (weights, values, weight_capacity)  

weight_capacity=10
Knapsack (weights, values, weight_capacity)  
            
            
            
            
    