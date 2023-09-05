import subprocess
import threading
import queue

def monitor_stdout(process, output_queue, data_available_event):
    """Monitor the stdout of the subprocess and append it to a buffer."""
    buffer = ""
    while True:
        char = process.stdout.read(1)
        print('Read:', char)
        if char:
            print('Char')
            buffer += char
            print('New buffer:', buffer)
            data_available_event.set()

            if buffer:
                output_queue.put(buffer.strip())
                print('output queue:', output_queue)
                buffer = ""
        else:
            print('No char')
            
            if process.poll() is not None:
                print('Returning from monitor')
                return

def interact_with_ai(buffered_output):
    """Stubbed function to interact with the AI."""
    print("AI received:", buffered_output)
    user_input = input("AI response (stdin for subprocess): ")
    return user_input

def run_python_file(filename):
    """Run a specified Python file and interact with it."""
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
    data_available_event = threading.Event()

    # Start a thread to monitor the subprocess's stdout
    monitor_thread = threading.Thread(target=monitor_stdout, args=(process, output_queue, data_available_event))
    monitor_thread.start()

    buffer = ""
    try:
        while process.poll() is None:
            data_available = data_available_event.wait(1)  # Wait for 1 second
            print('Data available thing done')
            
            # Process the buffer if the event was set or if there's data in the buffer
            if data_available or buffer:
                print('data available or buffer')
                while not output_queue.empty():
                    ch = output_queue.get()
                    print('adding to buffer:', ch)
                    buffer += output_queue.get()
                data_available_event.clear()
                
                if buffer:
                    print('buffer')
                    ai_response = interact_with_ai(buffer)
                    if ai_response:
                        process.stdin.write(ai_response + '\n')
                        process.stdin.flush()
                    buffer = ""
    finally:
        monitor_thread.join()

    # Collect any error messages
    stderr = process.stderr.read()
    if stderr:
        print(f"Error: {stderr.strip()}")

if __name__ == "__main__":
    filename = input("Enter the path to the Python file you want to run: ")
    run_python_file(filename)
