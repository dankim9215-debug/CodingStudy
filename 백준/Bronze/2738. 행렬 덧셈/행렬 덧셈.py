a, b = map(int, input().split())

li1 = [list(map(int, input().split())) for _ in range(a)]
li2 = [list(map(int, input().split())) for _ in range(a)]

for r1, r2 in zip(li1, li2):
    row = [c1 + c2 for c1, c2 in zip(r1, r2)]
    print(*row)