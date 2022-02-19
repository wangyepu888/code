


def bubble_sort(l):
    for i in range(len(l) - 1):  
        for j in range(len(l) - i - 1): 
            if l[j] > l[j + 1]:
                l[j], l[j + 1] = l[j + 1], l[j]
    return l

def IsSorted (l):
        listlen = len(l)
        for i in range(listlen-1): ## i=0,1, ... listlen-2
                if l[i]>l[i+1]:
                        print(l[i],l[i+1])
                        return False

        return True

l=[0,9,8,7,6,5,4,3,2,1]
print(l)
bubble_sort(l)
if IsSorted(l)==False:
        print('not working')
print(l)

