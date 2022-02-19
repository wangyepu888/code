#Yepu Wang 2020/11/17
class FileAnalyzer(object):
    global article
    article=[]
    txt=open('article.txt').read()
    txt=txt.lower()
    for ch in ' ! " () * + , - . ? ':
        txt=txt.replace(ch," ")
    for word in txt:
        word = word.strip()
    article=txt.split()
    def number(self):
        num=0
        for word in article:
            num=num+1
        print(num)
    def counts_word(self):
        counts={}
        for word in article:
            counts[word]=counts.get(word, 0)+1
        items=list(counts.items())
        items.sort(key=lambda x:x[1],reverse=True)
        for i in range(10):
            word,count=items[i]
            print("{0:<10}{1:>5}".format(word,count))
        print(counts)
words=FileAnalyzer()
words.number()
words.counts_word()