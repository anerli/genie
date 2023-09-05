# from subprocess import Popen, PIPE

# process = Popen([r'test_run.py'], stdin=PIPE, stdout=PIPE)

# to_program = input('> ')#"something to send to the program's stdin"
# while process.poll() == None:  # While not terminated
#     process.stdin.write(to_program)

#     from_program = process.stdout.readline()  # Modify as needed to read custom amount of output
#     print('Received: ', from_program)
#     to_program = input('> ')
#     # if from_program == "something":  # send something new based on stdout
#     #    to_program = "new thing to send to program"
#     # else:
#     #    to_program = "other new thing to send to program"

# print("Process exited with code {}".format(process.poll()))


# import subprocess

# def start(executable_file):
#     return subprocess.Popen(
#         ['python', executable_file],
#         stdin=subprocess.PIPE,
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE)

# def read(process):
#     return process.stdout.readline().decode("utf-8").strip()

# def write(process, message):
#     process.stdin.write(f"{message.strip()}\n".encode("utf-8"))
#     process.stdin.flush()

# def terminate(process):
#     process.stdin.close()
#     process.terminate()
#     process.wait(timeout=0.2)

# process = start("./test_run.py")
# #print(read(process))
# write(process, "100")
# print(read(process))
# terminate(process)


# import subprocess

# def start_executable_file(executable_file):
#     """Starts the specified executable file and returns the process."""
#     return subprocess.Popen(
#         executable_file,
#         stdin=subprocess.PIPE,
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#         text=True
#     )

# def read_process(process):
#     """Reads a line from the process's stdout."""
#     return process.stdout.readline().strip()

# def write_process(process, message):
#     """Writes a message to the process's stdin."""
#     process.stdin.write(message.strip() + '\n')
#     process.stdin.flush()

# def terminate_process(process):
#     """Terminates the process."""
#     process.stdin.close()
#     process.terminate()
#     process.wait()

# if __name__ == "__main__":
#     executable_file = input("Enter the path to the Python file you want to run: ")
#     process = start_executable_file(executable_file)
    
#     while True:
#         output = read_process(process)
#         if not output:
#             break
#         print(output)
#         user_input = input()
#         write_process(process, user_input)

#     terminate_process(process)

import subprocess

def start(executable_file):
    return subprocess.Popen(
        ['python', executable_file],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

def read(process):
    return process.stdout.readline().strip()

def write(process, message):
    process.stdin.write(f"{message.strip()}\n")
    process.stdin.flush()

def terminate(process):
    process.stdin.close()
    process.terminate()
    process.wait(timeout=0.2)

if __name__ == "__main__":
    process = start("./test_run.py")
    print(read(process))
    write(process, "100")
    print(read(process))
    terminate(process)
