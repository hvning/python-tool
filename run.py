'''
This .py is used for checking GPUs resources to run your code. And you can set the python program
that is ready to run in setting. 
Warm tip :) It don't highly recommend to set the checking frenquence paramer too large
'''

import os
import time
import pynvml
from terminaltables import AsciiTable  

# declare which gpu device to use
cuda_device = '1'

def check_mem(cuda_device):
    devices_info = os.popen('"/usr/bin/nvidia-smi" --query-gpu=memory.total,memory.used --format=csv,nounits,noheader').read().strip().split("\n")
    total, used = devices_info[int(cuda_device)].split(',')
    return total,used

#occupy the gpu memory 
def occumpy_mem(cuda_device):
    total, used = check_mem(cuda_device)
    total = int(total)
    used = int(used)
    max_mem = int(total * 0.9)
    block_mem = max_mem - used
    x = torch.cuda.FloatTensor(256,1024,block_mem)
    del x
    
def check(id):

    pynvml.nvmlInit()

    handle = pynvml.nvmlDeviceGetHandleByIndex(id)
    meminfo = pynvml.nvmlDeviceGetMemoryInfo(handle)
    total = (meminfo.total/1024/1024)
    free = (meminfo.free/1024/1024)

    return total,free

def create_table(id_list):
    table_data = [['GPU ID', '  Total/Free']]
    id_num = len(id_list)
    infor = []
    for i in id_list:
        infor.insert(i,check(i))
        infor_dis = str(infor[i][0]) +' MB / '+str(infor[i][1]) + ' MB'
        table_data.append([str(i),infor_dis])
    return infor,table_data

def prog_to_run(cmd_list):
   
    infor,table_data = create_table(cmd_dict['gpu_list'])
    gpu_ready_count = 0

    table_data[0].append('Ready To Run')   
    table_data[0].append('Memory') 

    #check every gpu needed 
    for index,gpu_id in enumerate(cmd_list['id']):

        memory_free = infor[gpu_ready_count][1]
        #add the information to the target GPU
        table_data[gpu_id+1].append(cmd_list['program'])
        table_data[gpu_id+1].append(cmd_list['memory'][index])

        if memory_free > cmd_list['memory'][index]: 
            gpu_ready_count+=1

    if gpu_ready_count == len(cmd_list['id']):
        # print('run the code')
        os.system(cmd_list['program'])
        return True
    else:
        print('Only %d '%gpu_ready_count,'GPU(S) has/have been ready! Wait for moment')  

    table = AsciiTable(table_data)
    print(table.table) 
    return False
clear = lambda: os.system('clear')      # or os.system('clear') for Unix
if __name__ == '__main__':
   
    cmd_dict = {
        'gpu_list':[0,1,2,3,4,5,6,7],
        'program':'python ./helloworld.py',
        'id':[1,2,3,5],
        'memory':[1000,1000,1000,20000],
        'check frequence':2     #uint is second
    }

    while True:
        clear()
        if(prog_to_run(cmd_dict)):
            print('.py has been running out')
            break
        else:
            print('checking continuedly')
            time.sleep(cmd_dict['check frequence'])
    