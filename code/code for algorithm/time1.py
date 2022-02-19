import random
import time

def RandList (start, end, len):
        res = [] # an empty list

        for j in range (len):
                res.append (random.randint(start,end))
                
        return res
    
def FindMinimum (l, left, right):

        ## minV is the minimum value so far
        ## in the beginning, first value is the smallest ... 
        minV = l[left]
        minI = left

        for i in range (left,right+1): ## i=left, left+1, ... right
                if l[i]<minV:
                        minV = l[i]
                        minI = i
        
        return minI
def SelectionSortRecursive (l,left,right):

           #fine index of smallest element in l[i...listlen-1]
           if left==right:
               return

           minIndex = FindMinimum (l, left, right)

                
           if minIndex!=left:
                        # the following does not work! 
                        #swap (l[i], l[minIndex]) 
                 l[left],l[minIndex]=l[minIndex],l[left]

           SelectionSortRecursive (l, left+1, right)

def SelectionSort (l):
        listlen=len(l)

        for i in range(listlen): ## i=0, 1, 2, ..., listlen-1
                #fine index of smallest element in l[i...listlen-1]
                minIndex = FindMinimum (l, i, listlen-1)

                #swap if needed
                if minIndex!=i:
                        # the following does not work! 
                        #swap (l[i], l[minIndex]) 
                        l[i],l[minIndex]=l[minIndex],l[i]
                
def BubbleSort(l):
    for i in range(len(l) - 1):  
        for j in range(len(l) - i - 1):  
            if l[j] > l[j + 1]:
                l[j], l[j + 1] = l[j + 1], l[j]
    return l

def BubbleSortRecursive(l,left,right):
    if left==right:
               return
    for i in range (right-1):
        if l[i]>l[i+1]:
            l[i], l[i + 1] = l[i + 1], l[i]
    BubbleSortRecursive(l,left,right-1)
print('lenth','BubbleSort','RecursiveBubbleSort','SelectionSort','RecursiveSelectionSort')
for i in range(10,2000,20): ## i=10,30,50,70, ... 1990OB
        c1=RandList(1,10000,i)
        c2=c1
        c3=c1
        c4=c1
        start_time = time.time()
        BubbleSort(c1)
        end_time = time.time()
        time1=end_time-start_time
        
        start_time = time.time()
        BubbleSortRecursive(c2,0,len(c2))
        end_time = time.time()
        time2=end_time-start_time
        
        start_time = time.time()
        SelectionSort(c3)
        end_time = time.time()
        time3=end_time-start_time
        
        start_time = time.time()
        SelectionSortRecursive (c4,0,len(c4)-1)
        end_time = time.time()
        time4=end_time-start_time
        
        print (i, time1,time2,time3,time4) 