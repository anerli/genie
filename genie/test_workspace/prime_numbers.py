def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True


def find_prime_numbers(n):
    prime_numbers = []
    count = 0
    num = 2
    while count < n:
        if is_prime(num):
            prime_numbers.append(num)
            count += 1
        num += 1
    return prime_numbers


if __name__ == '__main__':
    primes = find_prime_numbers(100)
    print(primes)