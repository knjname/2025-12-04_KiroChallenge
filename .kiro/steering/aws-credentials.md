---
inclusion: always
---

# AWS Credentials Management

## Terminal Session Awareness

When running AWS CLI commands or CDK operations:

1. **Reuse existing terminals** whenever possible instead of creating new ones
2. If AWS credentials are needed and not available in the current terminal:
   - Prompt the user to provide their AWS credentials
   - Ask if they want to set environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN)
   - Or suggest they run `aws configure` or `aws sso login` manually
3. Before running AWS commands, check if credentials are available by running `aws sts get-caller-identity`
4. If credentials are missing, inform the user and ask them to authenticate before proceeding

## Common AWS Authentication Methods
- AWS SSO: `aws sso login --profile <profile-name>`
- AWS Configure: `aws configure`
- Environment variables: Export AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN
- IAM roles (for EC2/ECS/Lambda environments)

Always respect the user's preferred authentication method and avoid making assumptions about their AWS setup.
