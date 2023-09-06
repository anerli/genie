import subprocess
import threading
import queue
import time
import os

def monitor_stdout(process, stdout_queue):
    """Monitor the stdout of the subprocess and append it to a buffer."""
    while True:
        char = process.stdout.read(1)
        #print(f'Read: {repr(char)}')
        stdout_queue.put(char)

        # Seems to return char '' when process is over, so first check here may not be needed even.
        if process.poll() is not None and char == '':
            print('Returning from stdout monitor')
            return

def monitor_stderr(process, stderr_queue):
    """Monitor the stderr of the subprocess and append it to a buffer."""
    while True:
        char = process.stderr.read(1)
        #print(f'Read: {repr(char)}')
        stderr_queue.put(char)

        # Seems to return char '' when process is over, so first check here may not be needed even.
        if process.poll() is not None and char == '':
            print('Returning from stderr monitor')
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

class ProcessRunner:
    def __init__(self, process_args, relisten_time=1.0, max_output_time=10.0):
        self.process_args = process_args
        self.relisten_time = relisten_time
        self.max_output_time = max_output_time
    
    def start(self):
        self.process = subprocess.Popen(
            #["python", filename],
            self.process_args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        self.stdout_queue = queue.Queue()
        self.stderr_queue = queue.Queue()

        self.stdout_monitor_thread = threading.Thread(target=monitor_stdout, args=(self.process, self.stdout_queue))
        self.stdout_monitor_thread.start()

        self.stderr_monitor_thread = threading.Thread(target=monitor_stderr, args=(self.process, self.stderr_queue))
        self.stderr_monitor_thread.start()
    
    def next(self, stdin=None, debug=False):
        '''
        Returns text, is_done
        Get next block of stdout text, and optionally pass into stdin
        '''
        if stdin != None:
            self.process.stdin.write(stdin + '\n')
            self.process.stdin.flush()

        stdout, stderr = self._collect_output_batch()

        if debug:
            print('Stdout monitor is alive? ', self.stdout_monitor_thread.is_alive())
            print('Stderr monitor is alive? ', self.stderr_monitor_thread.is_alive())
            #print('Queue is empty? ', self.output_queue.empty())
            #print(f'Buffer: {repr(buffer)}')

        is_done = not self.stdout_monitor_thread.is_alive() and not self.stderr_monitor_thread.is_alive() and self.stdout_queue.empty() and self.stderr_queue.empty()# and buffer == ''

        return stdout, stderr, is_done
        
    def _collect_output_batch(self):
        # Collect next batch of output
        stdout_buffer = ''
        stderr_buffer = ''
        total_time = 0.0
        while True:
            # Wait for output
            time.sleep(self.relisten_time)
            total_time += self.relisten_time

            if self.stdout_queue.empty() and self.stderr_queue.empty():
                break

            while not self.stdout_queue.empty():
                stdout_buffer += self.stdout_queue.get()
            while not self.stderr_queue.empty():
                stderr_buffer += self.stderr_queue.get()
            
            if total_time > self.max_output_time:
                break
        
        return stdout_buffer, stderr_buffer
    
    def close(self):
        self.stdout_monitor_thread.join()
        self.stderr_monitor_thread.join()
    
    def debug_run(self):
        # Example against user input as stub for AI response
        self.start()
        is_done = False
        stdin = None
        while True:
            stdout, stderr, is_done = self.next(stdin, True)
            print('stdout:', stdout)
            print('stderr:', stderr)
            if is_done:
                break
            stdin = input('stdin: ')
            if stdin == '':
                stdin = None
        self.close()


def create_workspace_python_runner(workspace, python_file_path):
    return ProcessRunner(['python', os.path.join(workspace, python_file_path)])