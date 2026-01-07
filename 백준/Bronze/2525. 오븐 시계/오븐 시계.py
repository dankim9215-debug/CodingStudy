hour, minute = map(int, input().split())
expt = int(input())

minute += expt

while minute >= 60:
	hour = (hour + 1) % 24
	minute -= 60

minute %= 60

print(hour, minute)