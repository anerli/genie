from planning_chain import generate_plan
from engineering_chain import get_engineering_chain, get_engineering_prompt
from run_chain import run_and_reflect
import json
import time

def execute_action(workspace, filepath, content):
    # Execute engineering action in the workspace
    with open(workspace + '/' + filepath, 'w') as f:
        f.write(content)

class Mancer:
    def __init__(self, project_goal, workspace):
        # Project Goal
        self.project_goal = project_goal
        # Workspace
        self.workspace= workspace
        # Run Report
        self.run_report = '(project has yet to be run)'
        self.is_finished = False
    
    def cycle(self):
        plan = generate_plan(self.project_goal, self.workspace, self.run_report)
        print('PLAN:')
        print(plan)
        
        time.sleep(5)

        if plan['is_finished']:
            print('Manager has indicated that the project is finished!')
            self.is_finished = True
            return

        with open('logs/plan.json', 'w') as f:
            json.dump(plan, f, indent=4)
        
        engineering_chain = get_engineering_chain()
        action = engineering_chain.run(system_prompt=get_engineering_prompt(self.workspace, plan['write_filepath'], self.project_goal, plan['write_plan']))
        print('ACTION:')
        print(action)

        time.sleep(5)

        with open('logs/action.json', 'w') as f:
            json.dump(action, f, indent=4)

        execute_action(self.workspace, plan['write_filepath'], action['file_content'])

        thoughts = run_and_reflect(self.workspace, plan['run_filepath'], plan['run_plan'])
        run_report = '\n'.join(['- ' + thought for thought in thoughts])

        print('RUN REPORT (thoughts):')
        print(run_report)

        time.sleep(5)
    
    def cycle_until_finished(self):
        while not self.is_finished:
            self.cycle()