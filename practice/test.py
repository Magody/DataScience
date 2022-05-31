
import re
def ab():
    x=1
    return x

ab()
s = set('abc')
s.add("san")
print(s)

a = [1,2,3,4]
print(a.extend(a))
b = a
b[0] = 5
print(a[:-1])

print(set([1,2,16]) == set([16,2,1]))


def listSkills(val, list=[]):
    list.append (val)
    return list

list1 = listSkills( "NodeJS ")
list2 = listSkills('Java', [])
list3 = listSkills ( 'ReactJS')
print ("%s" % list1)
print ("%s" %  list2)


print ("%s" % list3)

def f(x,l=[]):
    for i in range(x):
        l.append(i*i)
    print(l)
    
f(2)
f(3, [3,2,1])
f(3)

"""

print("{} {1} {2}".format("a","b","c"))

fa = None
with open("sdfs.txt", "r") as fa:
    pass
print(fa.close)



a = [1,2,3,4]
b = a
b[0] = 5
print(a[:-1])


print("Welcom TURING".capitalize())


a = [1,2,3,4]
a.insert(2,1666)
print(a)


a = [1,2]
for i in a:
    a.append(3)
    print(a)
    

print(re.findall("welcome 123", "welcome", 1))


t = '%(a)s'
print(t % dict(a="W"))


array = [10,20]
array.pop()
print(array)

"""