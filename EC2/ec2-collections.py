import boto3
ec2 = boto3.resource('ec2')

for instance in ec2.instances.all():
    print('Instance id is {} and  Instance Type is {}'.format(instance.instance_id,instance.instance_type))

for instance in ec2.instances.filter(Filters=[{
    'Name': 'availability-zone',
    'Values': ['us-east-2c']}]):
    print('Instance id is {} and  Instance Type is {}'.format(instance.instance_id, instance.instance_type))

