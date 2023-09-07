from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate
from langchain.chains.openai_functions import create_structured_output_chain
from process_runner import create_workspace_python_runner

llm = ChatOpenAI(temperature=0.0, model='gpt-3.5-turbo')

run_template = '''
You are a software tester, running and testing code that you have written.
You are not able to read the code itself but you are currently running the code.

Your manager has outlined the run plan for this test:
```
{plan}
```

Here are your thoughts so far:
{thoughts}

Here is the output of the program, and what you have provided as input, thus far:
{history}

Be direct and pass to stdin immediately if applicable, and terminate as soon as plan is completed.
'''[1:-1]

# You have access to the stdout and stderr of the program, and can optionally provide stdin.
# You are to consider the plan above, and take any relevant notes about the program, what is going according to plan, what could be improved, and what might be a bug or error.


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
            'description': 'Text to pass to stdin. Provide empty string to not send anything to stdin.'#'Text to pass to stdin. If not provided, nothing will be passed. If the output indicates the program is awaiting input, you should pass something to stdin, even if it is just for the purpose of continuing the program.'
        },
        'thoughts': {
            'type': 'string',
            'description': 'Note your thoughts about how the program is running, what inputs you might want to provide, and when you might want to terminate the program'
        },
        # 'notes': {
        #     'type': 'string',
        #     'description': 'Take note of key information specifically relevant to the run plan: Check if the program correctly finds the first 100 prime numbers.'#'Add any important notes',#'Add notes specifically relevant to the run plan'#'Any new notes to add relevant to how well the program is working or what needs fixing / improving'
        # },
        'terminate': {
            'type': 'boolean',
            'description': 'Set terminate to true if you believe the program is stuck or if you have gathered all necessary information'#'If you believe the program to be stuck or looping forever, set terminate to true. Default is false.'
        }
    },
    'required': ['stdin', 'thoughts']#, 'notes']
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
    all_thoughts = []
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

        # is_done break used to be here, moved down so that thoughts can be had even if no stdin
        

        #notes_summary = ''.join(['- ' + note + '\n' for note in all_notes])
        thoughts_summary = '\n'.join(['- ' + thought for thought in all_thoughts])
        
        resp = run_chain.run(plan=run_plan, thoughts=thoughts_summary, history=summarize_history(history)) #stdout=stdout, stderr=stderr)
        if 'stdin' in resp:
            stdin = resp['stdin']

            # LLM passing blank indicates no stdin
            if stdin == '':
                stdin = None
        else:
            stdin = None
        if 'terminate' in resp:
            terminate = resp['terminate']
        else:
            terminate = False
        
        print('stdin:', stdin)
        if stdin != None:
            history.append(('stdin', stdin))
        
        if 'notes' in resp:
            notes = resp['notes']
            print('notes:', notes)
            all_notes.append(notes)
        
        thoughts = resp['thoughts']
        print('thoughts:', thoughts)
        all_thoughts.append(thoughts)

        # moved down so that thoughts can be had even if no stdin,
        # especially important if we get stderr immediately
        if is_done:
            print('Program is done running.')
            break

        if terminate:
            # LLM thinks the program is stuck
            print('Termination commenced by LLM.')
            runner.terminate()
            #self.process.
            break
        #print('notes:', notes)

        # stdin = input('stdin: ')
        # if stdin == '':
        #     stdin = None
    runner.close()

    # for debug
    import json
    with open('logs/run.json', 'w') as f:
        json.dump({
            'history': history,
            'thoughts': all_thoughts
        }, f, indent=4)

    return all_thoughts#all_notes
