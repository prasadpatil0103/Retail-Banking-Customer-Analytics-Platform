
import boto3

def create_cloudwatch_alerts():
    client = boto3.client("cloudwatch", region_name="us-east-1")
    sns = boto3.client("sns", region_name="us-east-1")

    # Create SNS topic for alerts
    topic = sns.create_topic(Name="banking-pipeline-alerts")
    topic_arn = topic["TopicArn"]
    print(f"SNS topic created: {topic_arn}")

    alarms = [
        {
            "AlarmName": "banking-glue-job-failure",
            "AlarmDescription": "Alert when Glue ETL job fails",
            "MetricName": "glue.driver.aggregate.numFailedTasks",
            "Namespace": "Glue",
            "Statistic": "Sum",
            "Period": 300,
            "EvaluationPeriods": 1,
            "Threshold": 1,
            "ComparisonOperator": "GreaterThanOrEqualToThreshold",
            "Dimensions": [{"Name": "JobName", "Value": "banking-etl-job"}],
            "AlarmActions": [topic_arn],
        },
        {
            "AlarmName": "banking-s3-ingestion-lag",
            "AlarmDescription": "Alert when no new files in S3 for 24 hours",
            "MetricName": "NumberOfObjects",
            "Namespace": "AWS/S3",
            "Statistic": "Average",
            "Period": 86400,
            "EvaluationPeriods": 1,
            "Threshold": 1,
            "ComparisonOperator": "LessThanThreshold",
            "Dimensions": [
                {"Name": "BucketName", "Value": "retail-banking-analytics-prasad"},
                {"Name": "StorageType", "Value": "AllStorageTypes"},
            ],
            "AlarmActions": [topic_arn],
        },
        {
            "AlarmName": "banking-redshift-high-cpu",
            "AlarmDescription": "Alert when Redshift CPU exceeds 80%",
            "MetricName": "CPUUtilization",
            "Namespace": "AWS/Redshift-Serverless",
            "Statistic": "Average",
            "Period": 300,
            "EvaluationPeriods": 2,
            "Threshold": 80,
            "ComparisonOperator": "GreaterThanOrEqualToThreshold",
            "Dimensions": [{"Name": "WorkgroupName", "Value": "banking-workgroup"}],
            "AlarmActions": [topic_arn],
        },
    ]

    for alarm in alarms:
        client.put_metric_alarm(**alarm)
        print(f"Alarm created: {alarm['AlarmName']}")

    print("All CloudWatch alarms created successfully!")
    print(f"SNS Topic ARN: {topic_arn}")
    print("Add your email to receive alerts:")
    print(f"aws sns subscribe --topic-arn {topic_arn} --protocol email --notification-endpoint your@email.com")

if __name__ == "__main__":
    create_cloudwatch_alerts()
