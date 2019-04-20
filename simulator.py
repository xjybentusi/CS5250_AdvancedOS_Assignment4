'''
CS5250 Assignment 4, Scheduling policies simulator
Sample skeleton program
Input file:
    input.txt
Output files:
    FCFS.txt
    RR.txt
    SRTF.txt
    SJF.txt
'''
import sys
import copy
import operator

input_file = 'input.txt'

class Process:
    last_scheduled_time = 0
    def __init__(self, id, arrive_time, burst_time):
        self.id = id
        self.arrive_time = arrive_time
        self.burst_time = burst_time
        self.orig_burst_time = copy.deepcopy(burst_time) #used in rr
        self.last_preemptive_time = -10 #used to check if the process is the last process scheduled
        self.prediction = 0
    #for printing purpose
    def __repr__(self):
        return ('[id %d : arrival_time %d,  burst_time %d]'%(self.id, self.arrive_time, self.burst_time))

def FCFS_scheduling(process_list):
    #store the (switching time, proccess_id) pair
    schedule = []
    current_time = 0
    waiting_time = 0
    for process in process_list:
        if(current_time < process.arrive_time):
            current_time = process.arrive_time
        schedule.append((current_time,process.id))
        waiting_time = waiting_time + (current_time - process.arrive_time)
        current_time = current_time + process.burst_time
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

#Input: process_list, time_quantum (Positive Integer)
#Output_1 : Schedule list contains pairs of (time_stamp, proccess_id) indicating the time switching to that proccess_id
#Output_2 : Average Waiting Time
#Assume: new process have higher priority than pre-emptive task if two are appended to process_Q at the same time
#Assume: old process id =1 does not join new process id = 1 even if two are neighbors in process_Q
def RR_scheduling(process_list, time_quantum ):
    process_list2 = copy.deepcopy(process_list)
    current_time = 0
    process_Q = []
    schedule = []
    waiting_time = 0
    while True:
        schedule.append('current time in the begining is %d'%(current_time))
        for process in list(process_list2):
            if (process.arrive_time <= current_time):
                process_Q.append(process)
                #schedule.append('process id %d added to Q at time %d'%(process.id,current_time))
                process_list2.remove(process)
        if (len(process_Q) != 0):
            for process in process_Q:
                schedule.append('Process Q contains %d %d'%(process.id, process.burst_time))
            process_ = process_Q.pop(0)
            if (process_.last_preemptive_time != current_time - time_quantum): #the process_ is scheduled in the last round
                schedule.append((current_time,process_.id))
            if (process_.burst_time > time_quantum):
                process_.burst_time = process_.burst_time - time_quantum
                current_time = current_time + time_quantum
                process_.last_preemptive_time = current_time
                schedule.append('current time is %d'%(current_time))
                for process in list(process_list2):
                    #schedule.append('process in process_list2 %d %d'%(process.id,process.arrive_time))
                    if (process.arrive_time <= current_time):
                        process_Q.append(process)
                        schedule.append('process id %d added to Q at time %d'%(process.id,current_time))
                        process_list2.remove(process)
                process_Q.append(process_)
            else: #process_ end here
                schedule.append('process %d end here'%(process_.id))
                delta_time = process_.burst_time
                current_time = current_time + delta_time
                waiting_time = (current_time - process_.arrive_time - process_.orig_burst_time) + waiting_time
        if (len(process_Q) == 0 and len(process_list2) == 0 ):
            schedule.append('RR ended')
            break
        if (len(process_Q) == 0 and len(process_list2) != 0 ):
            schedule.append('RR wait for the next process arrival')
            current_time = process_list2[0].arrive_time
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

def SRTF_scheduling(process_list):
    process_list2 = copy.deepcopy(process_list)
    current_time = 0
    process_Q = []
    schedule = []
    waiting_time = 0
    duration =0
    while True:
        schedule.append('current time in the begining is %d'%(current_time))
        if (len(process_list2)==0):
            process_Q.sort(key=operator.attrgetter('burst_time'))
            duration=process_Q[0].burst_time
        for process in list(process_list2):
            if (process.arrive_time <= current_time):
                process_Q.append(process)
                #schedule.append('process id %d added to Q at time %d'%(process.id,current_time))
                process_list2.remove(process)
            else:
                duration=process.arrive_time-current_time #time to devoted to one process before next check
                break
        if (len(process_Q) != 0):
            process_Q.sort(key=operator.attrgetter('burst_time'))
            for process in process_Q:
                schedule.append('Process Q contains %d %d'%(process.id, process.burst_time))
            process_ = process_Q.pop(0)
            schedule.append('duration is %d'%(duration))
            if (process_.last_preemptive_time != current_time): #the process_ is scheduled in the last round
                schedule.append((current_time,process_.id))
            if (process_.burst_time > duration):
                process_.burst_time = process_.burst_time - duration
                current_time = current_time + duration
                process_.last_preemptive_time = current_time
                process_Q.append(process_)
            else: #process_ end here
                schedule.append('process %d end here'%(process_.id))
                delta_time = process_.burst_time
                current_time = current_time + delta_time
                waiting_time = (current_time - process_.arrive_time - process_.orig_burst_time) + waiting_time
        if (len(process_Q) == 0 and len(process_list2) == 0 ):
            schedule.append('RR ended')
            break
        if (len(process_Q) == 0 and len(process_list2) != 0 ):
            schedule.append('RR wait for the next process arrival')
            current_time = process_list2[0].arrive_time
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

def SJF_scheduling(process_list, alpha):
#when 2 processes have the same guess, the one with earlier arrival time get scheduled first
    process_list2 = copy.deepcopy(process_list)
    current_time = 0
    process_Q = []
    schedule = []
    waiting_time = 0
    record_table = [[0,0,0],[1,0,0],[2,0,0],[3,0,0]] #id, actual, last prediction
    def get_prediction(record_table, id):
        if (record_table[id][1] == 0):
            return 5
        else:
            schedule.append('prediction is %.2f'%((float)(alpha*record_table[id][1]+(1-alpha)*record_table[id][2])))
            return float(float(alpha)*float(record_table[id][1])+float((1-alpha))*float(record_table[id][2]))
    def update_record_table(process_):
        record_table[process_.id][1]=process_.burst_time
        record_table[process_.id][2]=process_.prediction
    while True:
        schedule.append('current time in the begining is %d'%(current_time))
        for process in list(process_list2):
            if (process.arrive_time <= current_time):
                process.prediction = get_prediction(record_table,process.id)
                process_Q.append(process)
                #schedule.append('process id %d added to Q at time %d'%(process.id,current_time))
                process_list2.remove(process)
        if (len(process_Q) == 0 and len(process_list2) == 0 ):
            schedule.append('RR ended')
            break
        if (len(process_Q) == 0 and len(process_list2) != 0 ):
            schedule.append('RR wait for the next process arrival')
            current_time = process_list2[0].arrive_time
        if (len(process_Q) != 0):
            process_Q.sort(key=operator.attrgetter('prediction'))
            for process in process_Q:
                schedule.append('Process Q contains %d %d %.2f'%(process.id, process.burst_time, process.prediction))
            process_ = process_Q.pop(0)
            update_record_table(process_)
            if (process_.last_preemptive_time != current_time): #the process_ is scheduled in the last round
                schedule.append((current_time,process_.id))
            schedule.append('process %d end here'%(process_.id))
            delta_time = process_.burst_time
            current_time = current_time + delta_time
            waiting_time = (current_time - process_.arrive_time - process_.orig_burst_time) + waiting_time
        
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

def read_input():
    result = []
    with open(input_file) as f:
        for line in f:
            array = line.split()
            if (len(array)!= 3):
                print ("wrong input format")
                exit()
            result.append(Process(int(array[0]),int(array[1]),int(array[2])))
    return result
def write_output(file_name, schedule, avg_waiting_time):
    with open(file_name,'w') as f:
        for item in schedule:
            f.write(str(item) + '\n')
        f.write('average waiting time %.2f \n'%(avg_waiting_time))


def main(argv):
    process_list = read_input()
    print ("printing input ----")
    for process in process_list:
        print (process)
    print ("simulating FCFS ----")
    FCFS_schedule, FCFS_avg_waiting_time =  FCFS_scheduling(process_list)
    write_output('FCFS.txt', FCFS_schedule, FCFS_avg_waiting_time )
    print ("simulating RR ----")
    RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list,time_quantum = 2)
    write_output('RR.txt', RR_schedule, RR_avg_waiting_time )
    print ("simulating SRTF ----")
    SRTF_schedule, SRTF_avg_waiting_time =  SRTF_scheduling(process_list)
    write_output('SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time )
    print ("simulating SJF ----")
    SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha = 0.5)
    write_output('SJF.txt', SJF_schedule, SJF_avg_waiting_time )

if __name__ == '__main__':
    main(sys.argv[1:])

