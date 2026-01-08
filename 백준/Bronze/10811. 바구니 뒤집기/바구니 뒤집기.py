n,m = map(int, input().split())
n2 = [*range(1, n+1)]

for _ in range(m):
    i, j = map(int, input().split())
    n2[i-1:j] = n2[i-1:j][::-1]

print(*n2)