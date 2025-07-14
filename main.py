MASTER_ACCOUNT_ID = "000000000000"
ROLE_NAME = "MyRole"

import boto3
import botocore
import json

# Assume cross-account role
def assumeRole(accountNo):
    try:
        sts_client = boto3.client('sts')
        response = sts_client.assume_role(
            RoleArn=f"arn:aws:iam::{accountNo}:role/{ROLE_NAME}",
            RoleSessionName="ListStoppedInstances",
            DurationSeconds=900
        )
        credentials = response['Credentials']
        print(f"[+] Assumed role in {accountNo}")
        return credentials
    except botocore.exceptions.ClientError as error:
        print(f"[-] Could not assume role in {accountNo} - {error}")
        return None

# Create session with assumed credentials
def create_session(accountNo, region):
    credentials = assumeRole(accountNo)
    if credentials is None:
        return None
    return boto3.Session(
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken'],
        region_name=region
    )

# Get all ACTIVE AWS accounts under the organization
def getAccounts(master_account):
    accounts = []
    # NOTE: Organizations is a global service; region here is just to satisfy boto3 session
    session = create_session(master_account, "us-west-2")
    if session is None:
        return []
    client = session.client('organizations')
    paginator = client.get_paginator('list_accounts')
    for page in paginator.paginate():
        for acct in page['Accounts']:
            if acct.get("Status") == "ACTIVE":
                accounts.append(acct.get("Id"))
    print(f"[+] Fetched active accounts: {accounts}")
    return accounts

# Get all regions enabled in an account
def get_active_regions(account_id):
    session = create_session(account_id, "us-west-2")
    if session is None:
        return []
    client = session.client('ec2')
    try:
        response = client.describe_regions(AllRegions=False)
        regions = [r['RegionName'] for r in response['Regions']]
        print(f"[+] Regions for account {account_id}: {regions}")
        return regions
    except Exception as e:
        print(f"[-] Could not fetch regions for {account_id}: {e}")
        return []

# Get stopped EC2 instances in a region/account
def get_stopped_instances(account_id, region):
    session = create_session(account_id, region)
    if session is None:
        return []

    client = session.client('ec2')
    stopped_instances = []

    try:
        print(f"[~] Checking stopped instances in {region} of {account_id}")
        paginator = client.get_paginator('describe_instances')
        for page in paginator.paginate(
            Filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}]
        ):
            for reservation in page['Reservations']:
                for instance in reservation['Instances']:
                    instance_id = instance['InstanceId']
                    launch_time = instance['LaunchTime'].isoformat()
                    stopped_instances.append({
                        "AccountId": account_id,
                        "Region": region,
                        "InstanceId": instance_id,
                        "LaunchTime": launch_time
                    })
        print(f"[+] Found {len(stopped_instances)} stopped instances in {region} of {account_id}")
        return stopped_instances

    except Exception as e:
        print(f"[-] Error in {account_id} {region}: {e}")
        return []

# === Main logic ===
accounts = getAccounts(MASTER_ACCOUNT_ID)
AllStoppedInstances = []

for account in accounts:
    regions = get_active_regions(account)
    for region in regions:
        instances = get_stopped_instances(account, region)
        if instances:
            AllStoppedInstances.extend(instances)

# Save result
output_path = './StoppedInstances.json'
with open(output_path, 'w') as f:
    f.write(json.dumps(AllStoppedInstances, indent=4))

print(f"\n✅ Done! Stopped instance data written to: {output_path}")
