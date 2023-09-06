import subprocess
import threading
import queue
import time
import os

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

        self.output_queue = queue.Queue()

        self.monitor_thread = threading.Thread(target=monitor_stdout, args=(self.process, self.output_queue))
        self.monitor_thread.start()
    
    def next(self, stdin=None, debug=False):
        '''
        Returns text, is_done
        Get next block of stdout text, and optionally pass into stdin
        '''
        if stdin != None:
            self.process.stdin.write(stdin + '\n')
            self.process.stdin.flush()

        buffer = self._collect_output_batch()

        if debug:
            print('Monitor is alive? ', self.monitor_thread.is_alive())
            print('Queue is empty? ', self.output_queue.empty())
            print(f'Buffer: {repr(buffer)}')

        is_done = not self.monitor_thread.is_alive() and self.output_queue.empty()# and buffer == ''

        return buffer, is_done
        
    def _collect_output_batch(self):
        # Collect next batch of output
        buffer = ''
        total_time = 0.0
        while True:
            # Wait for output
            time.sleep(self.relisten_time)
            total_time += self.relisten_time

            if self.output_queue.empty():
                break

            while not self.output_queue.empty():
                ch = self.output_queue.get()
                buffer += ch
            
            if total_time > self.max_output_time:
                break
        
        return buffer
    
    def close(self):
        self.monitor_thread.join()
    
    def debug_run(self):
        # Example against user input as stub for AI response
        self.start()
        is_done = False
        stdin = None
        while True:
            stdout, is_done = self.next(stdin, True)
            print('stdout:', stdout)
            if is_done:
                break
            stdin = input('stdin: ')
            if stdin == '':
                stdin = None
        self.close()


def create_workspace_python_runner(workspace, python_file_path):
    return ProcessRunner(['python', os.path.join(workspace, python_file_path)])