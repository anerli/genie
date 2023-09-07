def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True


def find_prime_numbers():
    prime_numbers = []
    num = 2
    while len(prime_numbers) < 100:
        if is_prime(num):
            prime_numbers.append(num)
        num += 1
    for prime in prime_numbers:
        print(prime)


find_prime_numbers()
