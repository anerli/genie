from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate
from langchain.chains.openai_functions import create_structured_output_chain
from process_runner import create_workspace_python_runner

llm = ChatOpenAI(temperature=0.0, model='gpt-3.5-turbo')

run_template = '''
You are a software tester, running and testing code that you have written.
You are not able to read the code itself but you are currently running the code.

Your manager has outlined the plan for this test run:
```
{plan}
```

You have access to the stdout and stderr of the program, and can optionally provide stdin.
You are to consider the plan above, and take any relevant notes about the program, what is going according to plan, what could be improved, and what might be a bug or error.

Here is the output of the program, and what you have provided as input, thus far:
{history}
'''[1:-1]

# stdout:
# ```
# {stdout}
# ```

# stderr:
# ```
# {stderr}
# ```

run_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(run_template)
])

run_chain = create_structured_output_chain({
    'type': 'object',
    'properties': {
        'stdin': {
            'type': 'string',
            'description': 'Text to pass to stdin. If not provided, nothing will be passed. If the output indicates the program is awaiting input, you should pass something to stdin, even if it is just for the purpose of continuing the program.'
        },
        'notes': {
            'type': 'string',
            'description': 'Any new notes to add relevant to how well the program is working or what needs fixing / improving'
        },
        'terminate': {
            'type': 'boolean',
            'description': 'If you believe the program to be stuck or looping forever, set terminate to true. Default is false.'
        }
    },
    'required': ['notes']
}, llm, run_prompt, verbose=True)

def summarize_history(history):
    '''
    Summarize history, a list of tuples (<stdout/stderr/stdin>, <text>)

    Combine consecutive stdout/stderr until hit stdin
    '''
    summary = ''
    stdout_chunk = ''
    stderr_chunk = ''
    for kind, text in history:
        if kind == 'stdout':
            #summary += '[STDOUT]\n'+text+'\n'
            stdout_chunk += text
        elif kind == 'stderr':
            #summary += '[STDERR]\n'+text+'\n'
            stderr_chunk += text
        elif kind == 'stdin':
            #summary += '[STDIN]\n'+text+'\n'
            if stdout_chunk:
                summary += '[STDOUT]\n'+stdout_chunk+'\n'
            if stderr_chunk:
                summary += '[STDERR]\n'+stderr_chunk+'\n'
            summary += '[STDIN]\n'+text+'\n'
            stdout_chunk = ''
            stderr_chunk = ''
    if stdout_chunk:
        summary += '[STDOUT]\n'+stdout_chunk+'\n'
    if stderr_chunk:
        summary += '[STDERR]\n'+stderr_chunk+'\n'
    return summary


def run_and_reflect(workspace, run_filepath, run_plan):
    print('Running and reflecting!')
    all_notes = []
    # Keep track of stdout/stderr/stdin so far so LLM has context
    #summary=''
    history = []
    
    runner = create_workspace_python_runner(workspace, run_filepath)

    runner.start()
    is_done = False
    stdin = None
    #last_stdout = None
    while True:
        stdout, stderr, is_done = runner.next(stdin, True)

        print('stdout:', stdout)
        print('stderr:', stderr)

        #summary += '[STDOUT]\n'+stdout+'\n'
        #summary += '[STDERR]\n'+stderr+'\n'
        history.append(('stdout', stdout))
        history.append(('stderr', stderr))

        # If stdout is blank, it may have been because LLM did not provide input when it should have?
        # if stdout == '' and last_stdout:
        #     stdout = last_stdout
        # last_stdout = stdout

        
        if is_done:
            break
        
        resp = run_chain.run(plan=run_plan, history=summarize_history(history)) #stdout=stdout, stderr=stderr)
        if 'stdin' in resp:
            stdin = resp['stdin']
        else:
            stdin = None
        if 'terminate' in resp:
            terminate = resp['terminate']
        else:
            terminate = False
        
        print('stdin:', stdin)
        if stdin != None:
            history.append(('stdin', stdin))

        notes = resp['notes']
        print('notes:', notes)
        all_notes.append(notes)

        if terminate:
            # LLM thinks the program is stuck
            print('Termination commenced by LLM')
            runner.terminate()
            #self.process.
            break
        #print('notes:', notes)

        # stdin = input('stdin: ')
        # if stdin == '':
        #     stdin = None
    runner.close()
    return all_notes
