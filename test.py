from random import randint

liste = []
for x in range(300): liste.append(randint(0,100))

def func(liste):
    liste.sort()
    for x in liste: 
        if liste.count(x) > 2: liste.remove(x)
    return liste

print(func(liste))