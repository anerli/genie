def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True


def find_prime_numbers(n):
    prime_numbers = []
    num = 2
    while len(prime_numbers) < n:
        if is_prime(num):
            prime_numbers.append(num)
        num += 1
    return prime_numbers


if __name__ == '__main__':
    primes = find_prime_numbers(int(input('Hello range for primes to find? ')))
    print(primes)
    primes = find_prime_numbers(int(input('Hello range for primes to find, again? ')))
    print(primes)

    if len(primes) > 10:
        # Example to show stderr
        x = 1 / 0