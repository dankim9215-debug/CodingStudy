t = int(input()) # 테스트 케이스 갯수

rows = 15
cols = 15
# 2차원 배열 만들 준비 됐나
apt = [[0 for _ in range(cols)] for _ in range(rows)]
# 0으로 초기화해서 만든당
for i in range(1, 15):
    apt[0][i] = i
# 0층 i호에는 i명이 산다 호호
for j in range(1, 15):
    for k in range(1, 15):
        apt[j][k] = apt[j-1][k] + apt[j][k-1]
# j층 k호는 j-1층 k호와 j층 k-1호를 더하면 됨 for example 302호 값은 301호까지의 합과 202호의 합
for _ in range(t):
    a = int(input())
    b = int(input())
    print(apt[a][b])