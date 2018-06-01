import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import problem_1.problem1 as p1

'''
1) Launch 5 free-tier instance with Amazon Linux:
    -   3 with  (HVM) ami
    -   2 with  Deep Learning ami

2) Update the machine type of the deep learning instances
   To t2 small

3) terminate the two most recentnly launched free tier instances

4) print a list of the instances still running at this point
'''

# 1
hvm = p1.ec2ResourceLaunch(3,3,'ami-969c2deb') #a
dl  = p1.ec2ResourceLaunch(2,2,'ami-3c8a3b41') #b

# 2 client-like invocation
p1.ec2ResourceStop([i.id for i in dl])
p1.ec2ResourceModifyInstanceType([i.id for i in dl],'t2.nano')
p1.ec2ResourceStart([i.id for i in dl])

# 2-bis taking advantage of the object interface
for instance in dl:
    instance.stop() #stop before upgrading   
    p1.ec2ResourceModifyInstanceType([instance.id],'t2.nano')
    p1.ec2ResourceStart([instance.id]) #instead of instance.start()
# 3
times = [{'id': i.id, 'launch': i.launch_time} for i in hvm]
t_sorted = sorted(times, key=lambda k: k['launch'], reverse=True)[0:2]

p1.ec2ResourceTerminate([t['id'] for t in t_sorted])

# 4
print p1.ec2ResourceListInstanceByStatus('running')
'''
