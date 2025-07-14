# 🔎 AWS Cross-Account EC2 Stopped Instances Finder

This Python script uses AWS Organizations and STS AssumeRole to **enumerate all active accounts in your AWS Organization**, then **lists all stopped EC2 instances** in every enabled region of those accounts.

It writes the results to a JSON file for easy auditing or further processing.

---

## 📜 Features

✅ Assumes cross-account roles into all active AWS accounts  
✅ Lists all AWS regions enabled in each account  
✅ Finds all stopped EC2 instances  
✅ Saves output to `StoppedInstances.json` in JSON format  
✅ Supports pagination for large numbers of instances  

---

## ⚙️ Requirements

- Python 3.7+
- [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- AWS credentials with permission to:
  - AssumeRole into target accounts
  - `organizations:ListAccounts`
  - `ec2:DescribeRegions`
  - `ec2:DescribeInstances`

---

## 📦 Installation

```bash
pip install boto3
