import boto3
from botocore.exceptions import ClientError
''' Notes: 
	-	If you detach a volume from a running instance, you must first unmount it
	-	if a volume is the root device of an instance, you must first stop the instance instead
'''
def ec2ResourceCreateVolume(zone, volumetype, size, encrypted = False):
	''' Create a volume of type -volumetype- and size -size- (in GB)
		possibly ecnrypted, using high-level resource interface
		and returns the related objects

		@type zone:     		string
		@param zone:    		one of the available zones
		@type volumetype:     	string
		@param volumetype:    	the type of volume: |'io1'|'gp2'|'sc1'|'st1'
		@type size:          	integer
		@param size:         	size in GigaBytes
		@type encrypted:		boolean
		@param encrypted:		allows for encrypted volumes
		@rtype:    [ec2VolumeObj, ..., ec2VolumeObj]
		@return:   list of volume type objects
	'''
	ec2resource = boto3.resource('ec2')

	try:
		ec2resource.create_volume(
		AvailabilityZone=zone,
		Encrypted=encrypted,
		VolumeType=volumetype,
		Size=size,
		DryRun=True)
	except ClientError as e:
		if 'DryRunOperation' not in str(e):
			raise

	try:
		volume = ec2resource.create_volume(
		AvailabilityZone=zone,
		Encrypted=encrypted,
		VolumeType=volumetype,
		Size=size)
	except ClientError as e:
		raise e

	return volume

def ec2ClientCreateVolume(zone, volumetype, size, encrypted = False ):
	''' Create a volume of type -volumetype- and size -size- (in GB)
		possibly ecnrypted, using low-level client interface
		and returns the related objects

		@type zone:     		string
		@param zone:    		one of the available zones
		@type volumetype:     	string
		@param volumetype:    	the type of volume: |'io1'|'gp2'|'sc1'|'st1'
		@type size:          	integer
		@param size:         	size in GigaBytes
		@type encrypted:		boolean
		@param encrypted:		allows for encrypted volumes
		@rtype:    [ec2VolumeObj, ..., ec2VolumeObj]
		@return:   list of volume type objects
	'''
	ec2client = boto3.client('ec2')

	try:
		ec2client.create_volume(
		AvailabilityZone=zone,
		Encrypted=encrypted,
		VolumeType=volumetype,
		Size=size,
		DryRun=True)
	except ClientError as e:
		if 'DryRunOperation' not in str(e):
			raise

	try:
		response = ec2client.create_volume(
		AvailabilityZone=zone,
		Encrypted=encrypted,
		VolumeType=volumetype,
		Size=size)
	except ClientError as e:
		raise e

	return response

def ec2ResourceDeleteVolume(volumeid):
	''' Delete a volume via his ids 
		using high-level resource interface.

		@type volumeid:     	string
		@param volumeid:    	the id of the volume
		@type size:          	integer
		@rtype:    ec2.Volume
		@return:   the deleted volume
	'''
	
	ec2resource = boto3.resource('ec2')

	try:
		ec2resource.Volume(volumeid).delete(DryRun=True)
	except ClientError as e:
		if 'DryRunOperation' not in str(e):
			raise

	try:
		volume = ec2resource.Volume(volumeid)
		volume.delete()
		volume.reload()
	except ClientError as e:
		raise e

	return volume

def ec2ClientDeleteVolume(volumeid):
	''' Delete a volume via his id 
		using the low-level client interface.

		@type volumeid:     	string
		@param volumeid:    	the id of the volume
		@type size:          	integer
		@rtype:    ec2.Volume
		@return:   the deleted volume
	'''

	ec2client = boto3.client('ec2')

	try:
		ec2client.delete_volume(VolumeId=volumeid,DryRun=True)
	except ClientError as e:
		if 'DryRunOperation' not in str(e):
			raise

	try:
		response = ec2client.delete_volume(VolumeId=volumeid)
	except ClientError as e:
		raise e

	return response

def ec2ResourceAttachVolume(devicename, volumeid, instanceid):
	''' Attach an available volume to an instance (running or stopped)
		using the high-level resource interface.

		@type devicename:     	string
		@param devicename:    	the name of the volume: ex. '/dev/sdh' or 'xvdh'
		@type volumeid:     	string
		@param volumeid:    	the id of the volume
		@type instanceid:     	string
		@param instanceid:    	the id of the instance
		@rtype:    ec2.Volume
		@return:   the attacched volume
	'''
	ec2resource = boto3.resource('ec2')

	try:
		ec2resource.Volume(volumeid).attach_to_instance(
			Device=devicename,
			InstanceId=instanceid,
			DryRun=True)
	except ClientError as e:
		if 'DryRunOperation' not in str(e):
			raise

	try:
		volume = ec2resource.Volume(volumeid)
		volume.attach_to_instance(Device=devicename, InstanceId=instanceid)
		volume.reload()
	except ClientError as e:
		raise e

	return volume

def ec2ClientAttachVolume(devicename, volumeid, instanceid ):
	''' Attach an available volume to an instance (running or stopped)
		using the low-level client interface.

		@type devicename:     	string
		@param devicename:    	the name of the volume: ex. '/dev/sdh' or 'xvdh'
		@type volumeid:     	string
		@param volumeid:    	the id of the volume
		@type instanceid:     	string
		@param instanceid:    	the id of the instance
		@rtype:    dict
		@return:   response metadata
	'''

	ec2client = boto3.client('ec2')

	try:
		ec2client.attach_volume(
			Device=devicename,
			InstanceId=instanceid,
			VolumeId=volumeid,
			DryRun=True)
	except ClientError as e:
		if 'DryRunOperation' not in str(e):
			raise

	try:
		response = ec2client.attach_volume(
			Device=devicename,
			InstanceId=instanceid,
			VolumeId=volumeid)
	except ClientError as e:
		raise e

	return response

def ec2ResourceDetachVolume(volumeid, force = False):
	''' Detach a volume from its instance (running or stopped)
		using the high-level resource interface.

		@type volumeid:     string
		@param volumeid:    the id of the volume
		@type force:     	boolean
		@param force:    	force the operation
		@rtype:    ec2.Volume
		@return:   the detached volume
	'''
	ec2resource = boto3.resource('ec2')

	try:
		ec2resource.Volume(volumeid).detach_from_instance(Force=force, DryRun=True)
	except ClientError as e:
		if 'DryRunOperation' not in str(e):
			raise

	try:
		volume = ec2resource.Volume(volumeid)
		volume.detach_from_instance(Force=force)
		volume.reload()
	except ClientError as e:
		raise e

	return volume

def ec2ClientDetachVolume(volumeid, force = False):
	''' Detach a volume from its instance (running or stopped)
		using the low-level client interface.

		@type volumeid:     string
		@param volumeid:    the id of the volume
		@type force:     	boolean
		@param force:    	force the operation
		@rtype:    dict
		@return:   response metadata
	'''

	ec2client = boto3.client('ec2')

	try:
		ec2client.detach_volume(
			VolumeId=volumeid,
			Force=force,
			DryRun=True)
	except ClientError as e:
		if 'DryRunOperation' not in str(e):
			raise

	try:
		response = ec2client.detach_volume(VolumeId=volumeid,Force=force)
	except ClientError as e:
		raise e

	return response

def ec2ResourceListAttacchedVolumes(ids):
	''' List all volumes attacched to input instances
		using the high-level resource interface.

		@type ids:     		[string,...,string]
		@param ids:    		ids of the instances
		@rtype:    [ec2VolumeObj, ..., ec2VolumeObj]
		@return:   list of volume type objects
	'''	
	ec2resource = boto3.resource('ec2')

	try:
		filters  = [{'Name':'status', 'Values':['in-use']},
					{'Name':'attachment.instance-id', 'Values':ids}]
		volumes  = ec2resource.volumes.filter(Filters=filters)
	except ClientError as e:
		raise e

	return volumes

def ec2ClientListAttacchedVolumes(ids):
	''' List all volumes attacched to input instances
		using the low-level resource interface.

		@type ids:     		[string,...,string]
		@param ids:    		ids of the instances
		@rtype:    dict
		@return:   response metadata
	'''
	ec2client = boto3.client('ec2')

	try:
		filters  = [{'Name':'status', 'Values':['in-use']},
					{'Name':'attachment.instance-id', 'Values':ids}]
		response  = ec2client.describe_volumes(Filters=filters)
	except ClientError as e:
		raise e

	return response
