'''
a module of logs saving and backuping
'''

import os
import huggingface_hub as hf
from apscheduler.schedulers.background import BackgroundScheduler
import datasets as ds
from threading import Thread
from zoneinfo import ZoneInfo
import json
from md5 import md5
from tqdm import trange
from date_utils import beijing,dateparser
import git_utils

class LogDS:
    '''
    params:
        backup_dir: a directory in cwd to store json file of log data
        repo_url: the remote repo_url of the dataset
        backup_interval: interval seconds to backup a time, default to 60s
    '''

    def __init__(self,backup_dir:str,repo_url:str,backup_interval:int=60):
        self.__backup_dir=backup_dir
        self.__repo_url=repo_url
        self.__backup_interval=backup_interval

        self.__repo=None
        self.__scheduler = BackgroundScheduler()
        self.__buffer=dict[str,ds.Dataset]()
        ds.disable_progress_bar()

    def __synchronize(self):
        '''synchronize logs in remote repo to local'''
        if not self.__repo:
            if not self.__clonerepo():
                return False
        HEAD_before=self.__repo.git_head_hash()
        if not self.__pullrepo():
            ######################
            # reset repo to HEAD^
            # wait for next sync
            ######################
            print("Trying to reset repo to HEAD^ hard")
            if git_utils.git_reset(rootdir=self.__backup_dir,commitid="HEAD^",hard=True):
                print("Success")
            else:
                print("Failed")
            return False
        HEAD_after=self.__repo.git_head_hash()
        if HEAD_after==HEAD_before:
            return True
        increasement=git_utils.git_diff_content(rootdir=self.__backup_dir,
                                                beforeId=HEAD_before,
                                                afterId=HEAD_after)
        if increasement==None:
            return False
        if not increasement:
            print("no increasement")
        self.__load_increasement(increasement)
        return True

    def __clonerepo(self):
        '''clone remote dataset to local'''
        print("cloning: start")
        try:
            hf_token=os.environ.get("db_token")
            self.__repo = hf.Repository(
                local_dir=self.__backup_dir,
                repo_type="dataset",
                clone_from=self.__repo_url,
                use_auth_token=hf_token,
            )
            print("cloning: done")
            return True
        except Exception as e:
            self.__repo = None
            print(f"Error {type(e)} occurred in __clonerepo: {e}")
            print("cloning: failed")
            return False

    def __pullrepo(self):
        ''' pull remote dataset to local'''
        print("pulling: start")
        try:
            self.__repo.git_pull()
            print("pulling: done")
            return True
        except Exception as e:
            print(f"Error {type(e)} occurred in __pullrepo: {e}")
            if str(e).startswith('Remote "origin" does not support the Git LFS locking API'):
                git_utils.git_config(rootdir=self.__backup_dir,
                                     key="lfs.https://hf.co/datasets/hubei-hunan/logs.git/info/lfs.locksverify",
                                     value="false")
            print("pulling: failed")
            return False

    def __load_increasement(self,increasement:dict[str,list[str]]):
        '''load increasement that will be changed by buffer'''
        print("loading increasement: start")
        filecount=len(increasement)
        for i in trange(filecount):
            filename,lines=increasement.popitem()
            filepath=os.sep.join([self.__backup_dir,filename])
            if filepath in self.__buffer:
                for line in lines:
                   self.addlog(json.loads(line)) 
        print("loading increasement: done")
        

    def __processlog(self,log:dict):
        '''transfer values in log to string format'''
        for key,value in log.items():
            log[key]=str(value)
        return log

    def addlog(self,log:dict):
        '''add one log'''
        log=self.__processlog(log)
        if "timestamp" in log:
            date=dateparser(log['timestamp'])
            if not date:
                date=beijing()
        else:
            date=beijing()
        year=date.year.__str__()
        month=date.month.__str__()
        day=date.day.__str__()
        filename=md5(log)[:2]+".json"
        filepath=os.sep.join([self.__backup_dir,year,month,day,filename])
        if filepath not in self.__buffer:
            if os.path.exists(filepath):
                self.__buffer[filepath]=ds.Dataset.from_json(filepath)
            else:
                self.__buffer[filepath]=ds.Dataset.from_dict({})
        self.__buffer[filepath]=self.__buffer[filepath].add_item(log)
    
    def __backup(self):
        if not len(self.__buffer):
            return True
        if self.__thread_synchronize.is_alive():
            return True
        if not self.__synchronize():
            print("[backup]: synchronizing failed")
            return False
        for filepath,dataset in self.__buffer.items():
            dataset.to_json(filepath)
        if not self.__pushrepo():
            print("[backup]: pushing failed")
            ######################
            # reset repo to HEAD^
            # wait for next sync
            ######################
            print("Trying to reset repo to HEAD^ hard")
            if git_utils.git_reset(rootdir=self.__backup_dir,commitid="HEAD^",hard=True):
                print("Success")
            else:
                print("Failed")
            return False
        self.__buffer.clear()
        print(f"[backup]: succeed at {beijing()}")
        return True

    def __pushrepo(self):
        try:
            self.__repo.push_to_hub(commit_message=f"Updated at {beijing()}")
            return True
        except Exception as e:
            print(f"Error {type(e)} occurred in pushrepo: {e}")
            if str(e).startswith('Remote "origin" does not support the Git LFS locking API'):
                git_utils.git_config(rootdir=self.__backup_dir,
                                     key="lfs.https://hf.co/datasets/hubei-hunan/logs.git/info/lfs.locksverify",
                                     value="false",
                                     domain=None)
            return False

    def start_synchronize(self):
        """start a thread to synchronize at once, 
        and a scheduler to backup periodically"""
        self.__thread_synchronize=Thread(target=self.__synchronize,
                                         name="synchronize")
        self.__thread_synchronize.start()

        self.__scheduler.add_job(func=self.__backup, 
                                 trigger="interval", 
                                 seconds=self.__backup_interval)
        self.__scheduler.start()
