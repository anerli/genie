def is_prime(num):
    if num < 2:
        return False
    for i in range(2, int(num ** 0.5) + 1):
        if num % i == 0:
            return False
    return True


def find_prime_numbers():
    prime_numbers = []
    num = 2
    while len(prime_numbers) < 100:
        if is_prime(num):
            prime_numbers.append(num)
        num += 1
    return prime_numbers


if __name__ == '__main__':
    primes = find_prime_numbers()
    print(primes)
