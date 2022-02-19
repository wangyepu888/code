import random
import time

def bubble_sort(l):
    for i in range(len(l) - 1):  
        for j in range(len(l) - i - 1):  
            if l[j] > l[j + 1]:
                l[j], l[j + 1] = l[j + 1], l[j]
    return l

def linerSearch(lst, x):

    i = 0

    count = len(lst)

    lst.append(x)

    while True:

        if lst[i] == x:

            del lst[count]

            return i if i < count else None

        i += 1
        

def binary_search(list, item):
    low = 0               
    high = len(list)                
 
    while low <= high:
        mid = int((low + high) / 2)  
        guess = list[mid]
        if guess == item:        
            return mid
        elif guess > item:     
            high = mid - 1     
        else:
            low = mid + 1      
    return None

def RandList (start, end, len):
        res = [] # an empty list

        for j in range (len):
                res.append (random.randint(start,end))
                
        return res
    
print('length','LinearSearch','BinarySearch')

for i in range(10,2000,20): ## i=10,30,50,70, ... 1990OB
        c1=RandList(1,10000,i)
        a=random.choice(c1)
        bubble_sort(c1)
        
        start_time = time.time()
        linerSearch(c1,a)
        end_time = time.time()
        time1=end_time-start_time
        
        start_time = time.time()
        binary_search(c1,a)
        end_time = time.time()
        time2=end_time-start_time
        
        print (i,time1,time2) 







