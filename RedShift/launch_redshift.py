import boto3
import configparser
import pandas as pd
from botocore.exceptions import ClientError
import json


config = configparser.ConfigParser()

def get_params():
    config.read_file(open('config.cfg'))

    DWH_CLUSTER_TYPE       = config.get("DWH","DWH_CLUSTER_TYPE")
    DWH_NUM_NODES          = config.get("DWH","DWH_NUM_NODES")
    DWH_NODE_TYPE          = config.get("DWH","DWH_NODE_TYPE")

    DWH_CLUSTER_IDENTIFIER = config.get("DWH","DWH_CLUSTER_IDENTIFIER")
    DWH_DB                 = config.get("DWH","DWH_DB")
    DWH_DB_USER            = config.get("DWH","DWH_DB_USER")
    DWH_DB_PASSWORD        = config.get("DWH","DWH_DB_PASSWORD")
    DWH_PORT               = config.get("DWH","DWH_PORT")

    DWH_IAM_ROLE_NAME      = config.get("DWH", "DWH_IAM_ROLE_NAME")

    return (DWH_DB_USER, DWH_DB_PASSWORD, DWH_DB,DWH_CLUSTER_TYPE,DWH_NUM_NODES,DWH_NODE_TYPE,
            DWH_CLUSTER_IDENTIFIER,DWH_PORT,DWH_IAM_ROLE_NAME)


def ec2_resource():
    return boto3.resource('ec2')

def s3_resource():
    return boto3.resource('s3')

def iam_resource():
    return boto3.client('iam')

def redshift_client():
    return boto3.client('redshift')


def create_arn_role(dwh_iam_role_name):
    print('1.1 : Creating a new iam role')
    iam=iam_resource()

    try:
        dwhRole=iam.create_role(
            Path = '/',
            RoleName = dwh_iam_role_name,
            Description = 'Allows Redshift Clusters to call AWS services on your behalf.',
            AssumeRolePolicyDocument = json.dumps(
                {'Statement': [{'Action': 'sts:AssumeRole',
                'Effect': 'Allow',
                'Principal': {'Service': 'redshift.amazonaws.com'}}],
                'Version': '2012-10-17'})
        )    
    except Exception as e:
        print(e)

    print("1.2 : Attaching Policy")

    iam.attach_role_policy(RoleName=dwh_iam_role_name,
                        PolicyArn="arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
                        )['ResponseMetadata']['HTTPStatusCode']

    print("1.3: Get the IAM role ARN")
    roleArn = iam.get_role(RoleName=dwh_iam_role_name)['Role']['Arn']

    print(roleArn)    
    

def create_redshift_cluster(cluster_type,node_type,numberOfnodes,dbname,clusteridentifier,username,password,roleArn,iamRoleName):
    iam = iam_resource()
    try:
        response = redshift.create_cluster(
            ClusterType = cluster_type,
            NodeType = node_type,
            NumberOfNodes = int(numberOfnodes),
            DBName = dbname,
            ClusterIdentifier = clusteridentifier,
            MasterUsername = username,
            MasterPassword = password,
            IamRoles = [roleArn]
        )

    except Exception as e:
        print(e)

    print("1.2 Attaching Policy")

    iam.attach_role_policy(RoleName=iamRoleName,
                        PolicyArn="arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
                        )['ResponseMetadata']['HTTPStatusCode']

    print("1.3 Get the IAM role ARN")
    roleArn = iam.get_role(RoleName=iamRoleName)['Role']['Arn']

    print(roleArn)



def prettyRedshiftProps(props):
    pd.set_option('display.max_colwidth', -1)
    keysToShow = ["ClusterIdentifier", "NodeType", "ClusterStatus", "MasterUsername", "DBName", "Endpoint", "NumberOfNodes", 'VpcId']
    x = [(k, v) for k,v in props.items() if k in keysToShow]
    return pd.DataFrame(data=x, columns=["Key", "Value"])


if __name__=='__main__':
        
    redshift = redshift_client()
    DWH_DB_USER, DWH_DB_PASSWORD, DWH_DB,DWH_CLUSTER_TYPE,DWH_NUM_NODES,DWH_NODE_TYPE,DWH_CLUSTER_IDENTIFIER,DWH_PORT,DWH_IAM_ROLE_NAME = get_params()

    
    myClusterProps = redshift.describe_clusters(ClusterIdentifier=DWH_CLUSTER_IDENTIFIER)['Clusters'][0]
    prettyRedshiftProps(myClusterProps)
    DWH_ENDPOINT = myClusterProps['Endpoint']['Address']
    DWH_ROLE_ARN = myClusterProps['IamRoles'][0]['IamRoleArn']
    print("DWH_ENDPOINT :: ", DWH_ENDPOINT)
    print("DWH_ROLE_ARN :: ", DWH_ROLE_ARN)

    #Open an incoming TCP port to access the cluster ednpoint

    ec2 = ec2_resource()
    try:
        vpc = ec2.Vpc(id=myClusterProps['VpcId'])
        defaultSg = list(vpc.security_groups.all())[0]
        print(defaultSg)
        
        defaultSg.authorize_ingress(
            GroupName= defaultSg.group_name,  # TODO: fill out
            CidrIp='0.0.0.0/0',  # TODO: fill out
            IpProtocol='TCP',  # TODO: fill out
            FromPort=int(DWH_PORT),
            ToPort=int(DWH_PORT)
        )
    except Exception as e:
        print(e)

    # Clean up your resources
    redshift.delete_cluster( ClusterIdentifier=DWH_CLUSTER_IDENTIFIER,  SkipFinalClusterSnapshot=True)

    myClusterProps = redshift.describe_clusters(ClusterIdentifier=DWH_CLUSTER_IDENTIFIER)['Clusters'][0]
    prettyRedshiftProps(myClusterProps)

    #-- Uncomment & run to delete the created resources
    #iam.detach_role_policy(RoleName=DWH_IAM_ROLE_NAME, PolicyArn="arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess")
    #iam.delete_role(RoleName=DWH_IAM_ROLE_NAME)

