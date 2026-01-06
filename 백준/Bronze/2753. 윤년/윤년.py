year = int(input())

if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0): # 조건 4의 배수이면서(and) (or) 100이 아니거나 400의 배수여야함
	print('1')
else:

	print('0')
