from planning_chain import generate_plan
from engineering_chain import get_engineering_chain, get_engineering_prompt
from run_chain import run_and_reflect

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
        plan = generate_plan(goal, workspace, run_report)#planning_chain.run(goal=goal, workspace_desc=describe_workspace(workspace), run_report=run_report)
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
