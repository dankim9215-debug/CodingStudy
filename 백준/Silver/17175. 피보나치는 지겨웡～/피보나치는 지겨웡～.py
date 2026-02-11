n = int(input())
dp = [1,1,3]

for i in range(3, n+1):
    dp.append((dp[i-1] + dp[i-2] + 1)%1000000007)

print(dp[n])