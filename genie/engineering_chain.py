from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate
from langchain.chains.openai_functions import create_structured_output_chain
from langchain.schema import SystemMessage
import os

llm = ChatOpenAI(temperature=0.0, model='gpt-3.5-turbo')

ENGINEERING_TEMPLATE = '''
You are a Software Engineer, responsible for executing planned actions.
You are trying to create the following software:
```
{goal}
```

{file_desc}

In this file, you are to:
```
{plan}
```

Pay attention to the file extension and write the appropriate code.
'''[1:-1]

def get_engineering_prompt(workspace, filepath, goal, plan):
    full_path = os.path.join(workspace, filepath)

    if not os.path.exists(full_path):
        file_desc = f'The Engineering Manager AI has planned for you to create the file {filepath}, which does not yet exist.'
    else:
        file_desc = f'The Engineering Manager AI has planned for you to create the file {filepath}, which currently has this content:\n```\n'
        with open(full_path, 'r') as f:
            file_desc += f.read()
        file_desc += '\n```'

    # Hacky, got to be a better way, prob?
    # Yeah not really necessary to do it both ways here, but we do need it to be dynamic in custom ways so maybe we don't use
    # langchains params at all.
    engineering_prompt = ENGINEERING_TEMPLATE.format(
        goal=goal,#'{goal}',
        plan=plan,#'{plan}',
        file_desc=file_desc
    )
    return engineering_prompt
    # could dynamically say edit/create based on file existence

def get_engineering_chain():
    engineering_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template('{system_prompt}')#engineering_template)]
        # using template causes issues if program content contains brackets
        #SystemMessage(content=engineering_template)
    ])

    engineering_chain = create_structured_output_chain({
        'type': 'object',
        'properties': {
            'file_content': {
                'type': 'string',
                'description': 'Content to write to the given file. Implement all planned code, do not use placeholders.'
            }
        },
        'required': ['write_filepath', 'write_plan', 'run_plan']
    }, llm, engineering_prompt, verbose=True)

    return engineering_chain