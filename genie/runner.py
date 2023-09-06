import subprocess
import threading
import queue
import time

def monitor_stdout(process, output_queue):
    """Monitor the stdout of the subprocess and append it to a buffer."""
    while True:
        char = process.stdout.read(1)
        #print(f'Read: {repr(char)}')
        output_queue.put(char)

        # Seems to return char '' when process is over, so first check here may not be needed even.
        if process.poll() is not None and char == '':
            print('Returning from monitor')
            return

def interact_with_ai(buffered_output):
    """Stubbed function to interact with the AI."""
    print("AI received:", buffered_output)
    user_input = input("AI response (stdin for subprocess): ")
    return user_input

def run_python_file(filename):
    process = subprocess.Popen(
        ["python", filename],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True
    )

    output_queue = queue.Queue()

    monitor_thread = threading.Thread(target=monitor_stdout, args=(process, output_queue))
    monitor_thread.start()

    buffer = ""
    try:
        while True:
            time.sleep(1)
            # print('Monitor is alive? ', monitor_thread.is_alive())
            # print('Queue is empty? ', output_queue.empty())
            # print(f'Buffer: {repr(buffer)}')

            if not monitor_thread.is_alive() and output_queue.empty() and buffer == "":
                break

            if output_queue.empty():
                # Done with this batch
                print('done with buffer:', buffer)
                ai_response = interact_with_ai(buffer)
                if ai_response:
                    process.stdin.write(ai_response + '\n')
                    process.stdin.flush()
                buffer = ""
            while not output_queue.empty():
                ch = output_queue.get()
                buffer += ch
    finally:
        monitor_thread.join()

    # Collect any error messages
    stderr = process.stderr.read()
    if stderr:
        print(f"Error: {stderr.strip()}")

if __name__ == "__main__":
    filename = input("Enter the path to the Python file you want to run: ")
    run_python_file(filename)
