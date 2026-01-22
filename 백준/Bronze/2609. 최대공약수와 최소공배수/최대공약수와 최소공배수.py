import math

a,b = map(int, input().split())
# 최대공약수
print(math.gcd(a, b))
# 최소공배수
print(math.lcm(a, b))