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
def IsSorted (l):
        listlen = len(l)
        for i in range(listlen-1): ## i=0,1, ... listlen-2
                if l[i]>l[i+1]:
                        print(l[i],l[i+1])
                        return False

        return True
l=[0,9,8,7,6,5,4,3,2,1]
print(l)
SelectionSort(l)
if IsSorted(l)==False:
        print('not working')
print(l)