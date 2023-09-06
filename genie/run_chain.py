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

stdout:
```
{stdout}
```

stderr:
```
{stderr}
```
'''[1:-1]

run_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(run_template)
])

run_chain = create_structured_output_chain({
    'type': 'object',
    'properties': {
        'stdin': {
            'type': 'string',
            'description': 'Text to pass to stdin. If not provided, nothing will be passed.'
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

def run_and_reflect(workspace, run_filepath, run_plan):
    print('Running and reflecting!')
    all_notes = []
    
    runner = create_workspace_python_runner(workspace, run_filepath)

    runner.start()
    is_done = False
    stdin = None
    #last_stdout = None
    while True:
        stdout, stderr, is_done = runner.next(stdin, True)

        print('stdout:', stdout)
        print('stderr:', stderr)

        # If stdout is blank, it may have been because LLM did not provide input when it should have?
        # if stdout == '' and last_stdout:
        #     stdout = last_stdout
        # last_stdout = stdout

        
        if is_done:
            break
        
        resp = run_chain.run(plan=run_plan, stdout=stdout, stderr=stderr)
        if 'stdin' in resp:
            stdin = resp['stdin']
        else:
            stdin = None
        if 'terminate' in resp:
            terminate = resp['stdin']
        else:
            terminate = False
        
        print('stdin:', stdin)
        if terminate:
            # LLM thinks the program is stuck
            print('Termination commenced by LLM')
            break
        notes = resp['notes']
        print('notes:', notes)
        all_notes.append(notes)
        #print('notes:', notes)

        # stdin = input('stdin: ')
        # if stdin == '':
        #     stdin = None
    runner.close()
    return all_notes
