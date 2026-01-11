a, b = map(int, input().split())

li1 = [list(map(int, input().split())) for _ in range(a)]
li2 = [list(map(int, input().split())) for _ in range(a)]

result = []
for i in range(a):
	row = []
	for j in range(b):
		row.append(li1[i][j] + li2[i][j])
	result.append(row)

for k in result:
	print(*k)