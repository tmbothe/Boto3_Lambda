import boto3
import json

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


def handler(event,context):
    return {
        'statusCode' : 200,
        'message': 'Hello from python Lambda Function'
    }



if __name__=='__main__':
    print(create_access_policy_for_lambda())