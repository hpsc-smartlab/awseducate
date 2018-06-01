import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import problem_1.problem1 as p1
import problem_2.problem2 as p2

# creaiamo i volumi
v1 = p2.ec2ResourceCreateVolume(zone='eu-west-3c', volumetype='standard', size=1024)
v2 = p2.ec2ResourceCreateVolume(zone='eu-west-3c', volumetype='gp2', size=512)

# acquisiamo le istanze in esecuzione sul nostro account
instances = p1.ec2ResourceListInstanceByStatus('running')

# selezione delle prime due istanze restituite
selected = list(instances)[0:2]

# che tipo di for e' questo ?
for instance, volume in zip(selected,[v1,v2]):
    p2.ec2ResourceAttachVolume( devicename='/dev/sdh',
                                volumeid=volume.id,
                                instanceid=instance.id)


# cambiamo il size, lasciando inalterato il tipo
p2.ec2ClientModifyVolume(volumeid=v2.id, volumetype=v2.volume_type, volumesize=2048)

p2.ec2ClientDetachVolume(v1.id)

# questa funzione potrebbe non partire, perche' ? Come risolvere ?
# hint: controllare la funzione per la creazione del volume

# --- placeholder ---

p2.ec2ClientDeleteVolume(v1.id)
