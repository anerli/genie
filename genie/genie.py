from pydantic import BaseModel, Field
from enum import Enum
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate
from langchain.chains.openai_functions import create_structured_output_chain, create_openai_fn_chain, convert_to_openai_function

prelude_template='''
You are an AI software engineer capable of reading/editing as well as running/testing programs.
You are trying to create the following software:

{goal_description}

If you do not immediately know how to create the software, create and experiment in what you think might be a step in the right direction, and test and iterate from there.
'''[1:-1]

class Operation(Enum):
    WRITE_FILE = 'WriteFile'
    #READ_FILE = 'ReadFile'
    #NEW_FILE = 'NewFile'
    EDIT_FILE = 'EditFile'

class GenieCommand(BaseModel):
    op: Operation = Field(..., description='The type of action to perform')
    #command: str = Field(..., description='shell code to run')
    #msg: str
    #op:


'''
Alt: provide multiple OpenAI functions and tell it that it must use one and hope for the best, lol.
in the past though GPT can get confused and think its still in a chat conversation.
'''

goal_description='Write a simple snake game in Python.'

# TODO: redo as chain
prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(prelude_template)
    #('system', prelude_template.format(goal_description=goal_description))
])

llm = ChatOpenAI(temperature=0.1)
#print(convert_to_openai_function(GenieCommand))
#chain = create_structured_output_chain(GenieCommand, llm, prompt, verbose=True)#, output_parser=lambda x: print('POTATO:', x))

#C:\Users\anerli\Sync\Code\Python\lib\langchain\libs\langchain

# Method 1 of using schema directly

# chain = create_structured_output_chain({
#     'type': 'object',
#     'properties': {
#         'op': {
#             'type': 'string',
#             'enum': ['WRITE_FILE', 'LIST_FILES'],
#             'description': 'Type of operation to perform'
#         }
#     },
#     'required': ['op']
# }, llm, prompt, verbose=True)

# What do we need to do to fix the generated one?
chain = create_structured_output_chain({
    "title": "_OutputFormatter",
    "description": "Output formatter. Should always be used to format your response to the user.",
    "type": "object",
    "properties": {
        "output": { "$ref": "#/definitions/GenieCommand" }
    },
    "required": ["output"],
    "definitions": {
        "Operation": {
            "title": "Operation",
            "description": "An enumeration.",
            "enum": ["WriteFile", "EditFile"]
        },
        "GenieCommand": {
            "title": "GenieCommand",
            "type": "object",
            "properties": {
                "op": {
                    "description": "The type of action to perform",
                    "allOf": [{ "$ref": "#/definitions/Operation" }]
                }
            },
            "required": ["op"]
        }
    }
}, llm, prompt, verbose=True)


'''
Can we debug the schema generated for the Pydantic model?
Yes! openai_functions.convert_to_openai_function

Hm but not public. Time to clone langchain & install in edit mode, ig
'''


# chain = create_openai_fn_chain([ # create_openai_fn_chain
#     {
#         'name': 'Command',
#         'description': 'Perform a command on the system',
#         'parameters': {
#             'type': 'object',
#             'properties': {
#                 'op': {
#                     'type': 'string',
#                     'enum': ['WRITE_FILE', 'LIST_FILES'],
#                     'description': 'Type of operation to perform'
#                 }
#             },
#             'required': ['op']
#         }
#         # "description": "Get the current weather in a given location",
#         # "parameters": {
#         #     "type": "object",
#         #     "properties": {
#         #         "location": {
#         #             "type": "string",
#         #             "description": "The city and state, e.g. San Francisco, CA",
#         #         },
#         #         "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
#         #     },
#         #     "required": ["location"],
#         # },
#     }
# ], llm, prompt, verbose=True)
output = chain.run(goal_description=goal_description)

print(output)