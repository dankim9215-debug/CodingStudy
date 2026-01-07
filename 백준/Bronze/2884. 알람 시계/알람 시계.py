hour, min = map(int, input().split())

min -= 45

if min < 0:
    min += 60
    hour = (hour - 1) % 24

print(hour, min)