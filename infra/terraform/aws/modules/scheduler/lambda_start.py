import os
import boto3

ec2 = boto3.client("ec2")

def lambda_handler(event, context):
    tag_key = os.environ["TAG_KEY"]
    tag_value = os.environ["TAG_VALUE"]

    response = ec2.describe_instances(
        Filters=[
            {"Name": f"tag:{tag_key}", "Values": [tag_value]},
            {"Name": "instance-state-name", "Values": ["stopped"]},
        ]
    )

    instance_ids = []
    for reservation in response.get("Reservations", []):
        for instance in reservation.get("Instances", []):
            instance_ids.append(instance["InstanceId"])

    if not instance_ids:
        print("No stopped instances found matching tag filter")
        return {"started_instances": []}

    ec2.start_instances(InstanceIds=instance_ids)
    print(f"Started instances: {instance_ids}")
    return {"started_instances": instance_ids}