
li_ = []

for _ in range(10):
    num = int(input())
    li_.append(num % 42)

li2_ = []
for a in range(10):
    for b in range(10):
        if li_[a] == li_[b]:
            li2_.append(li_[a])
        b += 1
    a += 1
    
print(len((set(li2_))))