# Implement the user interaction logic in the main function

import math


# Function to calculate the digits of PI accurately
# Reference: https://stackoverflow.com/a/9007879
# The algorithm used is the Bailey-Borwein-Plouffe (BBP) formula
# It calculates the nth hexadecimal digit of PI
# The formula is given by: PI = SUM(k=0 to infinity) (1/16^k) * (4/(8k+1) - 2/(8k+4) - 1/(8k+5) - 1/(8k+6))
# The formula is used to calculate the hexadecimal digits of PI, so we need to convert them to decimal digits
# We can do this by multiplying the hexadecimal digit by 16 and taking the integer part
# This will give us the corresponding decimal digit
# The number of digits to calculate is determined by the input parameter 'num_digits'
def calculate_pi_digits(num_digits):
    # Initialize variables
    pi_digits = []
    k = 0
    sum = 0
    
    # Calculate the digits of PI
    while len(pi_digits) < num_digits:
        # Calculate the terms of the BBP formula
        term1 = 4 / (8 * k + 1)
        term2 = 2 / (8 * k + 4)
        term3 = 1 / (8 * k + 5)
        term4 = 1 / (8 * k + 6)
        
        # Calculate the sum of the terms
        sum += (term1 - term2 - term3 - term4) / (16 ** k)
        
        # Calculate the hexadecimal digit
        hex_digit = int(sum * 16)
        
        # Convert the hexadecimal digit to decimal
        decimal_digit = hex_digit // 16
        
        # Add the decimal digit to the list
        pi_digits.append(decimal_digit)
        
        # Update k
        k += 1
        
    return pi_digits


# Fix the error in the main function where it cannot find the '__main__' module

def main():
    # Get the digits of PI
    pi_digits = calculate_pi_digits(100)
    
    # Initialize variables
    score = 0
    strikes = 0
    
    # Loop through each digit of PI
    for digit in pi_digits:
        # Ask the user to guess the digit
        guess = input('Guess the next digit of PI: ')
        
        # Check if the guess is correct
        if guess == str(digit):
            print('Correct!')
            score += 1
        else:
            print('Incorrect!')
            strikes += 1
            
            # Check if the user has reached 3 strikes
            if strikes == 3:
                print('Game over! You lost.')
                break
    
    # Print the final score
    print(f'Your score: {score}')


if __name__ == '__main__':
    main()
