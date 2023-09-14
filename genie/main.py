import sys
from mancer import Mancer
# print('Hello, I am GENIE, I shall grant you one wish. Please describe the software you would like me to create.')

# desc = input('> ')

if __name__ == '__main__':
    workspace = './test_workspace'
    goal = 'Write a program that finds the first 100 prime numbers.'

    if len(sys.argv) == 3:
        workspace = sys.argv[1]
        goal = sys.argv[2]
    
    mancer = Mancer(goal, workspace)
    mancer.cycle_until_finished()