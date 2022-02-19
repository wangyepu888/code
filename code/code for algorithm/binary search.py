
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
 
list = [1,2,3,4,5,6,7,8,9,10,11,
        12,14,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,40]

print(binary_search(list, 22))