def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def find_primes(limit):
    primes = []
    for num in range(2, limit + 1):
        if is_prime(num):
            primes.append(num)
    return primes

if __name__ == '__main__':
    limit = int(input("Enter the upper limit: "))
    primes = find_primes(limit)
    print("Prime numbers up to", limit, "are:")
    for prime in primes:
        print(prime)