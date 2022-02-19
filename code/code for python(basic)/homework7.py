def getText():
    txt=open('speech.txt').read()
    txt=txt.lower()
    for ch in ' ! " () * + , - . ? ':
        txt=txt.replace(ch," ")
    return txt
txt=getText()
for word in txt:
    word = word.strip()
speech=txt.split()
num=0
for word in speech:
    num=num+1
print(num)
counts={}
for word in speech:
    counts[word]=counts.get(word, 0)+1
items=list(counts.items())
items.sort(key=lambda x:x[1],reverse=True)
for i in range(10):
    word,count=items[i]
    print("{0:<10}{1:>5}".format(word,count))
print(counts)