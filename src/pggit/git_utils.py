'''a module implemented with subprocess module,
providing some tools to manage repository
'''

import os
import subprocess

def is_repo(path:str):
    '''check if the path is a root directory of a repository'''
    try:
        if not os.path.exists(path):
            print("Error occurred in is_repo: No such directory")
            return False
        root=subprocess.check_output(["git","-C",path,"rev-parse","--show-toplevel"]).decode('utf-8').strip('\n')
        if os.path.samefile(root,path):
            return True
    except Exception as e:
        print(f"Error {type(e)} occurred in is_repo: {e}")
    return False

def git_reset(rootdir:str,commitid:str="HEAD",hard:bool=False):
    '''execute command 'git reset --hard commitid', rollback to the version in commitid hardly
    
    params:
        rootdir: the root directory of a repository
        commitid: a existed commit id
        hard: whether delete changes staged and in cwd
    '''
    if not os.path.exists(rootdir):
        print("Error occurred in git_reset_to_HEAD: rootdir not exists")
        return False
    if not is_repo(rootdir):
        print(f"Error occurred in git_reset_to_HEAD: there is not a repository in {rootdir}")
        return False
    
    cwd=os.getcwd()
    try:
        os.chdir(rootdir)
        # stage all before reset
        subprocess.call(["git","add","."])
        command=["git","reset"]
        if hard:
            command.append("--hard")
        command.append(commitid)
        subprocess.call(command)
        os.chdir(cwd)
        return True
    except Exception as e:
        print(f"Error {type(e)} occurred in git_reset_to_HEAD: {e}")
        os.chdir(cwd)
        return False


    
def git_diff_content(rootdir:str,beforeId:str,afterId:str):
    '''get files content changed between two committing, 
    changes are from beforeId to afterId

    params:
        rootdir: the root directory of a repository
        beforeId: the commit id earlier committed
        afterId: the commit id later commidtted
    return:
        if succeed, return a dict with filename as key and list of changed lines as value\n
            return a empty dict if nothing changed
        if failed, return None
    '''
    if not os.path.exists(rootdir):
        print("Error occurred in git_diff_content: rootdir not exists")
        return None
    if not is_repo(rootdir):
        print(f"Error occurred in git_diff_content: there is not a repository in {rootdir}")
        return None
        
    cwd=os.getcwd()
    try:
        os.chdir(rootdir)
        output=subprocess.check_output(["git","diff",beforeId,afterId]).decode('utf-8')
        os.chdir(cwd)
        lines=output.replace("/",os.sep).splitlines()
        result=dict[str,list[str]]()
        filename=None
        for line in lines:
            if line.startswith("+"):
                if line.startswith("+++"):
                    filename=line[6:]
                    result[filename]=[]
                else:
                    result[filename].append(line[1:])
        return result
    except Exception as e:
        print(f"Error {type(e)} occurred in git_diff_content: {e}")
        os.chdir(cwd)
        return None
    
def git_current_commitid(rootdir:str):
    '''get the commit id that HEAD pointed'''
    
    if not os.path.exists(rootdir):
        print("Error occurred in git_current_commitid: rootdir not exists")
        return None
    if not is_repo(rootdir):
        print(f"Error occurred in git_current_commitid: there is not a repository in {rootdir}")
        return None
    cwd=os.getcwd()
    try:
        os.chdir(rootdir)
        output=subprocess.check_output(["git","rev-parse","HEAD"]).decode('utf-8')
        os.chdir(cwd)
        return output
    except Exception as e:
        print(f"Error {type(e)} occurred in git_current_commitid: {e}")
        os.chdir(cwd)
        return None

def git_config(rootdir:str,key:str,value:str,domain="--global"):
    '''set a configure value, default global'''
    if not os.path.exists(rootdir):
        print("Error occurred in git_current_commitid: rootdir not exists")
        return False
    if not is_repo(rootdir):
        print(f"Error occurred in git_current_commitid: there is not a repository in {rootdir}")
        return False
    cwd=os.getcwd()
    try:
        os.chdir(rootdir)
        command=['git','config']
        if domain:
            command+=[domain]
        command+=[key]
        command+=[value]
        subprocess.call(command)
        os.chdir(cwd)
        return True
    except Exception as e:
        print(f"Error {type(e)} occurred in git_current_commitid: {e}")
        os.chdir(cwd)
        return False



if __name__=="__main__":
    print(is_repo("123"))
    # print("testing git_reset_to_HEAD")
    # rootdir='test'
    # commitid="0a72079cb7f308e86a3b5c47086965140503c1e1"
    # git_reset(rootdir=rootdir,commitid="HEAD^",hard=True)
    # afterid="00b3d96"
    # beforeid="00b3d96"
    # contents=git_diff_content(rootdir="logs",beforeId=beforeid,afterId=afterid)
    # print(contents)
