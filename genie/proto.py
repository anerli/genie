from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate
from langchain.chains.openai_functions import create_structured_output_chain

import os
import subprocess

#from runner import create_workspace_python_runner
from run_chain import run_and_reflect

llm = ChatOpenAI(temperature=0.0, model='gpt-3.5-turbo')

planning_template = '''
You are a Software Engineering Manager, responsible for planning the actions of an AI Software Engineer.
You are trying to create the following software:
```
{goal}
```
Here are all the files in the project so far:
{workspace_desc}

The report from the last time the project was run:
{run_report}

Plan which file to write to (an existing file, or a new one) and what needs to be done in that file.
After this is done, the program will be run. Plan what to check for and take notes on when the program is being run.
'''[1:-1]

planning_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(planning_template)
])

planning_chain = create_structured_output_chain({
    'type': 'object',
    'properties': {
        'write_filepath': {
            'type': 'string',
            'description': 'Relative path to the file that the engineer should create or edit'
        },
        'write_plan': {
            'type': 'string',
            'description': 'What the engineer should do with the specified file'
        },
        'run_filepath': {
            'type': 'string',
            'description': 'What file the engineer should run'
        },
        'run_plan': {
            'type': 'string',
            'description': 'What the engineer should look for, or take notes on, when running the program'
        },
    },
    'required': ['write_filepath', 'write_plan', 'run_filepath', 'run_plan']
}, llm, planning_prompt, verbose=True)

engineering_template = '''
You are a Software Engineer, responsible for executing planned actions.
You are trying to create the following software:
```
{goal}
```

The Engineering Manager AI has planned for you to create the file {filepath}, which does not yet exist. In this file, you are to:
```
{plan}
```

Pay attention to the file extension and write the appropriate code.
'''[1:-1]
# could dynamically say edit/create based on file existence

engineering_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(engineering_template)
])

engineering_chain = create_structured_output_chain({
    'type': 'object',
    'properties': {
        'file_content': {
            'type': 'string',
            'description': 'Content to write to the given file'
        }
    },
    'required': ['write_filepath', 'write_plan', 'run_plan']
}, llm, engineering_prompt, verbose=True)

def describe_workspace(workspace):
    desc = ''
    for root, _dirs, files in os.walk(workspace):
        for name in files:
            path = os.path.join(root, name)
            trimmed_path = os.path.relpath(path, workspace).replace('\\', '/')
            #print(trimmed_path)
            desc += trimmed_path + '\n```'
            with open(path, 'r') as f:
                desc += f.read()
            desc += '\n```\n\n'
        # for name in dirs:
        #     print(os.path.join(root, name))
    if desc == '':
        desc = '(no files yet)'
    return desc


def execute_action(workspace, filepath, content):
    # Execute engineering action in the workspace
    with open(workspace + '/' + filepath, 'w') as f:
        f.write(content)

# def run_python_project(workspace, run_filepath):
#     from runner import run_python_file

#     run_python_file(os.path.join(workspace, run_filepath))

if __name__ == '__main__':
    import json
    import time

    workspace = './test_workspace'
    goal = 'Write a program that finds the first 100 prime numbers.'
    
    run_report='[project has not yet been run]'
    while True:
        plan = planning_chain.run(goal=goal, workspace_desc=describe_workspace(workspace), run_report=run_report)
        print('PLAN:')
        print(plan)

        time.sleep(5)

        with open('logs/plan.json', 'w') as f:
            json.dump(plan, f, indent=4)
        
        action = engineering_chain.run(goal=goal, plan=plan['write_plan'], filepath=plan['write_filepath'])
        print('ACTION:')
        print(action)

        time.sleep(5)

        with open('logs/action.json', 'w') as f:
            json.dump(action, f, indent=4)

        execute_action(workspace, plan['write_filepath'], action['file_content'])

        thoughts = run_and_reflect(workspace, plan['run_filepath'], plan['run_plan'])
        run_report = '\n'.join(['- ' + thought for thought in thoughts])

        print('RUN REPORT (thoughts):')
        print(run_report)

        time.sleep(5)
