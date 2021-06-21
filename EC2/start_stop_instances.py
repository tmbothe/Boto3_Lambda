import boto3

client = boto3.client('ec2')

def start_instance(instanceID):
    try:
        resp = client.start_instances(InstanceIds=[instanceID])
        print('Instance successfully started')
    except:
        print('The instance does not exists')

def stop_instance(instanceId):
    try:
        resp = client.stop_instances(InstanceIds=[instanceId])
        print('Instance successfully stopped')
    except:
        print('An eror occured')

def terminate_instance(instanceId):
    try:
        resp = client.terminate_instances(InstanceIds=[instanceId])
        print('Instance successfully terminated')
    except:
        print('An eror occured')

#for instance in response['InstanceId']:
#    print("The instance with id {} ".format(instance['InstanceId']))


if __name__=='__main__':
    instanceId = 'i-0e6bdd316ff1998b2'

    #stop_instance(instanceId)
    terminate_instance(instanceId)