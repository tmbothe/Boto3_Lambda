import boto3

client = boto3.client('ec2')

resp = client.describe_instances()
print(resp['Reservations'])
#print(resp['Reservations'][0]['Instances'][0])
for reservation in resp['Reservations']:
    for instance in reservation['Instances']:
        print(f"The instance Is {instance['InstanceId']}")
        print(f"The instance type {instance['InstanceType']}")
        print(f"The instance state {instance['State']['Name']}")
