
def linerSearch(lst, x):

    i = 0

    count = len(lst)

    lst.append(x)

    while True:

        if lst[i] == x:

            del lst[count]

            return i if i < count else None

        i += 1

list = [1,2,3,4,5,6,7,8,9,10,11,
        12,14,14,15,16,17,18,19,20]

print(linerSearch(list, 11))



