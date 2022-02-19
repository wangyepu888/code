def swap (x,y):
        tmp=x
        x=y
        y=tmp
def BubbleSortRecursive(l,left,right):
    if left==right:
               return
    for i in range (right-1):
        if l[i]>l[i+1]:
            l[i], l[i + 1] = l[i + 1], l[i]
    BubbleSortRecursive(l,left,right-1)

def IsSorted (l):
        listlen = len(l)
        for i in range(listlen-1): ## i=0,1, ... listlen-2
                if l[i]>l[i+1]:
                        print(l[i],l[i+1])
                        return False

        return True

l=[0,9,8,7,6,5,4,3,2,1]
print(l)
BubbleSortRecursive(l,0,len(l))
if IsSorted(l)==False:
        print('not working')
print(l)




