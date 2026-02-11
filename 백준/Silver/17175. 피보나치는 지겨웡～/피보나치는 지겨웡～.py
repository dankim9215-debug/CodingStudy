n = int(input())

d = [1, 1]

for i in range(2, n + 1):
    new_value = d[i-1] + d[i-2] + 1
    d.append(new_value % 1000000007)

print(d[n])