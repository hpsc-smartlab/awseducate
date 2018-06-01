import boto3
from botocore.exceptions import ClientError

def iamCreateSecurityGroup(groupname, path=None):
    
    iam = boto3.resource('iam')

    try:
        group = iam.create_group(GroupName=groupname)
    except ClientError as e:
        raise e

    return group

def iamCreateUser(username, path=None):
    
    iam = boto3.resource('iam')
    
    try:
        user = iam.create_user(UserName=username)
    except ClientError as e:
        raise e

    return user

def iamAddUserToGroup(groupname, username):
    
    iam = boto3.resource('iam')
    
    try:
        group = iam.Group(groupname)
        user  = iam.User(username)

    except Exception as e:
        raise e

    try:
        group.add_user(UserName=user.name)
    except ClientError as e:
        raise e

def iamDeleteUser():
    
    iam = boto3.resource('iam')

    try:
        user  = iam.User(username)
    except Exception as e:
        raise e

    try:
        response = user.delete()
    except Exception as e:
        raise e

    return response

def iamCreatePolicy():
    pass

def iamAttachPolicy(target, policy):
    pass

def iamDetachPolicy(target, policy):
    pass

def iamDeletePolicy(policy):
    pass

def iamListPolicies(scope, onlyattached):
    pass

def iamListAttacchedPolicies(target):
    pass

def iamCreateRole():
    pass

if __name__ == '__main__':
    
    iam = boto3.resource('iam')

    user = iam.User('bob')
    group = iam.Group('Devs')

    print user.name
    print group.name

    iamAddUserToGroup(group.name,user.name)
