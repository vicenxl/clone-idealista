# IdealistaCloneStack CDK Project

This project is an AWS Cloud Development Kit (CDK) application written in Python. It provisions an infrastructure that includes S3, DynamoDB, SNS, Lambda, and API Gateway to build a scalable backend for a property listing clone application.

## Table of Contents

- [IdealistaCloneStack CDK Project](#idealistaclonestack-cdk-project)
  - [Table of Contents](#table-of-contents)
  - [Project Overview](#project-overview)
  - [Architecture](#architecture)
  - [Prerequisites](#prerequisites)
  - [Setup](#setup)
  - [Deploy](#deploy)
  - [Usage](#usage)
    - [Endpoints](#endpoints)
    - [Environment Variables](#environment-variables)
  - [Cleanup](#cleanup)
  - [License](#license)

## Project Overview

The `IdealistaCloneStack` sets up the following resources:
- **S3 Bucket**: For storing property images with versioning enabled.
- **SNS Topic**: To send email notifications on image uploads.
- **DynamoDB Table**: To store contact form data.
- **Lambda Functions**:
  - `process_image`: Processes uploaded images and triggers SNS notifications.
  - `contact_form`: Handles user contact form submissions.
- **API Gateway**: Exposes REST API endpoints for image upload and contact form submission.

## Architecture

![Architecture Diagram](https://source.unsplash.com/random/800x400?architecture)

1. Users upload images to the S3 bucket.
2. The `process_image` Lambda is triggered by new uploads and sends notifications via SNS.
3. Users submit contact forms via the API Gateway, which triggers the `contact_form` Lambda to save data in DynamoDB.

## Prerequisites

1. Install [AWS CDK CLI](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html#aws_cdk_prerequisites).
2. Python 3.9+.
3. Node.js 14+ for Lambda runtime compatibility.
4. AWS CLI configured with appropriate credentials.

## Setup

1. Clone the repository:
    ```bash
    git clone https://github.com/your-repo/idealista-clone.git
    cd idealista-clone
    ```
2. Install dependencies:
    ```bash
    python -m venv .env
    source .env/bin/activate # On Windows use .env\Scripts\activate
    pip install -r requirements.txt
    ```

## Deploy

1. Bootstrap your AWS environment if not already done:
    ```bash
    cdk bootstrap
    ```
2. Deploy the stack:
    ```bash
    cdk deploy
    ```

## Usage

### Endpoints

1. **Image Upload**:
   - **POST** `/upload`
   - Body: `{ "image": <Base64EncodedImage> }`
2. **Contact Form Submission**:
   - **POST** `/contact`
   - Body: `{ "ad_id": "<AdID>", "message": "<Message>", "email": "<UserEmail>" }`

### Environment Variables

- `BUCKET_NAME`: The name of the S3 bucket for image storage.
- `SNS_TOPIC_ARN`: The ARN of the SNS topic for notifications.
- `CONTACT_TABLE`: The name of the DynamoDB table for contact data.

## Cleanup

To delete the stack:
```bash
cdk destroy
```

## License

This project is licensed under the MIT License. See the LICENSE file for details.
