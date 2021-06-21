import boto3

client = boto3.client('ec2')

resp = client.describe_instances()

#print(resp['Reservations'][0]['Instances'][0])
for reservation in resp['Reservations']:
    for instance in reservation['Instances']:
        print(f"The instance Is {instance['InstanceId']}")
