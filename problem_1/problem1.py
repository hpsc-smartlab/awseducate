import boto3
from botocore.exceptions import ClientError

# Notes: If you specify more instances than Amazon EC2 can launch in the target Availability Zone, 
# Amazon EC2 launches the largest possible number of instances above MinCount. 
# If you specify a minimum that is more instances than Amazon EC2 can launch in the target Availability Zone, 
# Amazon EC2 launches no instances at all.

def ec2ResourceLaunch(mincount, maxcount, ami, instancetype = 't2.micro', sync = True):
	
	''' Launches -maxcount- instances of -InstanceType- with the specified ami using object oriented interface (resource)
		and returns the related object interfaces

		@type mincount:     	integer
		@param mincount:    	minimum number of instances to launch
		@type maxcount:     	integer
		@param maxcount:    	maximum number of instances to launch
		@type ami:          	string
		@param ami:         	amazon machine image deployed
		@type instancetype:		string
		@param instancetype:	type of launched instances
		@type sync:				boolean
		@param sync: 			wait for the operation to take effect
		@rtype:    [ec2factoryObj, ..., ec2factoryObj]
		@return:   list of instance type objects
	'''

	# Object Oriented High level AWS client interface
	ec2resource = boto3.resource('ec2')
	
	# Try a dry run to veryfy permissions
	# Dry-runs always return an error response:
	# 'DryrunOperation': OK 'UnauthorizedOperation': NO
	try:
		ec2resource.create_instances(
		MinCount = mincount, 
		MaxCount = maxcount, 
		ImageId  = ami, 
		InstanceType=instancetype,
		DryRun = True)
	except ClientError as e:
		if 'DryRunOperation' not in str(e):
			raise

	try:
		instances = ec2resource.create_instances(
		MinCount = mincount, 
		MaxCount = maxcount, 
		ImageId  = ami, 
		InstanceType=instancetype)
	except ClientError as e:
		raise e
 
	if sync:
		# Wait till all the instances are in a running state
		for instance in instances:
			print "waiting for the instance to be in running state"
			instance.wait_until_running()
			instance.reload()
			print "Image id: ",		instance.image_id
			print "Instance id: ", instance.id
			print "Instance type: ", instance.instance_type
			print "Instance state: ", instance.state['Name']
			print "instance public IP: ", instance.public_ip_address
			print "Instance public DNS: ", instance.public_dns_name

	return instances

def ec2ClientLaunch(mincount, maxcount, ami, instancetype = 't2.micro', sync = True):
	
	''' 
	Launches -maxcount- instances of -InstanceType- with the specified ami
	and returns the related object interfaces

	@type mincount:     	integer
	@param mincount:    	minimum number of instances to launch
	@type maxcount:     	integer
	@param maxcount:    	maximum number of instances to launch
	@type ami:          	string
	@param ami:         	amazon machine image deployed
	@type instancetype:   	string
	@param instancetype: 	type of launched instances
	@type sync:				boolean
	@param sync: 			wait for the operation to take effect
	@rtype:    dict
	@return:   response dict containing the information of the running instances
	'''

	# Low level AWS client 1:1 interface
	ec2client = boto3.client('ec2')

	# Try a dry run to veryfy permissions
	# Dry-runs always return an error response:
	# 'DryrunOperation': OK 'UnauthorizedOperation': NO
	try:
		ec2client.run_instances(
			MinCount = mincount, 
			MaxCount = maxcount, 
			ImageId = ami, 
			InstanceType = instancetype,
			DryRun = True)
	except ClientError as e:
		if 'DryRunOperation' not in str(e):
			raise
	try:
		response = ec2client.run_instances(
			MinCount = mincount, 
			MaxCount = maxcount, 
			ImageId = ami, 
			InstanceType = instancetype)
	except ClientError as e:
		raise e

	ids = [x.get('InstanceId') for x in response['Instances']]

	# wait for the instances to be in a running state
	if sync:
		for my_id in ids:
			waiter = ec2client.get_waiter('instance_running')
			print "waiting for the instance to be in running state"
			waiter.wait(InstanceIds=[my_id])
			
		info = ec2client.describe_instances(InstanceIds = ids)

		for reservation in info['Reservations']:
			for instance in reservation['Instances']:
				print "Image id: ", instance['ImageId']
				print "Instance id: ", instance['InstanceId']
				print "Instance type: ", instance['InstanceType']
				print "Instance state: ", instance['State']['Name']
				print "Instance public IP: ", instance['PublicIpAddress']
				print "Instance public DNS: ", instance['PublicDnsName']

	return response

def ec2ResourceStop(ids, force = False, sync = True):
	''' stops running instances

		@type ids:		[string,...,string]
		@param ids:		ids of the instances
		@type force:	boolean
		@param force:	force the stop
		@type sync:		boolean
		@param sync: 	wait for the operation to take effect
		@rtype:		[dict,...,dict]
		@return:	response metadata
	'''

	# Object Oriented High level AWS client interface
	ec2resource = boto3.resource('ec2')

	# Try a dry run to veryfy permissions
	# Dry-runs always return an error response:
	# 'DryrunOperation': OK 'UnauthorizedOperation': NO
	try:
		ec2resource.instances.filter(InstanceIds=ids).stop(Force=force, DryRun=True)
	except ClientError as e:
		if 'DryRunOperation' not in str(e):
			raise
	try:
		instances = ec2resource.instances.filter(InstanceIds=ids)
		response  = instances.stop(Force=force)

		if sync:
			for instance in instances:
				print "waiting for the instance to be in stopped state"
				instance.wait_until_stopped()
				instance.reload()
				print "Instance id: ", instance.id
				print "Instance state: ", instance.state['Name']	 
	except ClientError as e:
		raise e

	return response

def ec2ClientStop(ids, force = False, sync = True):
	''' stops running instances

		@type ids:		[string,...,string]
		@param ids:		ids of the instances
		@type force:	boolean
		@param force:	force the stop
		@type sync:		boolean
		@param sync: 	wait for the operation to take effect
		@rtype:		[dict,...,dict]
		@return:	response metadata
	'''

	# Object Oriented High level AWS client interface
	ec2client = boto3.client('ec2')

	# Try a dry run to veryfy permissions
	# Dry-runs always return an error response:
	# 'DryrunOperation': OK 'UnauthorizedOperation': NO
	try:
		ec2client.stop_instances(InstanceIds=ids, Force=force, DryRun=True)	
	except ClientError as e:
		if 'DryRunOperation' not in str(e):
			raise
	try:
		response = ec2client.stop_instances(InstanceIds=ids, Force=force)
	
		# wait for the instances to be in a stopped state
		if sync:
			for my_id in ids:
				waiter = ec2client.get_waiter('instance_stopped')
				print "waiting for the instance to be in stopped state"
				waiter.wait(InstanceIds=[my_id])

			info = ec2client.describe_instances(InstanceIds = ids)

			for reservation in info['Reservations']:
				for instance in reservation['Instances']:
					print "Instance id: ", instance['InstanceId']
					print "Instance state: ", instance['State']['Name']

	except ClientError as e:
		raise e

	return response

def ec2ResourceStart(ids, sync = True):
	''' starts stopped instances

		@type ids:		[string,...,string]
		@param ids:		ids of the instances
		@type sync:		boolean
		@param sync: 	wait for the operation to take effect
		@rtype:    [dict,...,dict]
		@return:   response metadata
	'''

	# Object Oriented High level AWS client interface
	ec2resource = boto3.resource('ec2')

	# Try a dry run to veryfy permissions
	# Dry-runs always return an error response:
	# 'DryrunOperation': OK 'UnauthorizedOperation': NO
	try:
		ec2resource.instances.filter(InstanceIds=ids).start(DryRun=True)
	except ClientError as e:
		if 'DryRunOperation' not in str(e):
			raise
	try:
		instances = ec2resource.instances.filter(InstanceIds=ids)
		response  = instances.start()
		if sync:
			for instance in instances:
				print "waiting for the instance to be in running state"
				instance.wait_until_running()
				instance.reload()
				print "Instance id: ", instance.id
				print "Instance state: ", instance.state['Name']
	except ClientError as e:
		raise e

	return response

def ec2ClientStart(ids, sync = True):
	''' starts stopped instances

		@type ids:		[string,...,string]
		@param ids:		ids of the instances
		@type sync:		boolean
		@param sync: 	wait for the operation to take effect
		@rtype:    [dict,...,dict]
		@return:   response metadata
	'''

	# Object Oriented High level AWS client interface
	ec2client = boto3.client('ec2')

	# Try a dry run to veryfy permissions
	# Dry-runs always return an error response:
	# 'DryrunOperation': OK 'UnauthorizedOperation': NO
	try:
		ec2client.start_instances(InstanceIds=ids, DryRun=True)	
	except ClientError as e:
		if 'DryRunOperation' not in str(e):
			raise
	try:
		response = ec2client.start_instances(InstanceIds=ids)
		
		# wait for the instances to be in a running state
		if sync:
			for my_id in ids:
				waiter = ec2client.get_waiter('instance_running')
				print "waiting for the instance to be in stopped state"
				waiter.wait(InstanceIds=[my_id])

			info = ec2client.describe_instances(InstanceIds = ids)

			for reservation in info['Reservations']:
				for instance in reservation['Instances']:
					print "Instance id: ", instance['InstanceId']
					print "Instance state: ", instance['State']['Name']
	except ClientError as e:
		raise e

	return response

def ec2ResourceTerminate(ids, sync = True):
	''' termiates running/stopped instances

		@type ids:		[string,...,string]
		@param ids:		ids of the instances
		@type sync:		boolean
		@param sync: 	wait for the operation to take effect
		@rtype:    [dict,...,dict]
		@return:   response metadata
	'''

	# Object Oriented High level AWS client interface
	ec2resource = boto3.resource('ec2')

	# Try a dry run to veryfy permissions
	# Dry-runs always return an error response:
	# 'DryrunOperation': OK 'UnauthorizedOperation': NO
	try:
		ec2resource.instances.filter(InstanceIds=ids).terminate(DryRun=True)
	except ClientError as e:
		if 'DryRunOperation' not in str(e):
			raise
	try:
		instances = ec2resource.instances.filter(InstanceIds=ids)
		response  = instances.terminate()
		if sync:
			for instance in instances:
				print "waiting for the instance to be in terminated state"
				instance.wait_until_terminated()
				instance.reload()
				print "Instance id: ", instance.id
				print "Instance state: ", instance.state['Name']
	except ClientError as e:
		raise e

	return response

def ec2ClientTerminate(ids, sync = True):
	''' terminates running/stopped instances

		@type ids:		[string,...,string]
		@param ids:		ids of the instances
		@type sync:		boolean
		@param sync: 	wait for the operation to take effect
		@rtype:    [dict,...,dict]
		@return:   response metadata
	'''

	# Object Oriented High level AWS client interface
	ec2client = boto3.client('ec2')

	# Try a dry run to veryfy permissions
	# Dry-runs always return an error response:
	# 'DryrunOperation': OK 'UnauthorizedOperation': NO
	try:
		ec2client.terminate_instances(InstanceIds=ids, DryRun=True)	
	except ClientError as e:
		if 'DryRunOperation' not in str(e):
			raise
	try:
		response = ec2client.terminate_instances(InstanceIds=ids)

		# wait for the instances to be in a terminated state
		if sync:
			for my_id in ids:
				waiter = ec2client.get_waiter('instance_terminated')
				print "waiting for the instance to be in terminated state"
				waiter.wait(InstanceIds=[my_id])

			info = ec2client.describe_instances(InstanceIds = ids)

			for reservation in info['Reservations']:
				for instance in reservation['Instances']:
					print "Instance id: ", instance['InstanceId']
					print "Instance state: ", instance['State']['Name']
	except ClientError as e:
		raise e

	return response

def ec2ResourceListInstanceByStatus(status):
	''' list all instances in a given status
		@type status:		string
		@param status:		running|terminated|stopped...
		@rtype:    [ec2factoryObj, ..., ec2factoryObj]
		@return:   filtered list of instance type objects
	'''
	ec2resource = boto3.resource('ec2')

	filters = [{
	'Name':'instance-state-name',
	'Values': [status]
	}]

	instances = ec2resource.instances.filter(Filters=filters)

	for instance in instances:
		print "Instance id: ", instance.id
		print "Instance type: ", instance.instance_type
		print "Instance state: ", instance.state['Name']
		print "instance public IP: ", instance.public_ip_address
		print "Instance public DNS: ", instance.public_dns_name
		print "--------------------"

	return instances

def ec2ClientListInstanceByStatus(status):
	''' list all instances in a given status
		@type status:		string
		@param status:		running|terminated|stopped...
		@rtype:    [dict,...,dict]
		@return:   response metadata
	'''
	ec2client = boto3.client('ec2')

	filters = [{
	'Name':'instance-state-name',
	'Values': [status]
	}]

	info = ec2client.describe_instances(Filters=filters)

	for reservation in info['Reservations']:
		for instance in reservation['Instances']:
			print "Instance id: ", instance['InstanceId']
			print "Instance type: ", instance['InstanceType']
			print "Instance state: ", instance['State']['Name']
			print "Instance public IP: ", instance['PublicIpAddress']
			print "Instance public DNS: ", instance['PublicDnsName']
			print "--------------------"

	return info

def ec2ClientModifyInstanceType(ids, new_type):
	''' Change instance type, only works if instance is stopped

		@type ids:		[string,...,string]
		@param ids:		ids of the instances
		@type new_type:	string
		@param newtype: t2.micro|m4.large|...
		@rtype:    None
		@return:   None
	'''
	
	ec2client = boto3.client('ec2')
	filters   = [{'Name':'instance-state-name','Values': ['stopped']}]

	info = ec2client.describe_instances(InstanceIds=ids, Filters=filters)

	# Try a dry run to veryfy permissions
	# only single instance objects can invoke modify attribute
	# instancegroups cannot
	try:
		for reservation in info['Reservations']:
			for instance in reservation['Instances']:		
				if instance['InstanceType'] is not new_type:
					ec2client.modify_instance_attribute(
						InstanceId=instance['InstanceId'],
						InstanceType={'Value': new_type}, 
						DryRun=True)
	except ClientError as e:
		if 'DryRunOperation' not in str(e):
			raise

	try:
		for reservation in info['Reservations']:
			for instance in reservation['Instances']:
				if instance['InstanceType'] is not new_type:
					print "Changing the type of instance: "
					print "Instance id: ", instance['InstanceId']
					print "From "+instance['InstanceType']+" to "+new_type
					ec2client.modify_instance_attribute(
						InstanceId=instance['InstanceId'],
						InstanceType={'Value': new_type})
	except ClientError as e:
			raise e

	return None
	
def ec2ResourceModifyInstanceType(ids, new_type):
	''' Change instance type, only works if instance is stopped

		@type ids:		[string,...,string]
		@param ids:		ids of the instances
		@type new_type:	string
		@param newtype: t2.micro|m4.large|...
		@rtype:    None
		@return:   None
	'''

	# Object Oriented High level AWS client interface
	ec2resource = boto3.resource('ec2')
	filters     = [{'Name':'instance-state-name','Values': ['stopped']}]

	# Try a dry run to veryfy permissions
	# only single instance objects can invoke modify attribute
	# instancegroups cannot
	try:
		instances = ec2resource.instances.filter(InstanceIds=ids, Filters=filters)
		
		for instance in instances:
			if instance.instance_type is not new_type:
				instance.modify_attribute(InstanceType={'Value': new_type}, DryRun=True)
	except ClientError as e:
		if 'DryRunOperation' not in str(e):
			raise

	try:		
		instances = ec2resource.instances.filter(InstanceIds=ids, Filters=filters)		
		for instance in instances:
			# reverse filtering doesn't exist yet in boto3
			if instance.instance_type is not new_type:
				print "Changing the type of instance: "
				print "Instance id: ", instance.id
				print "From "+instance.instance_type+" to "+new_type
				instance.modify_attribute(InstanceType={'Value': new_type})

	except ClientError as e:
		raise e

	return None
