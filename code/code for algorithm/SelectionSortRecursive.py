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
                        
def IsSorted (l):
        listlen = len(l)
        for i in range(listlen-1): ## i=0,1, ... listlen-2
                if l[i]>l[i+1]:
                        print(l[i],l[i+1])
                        return False

        return True
l=[0,9,8,7,6,5,4,3,2,1]
print(l)
SelectionSortRecursive(l,0,len(l)-1)
if IsSorted(l)==False:
        print('not working')
print(l)
