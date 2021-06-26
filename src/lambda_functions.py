import boto3
import json
from os import path

from src.utils import *

LAMBDA_ROLE = 'Lambda_Execution_Role_new'
LAMDA_ACCESS_POLICY_ARN = 'arn:aws:iam::425439196533:policy/LambdaS3AccessPolict_new'
LAMDA_ROLE_ARN = 'arn:aws:iam::425439196533:role/Lambda_Execution_Role_new'
LAMBDA_TIMEOUT = 10
LAMBDA_MEMORY = 128
PYTHON_36_RUNTIME = 'python3.6'
PYTHON_FUNCTION_NAME = 'PYTHON_LAMBDA_FUNCTION'
PYTHON_HANDLER = 'Lambda_function.handler'

def lambda_client():
    aws_lambda = boto3.client('lambda')
    return aws_lambda

def iam_client():
    return boto3.client('iam')

def create_access_policy_for_lambda():
    s3_access_policy_document = {
        "Version": "2012-10-17",
        "Statement" : [
            {
            "Action" : [
                "S3:*",
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"

            ],
            "Effect":"Allow",
            "Resource": "*"
            }
        ]
        
    }
    return iam_client().create_policy(
        PolicyName = 'LambdaS3AccessPolict_new',
        PolicyDocument = json.dumps(s3_access_policy_document),
        Description  = "Allow Lambda to access S3 resources"
        )

#'arn:aws:iam::425439196533:policy/LambdaS3AccessPolict_new'
def create_execution_role_for_lambda():
    lambda_execution_assumption = {
        "Version" : "2012-10-17",
        "Statement" : [
            {
                "Effect": "Allow",
                "Principal" : {
                    "Service" : "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    return iam_client().create_role(
        RoleName= LAMBDA_ROLE,
        AssumeRolePolicyDocument=json.dumps(lambda_execution_assumption),
        Description = 'Gives necessary permission to lambda'
    )


def attach_access_policy_to_execution():
    return iam_client().attach_role_policy(
        RoleName = LAMBDA_ROLE,
        PolicyArn = LAMDA_ACCESS_POLICY_ARN
    )

def deploy_lambda_function(function_name,runtime,handler,role_arn,source_folder):
    folder_path = path.join(path.dirname(path.abspath(__file__)),source_folder)
    zip_file  = Utils.make_zip_file_bytes(path = folder_path)

    return lambda_client().create_function(
        FunctionName = function_name,
        Runtime = runtime,
        Role = role_arn,
        Handler = handler,
        Code = {
            'ZipFile' : zip_file
        },
        Timeout = LAMBDA_TIMEOUT,
        MemorySize = LAMBDA_MEMORY
        #Publish = False
    )


def invoke_lambda_function(function_name):
    return lambda_client().invoke(FunctionName=function_name)

def add_environment_variable_to_lambda(function_name,variables):
    return lambda_client().update_function_configuration(
        FunctionName=function_name,
        Environment=variables
    )


if __name__=='__main__':
    #print(create_access_policy_for_lambda())
    #print(create_execution_role_for_lambda())
    #print(attach_access_policy_to_execution())
    #print(deploy_lambda_function(PYTHON_FUNCTION_NAME,PYTHON_36_RUNTIME,PYTHON_HANDLER,LAMDA_ROLE_ARN,source_folder='/Users/thimothekonchou/Datascience/Boto3_Lambda/src/Lambda'))
    #response = invoke_lambda_function(function_name=PYTHON_FUNCTION_NAME)
    #print(response['Payload'].read().decode())
    env_variables={
     "Variables" :  {
        'ENV_VAR_TEST': 'This is an environment variables'
    }
    }

    add_environment_variable_to_lambda(PYTHON_FUNCTION_NAME,env_variables)
