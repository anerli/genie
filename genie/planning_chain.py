from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate
from langchain.chains.openai_functions import create_structured_output_chain
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

def generate_plan(project_goal, workspace, last_run_report):
    return planning_chain.run(
        goal=project_goal,
        workspace_desc=describe_workspace(workspace),
        run_report=last_run_report
    )
