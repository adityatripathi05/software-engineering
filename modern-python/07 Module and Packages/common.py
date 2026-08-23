''' This module is having
- variable 'name'
- functions like is_even_odd(), factorial(), is_prime()
- class Student with method total(), avg_marks(),
percent
'''
name='Aditya Tripathi'

def is_even_odd(num):
    if num%2 == 0:
        return f'{num} is even no.'
    else:
        return f'{num} is odd no.'

def factorial(num):
    f=1
    for i in range(num,0,-1):
        f *= i
    return f'factorial of {num} is {f}.'

def is_prime(num):
    count = 0
    if (num == 1):
        return '1 is neither prime nor composite'
    else:
        for i in range (2, (num//2)+1):
            if (num % i == 0):
                count += 1
        if (count == 0):
            return f'{num} is prime number'
        else:
            return f'{num} is not a prime number'

class Student:
    def __init__(self,name,m1,m2,m3,m4,m5):
        self.name = name
        self.m1 = m1
        self.m2 = m2
        self.m3 = m3
        self.m4 = m4
        self.m5 = m5
    def total(self):
        return self.m1+self.m2+self.m3+self.m4+self.m5
    def avg_marks(self):
        return f'Average marks: {self.total()/5}'
    def percent(self):
        return f'Percentage: {(self.total()/500)*100}%'

if __name__=='__main__':
    print(name)
    print(is_even_odd(16))
    print(is_prime(19))
    
