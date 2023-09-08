from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate
from langchain.chains.openai_functions import create_structured_output_chain

import os
import subprocess

#from runner import create_workspace_python_runner
from run_chain import run_and_reflect
from engineering_chain import get_engineering_chain, get_engineering_prompt
from workspace import describe_workspace

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
        'is_finished': {
            'type': 'boolean',
            'description': 'If no further changes are needed, set to true'#'Whether the project is finished or not. Set to true once the run report shows the goal is accomplished successfully.'
        }
    },
    'required': ['write_filepath', 'write_plan', 'run_filepath', 'run_plan', 'is_finished']
}, llm, planning_prompt, verbose=True)

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
    import sys

    workspace = './test_workspace'
    goal = 'Write a program that finds the first 100 prime numbers.'

    if len(sys.argv) == 3:
        workspace = sys.argv[1]
        goal = sys.argv[2]
    
    run_report='[project has not yet been run]'
    while True:
        plan = planning_chain.run(goal=goal, workspace_desc=describe_workspace(workspace), run_report=run_report)
        print('PLAN:')
        print(plan)
        
        time.sleep(5)

        if plan['is_finished']:
            print('Manager has indicated that the project is finished!')
            break

        with open('logs/plan.json', 'w') as f:
            json.dump(plan, f, indent=4)
        
        engineering_chain = get_engineering_chain()#get_engineering_chain(workspace, plan['write_filepath'], goal, plan['write_plan'])
        action = engineering_chain.run(system_prompt=get_engineering_prompt(workspace, plan['write_filepath'], goal, plan['write_plan']))#goal=goal, plan=plan['write_plan'], filepath=plan['write_filepath'])
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
