# -*- coding: utf-8 -*-
"""
Created on Wed Mar 17 14:45:12 2021

@author: Administrator
"""
import random
import time
from queue import Queue

def IsSorted (l):
        listlen = len(l)
        for i in range(listlen-1): ## i=0,1, ... listlen-2
                if l[i]>l[i+1]:
                        print(l[i],l[i+1])
                        return False

        return True

def FindMinimum (l, left, right):

        ## minV is the minimum value so far
        ## in the beginning, first value is the smallest ... 
        minV = l[left]
        minI = left

        for i in range (left,right+1): ## i=left, left+1, ... right
                if l[i]<minV:
                        minV = l[i]
                        minI = i

                ## loop invariant
                ## minV = min (l[left...i]), i.e., min. value seen so far 
                ## minV = l[minI]

        return minI

                                           
                
#mergesort recursion
def MergeSort(l):
    if len(l)<=1:
        return l 
    else: 
        mid=len(l)//2
        l1=MergeSort(l[:mid])
        l2=MergeSort(l[mid:])
    merged=[]
    while l1 and l2:
        if l1[0]<l2[0]:
            merged.append(l1.pop(0))
        else:
            merged.append(l2.pop(0))
    merged.extend(l1 if l1 else l2)
    return merged




## Iterative Merge sort l[] into ascending order
def function(q):
   Q=Queue(maxsize=20)
   while q.empty()==False:
       left=q.get()
       merged=[]
       if q.empty()==False:
           right=q.get()
           while left and right:
               if left[0]<right[0]:#小的先添加到结果
                  merged.append(left.pop(0))
               else:
                  merged.append(right.pop(0))
                #print(merged)
           merged.extend(left if left else right)
       else:
               merged=left
       Q.put(merged)
   return Q

def iteration_MergeSort(alist):
    n=len(alist)
    q=Queue(maxsize=n)
    for i in range (n):
        q.put([alist[i]]) 
    while q.qsize()>1:
        q=function(q)
    return q.get()
   



## partition l[left...right] using l[right] as pivot: 
## return index of the pivot value 
def partition(A,left,right):
    x=A[right]
    i=left-1
    for j in range(left,right):
        if A[j]<=x:
            i=i+1
            if i!=j:
              tmp=A[i]
              A[i]=A[j]
              A[j]=tmp
    tnp=A[i+1]
    A[i+1]=A[right]
    A[right]=tnp
    return i+1
    
#quicksort


def Quicksort(l,left,right):
     if left>=right:
        return
     q=partition(l,left,right)
     Quicksort(l,left,q-1)
     Quicksort(l,q+1,right)



def Selection (l, k):
    v=random.randint(0,len(l)-1)
    SL=[]
    SV=[]
    SR=[]
    for i in range(len(l)):
        if l[i]==l[v]:
            SV.append(l[i])
        if l[i]>l[v]:
            SR.append(l[i])
        if l[i]<l[v]:
            SL.append(l[i])
    if k<=len(SL):
        return Selection (SL, k)
    if len(SL)<k<=(len(SL)+len(SV)):
        return l[v]
    if k>(len(SL)+len(SV)):
        return Selection (SR, k-len(SL)-len(SV))
    
## check if l[] contains duplicate or not
## l is sorted
def ContainDuplicateSortedList(l):
      if len(l)<2:
          return False
      else:
          mid=(len(l))//2
          if l[mid]==l[mid-1]:
              return True
          else:
              n=ContainDuplicateSortedList(l[:mid])
              m=ContainDuplicateSortedList(l[mid:])
              if n==True or m==True:
                  return True
## check if l[] contains duplicate or not
## l is not sorted, and you are not allowed to sort it 
def ContainDuplicate(l):
    for i in range (len(l)):
        for j in range(i+1,len(l)):
            if l[i]==l[j]:
                return True
    return False

#testing MergeSort
print('testing MergeSort')
l=[38,27,43,3,9,82,10,8]  
a=MergeSort(l)
if IsSorted(a)==False:
        print('MergeSort not working')
print(a)

la=[]

lb=[2,1]
lc=[5,4,6]
ld=[10,11,9,8,7,6,31,4,3,20]
le=[2,11,9,8,7,6,31,4,3,5]
print(MergeSort(la))
print(MergeSort(lb))
print(MergeSort(lc))
print(MergeSort(ld))
print(MergeSort(le))

#testing iteration_MergeSort
print('testing iteration_MergeSort')
alist=[9,8,7,6,5,4,3,2,1,10]
b=iteration_MergeSort(alist)
if IsSorted(b)==False:
        print('MergeSort not working')
print(b)

#testing partition
print('testing partition')
l2=[2,8,7,1,3,5,6,4]
print(partition(l2,0,len(l2)-1))
print(l2)

#testing quicksort
print('testing quicksort')
l3=[200,3,5,7,0,4,7,15,5,2,7,9,10,15,9,17,12,15]
Quicksort(l3,0,len(l3)-1)
print(l3)


##testing selection algorithm
print('testing selection algorithm')

l4=[9,8,7,6,5,4,3,11,12,14]
print(Selection (l4, 5))

#testing ContainDuplicateSortedList algorithms 
print("testing ContainDuplicateSortedList algorithms ")
l5=[1,2,3,4,5,6,7,8]
l6=[1,2,3,4,5,5,6,7,8,9]
print(ContainDuplicateSortedList(l5))
print((ContainDuplicateSortedList(l6)))

#testing ContainDuplicate
print('testing ContainDuplicate')
l7=[1,2,3,9,8,7,6,11,12,14,15,11]
print(ContainDuplicate(l7))