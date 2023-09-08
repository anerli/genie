import os
import fnmatch

IGNORE_FILE_NAME = '.genieignore'

def read_ignore(file_path):
    with open(file_path, 'r') as f:
        # Strip out comments, leading/trailing whitespaces, and empty lines
        lines = [line.strip() for line in f.readlines() if not line.strip().startswith('#') and line.strip() != '']
    lines.append(IGNORE_FILE_NAME)
    return lines

def is_ignored(path, patterns):
    for pattern in patterns:
        if fnmatch.fnmatch(path, pattern):
            return True
    return False

def walk_and_skip_ignored(workspace):
    ignore_patterns = read_ignore(os.path.join(workspace, IGNORE_FILE_NAME))
    for dirpath, dirnames, filenames in os.walk(workspace):
        # Modify dirnames in-place to remove ignored directories
        dirnames[:] = [d for d in dirnames if not is_ignored(os.path.relpath(os.path.join(dirpath, d), workspace), ignore_patterns)]

        for filename in filenames:
            if not is_ignored(os.path.relpath(os.path.join(dirpath, filename), workspace), ignore_patterns):
                yield os.path.join(dirpath, filename)

def describe_workspace(workspace):
    desc = ''
    #for root, _dirs, files in os.walk(workspace):
    for file_path in walk_and_skip_ignored(workspace):
        #print('describing:', file_path)
        #for name in files:
            #path = os.path.join(root, name)
        unix_path = os.path.relpath(file_path, workspace).replace('\\', '/')
        desc += unix_path + '\n```\n'
        with open(file_path, 'r') as f:
            desc += f.read()
        desc += '\n```\n\n'
    if desc == '':
        desc = '(no files yet)'
    return desc

if __name__ == '__main__':
    print(describe_workspace('./testing/poo'))