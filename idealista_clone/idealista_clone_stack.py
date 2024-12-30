from aws_cdk import (
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
    aws_apigateway as apigateway,
    aws_iam as iam,
)

class IdealistaCloneStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Bucket para imágenes
        bucket = s3.Bucket(self, "IdealistaImagesBucket", versioned=True,  )

        # SNS Topic para notificaciones por correo
        sns_topic = sns.Topic(self, "ImageUploadNotification")
        sns_topic.add_subscription(subscriptions.EmailSubscription("user@example.com"))

        # DynamoDB para almacenar datos de contacto
        contact_table = dynamodb.Table(
            self,
            "ContactTable",
            partition_key=dynamodb.Attribute(name="ad_id", type=dynamodb.AttributeType.STRING),
        )

        # Lambda para procesar imágenes y enviar notificaciones
        process_image_lambda = _lambda.Function(
            self,
            "ProcessImageLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="process_image.handler",
            code=_lambda.Code.from_asset("lambda_functions/process_image"),
            environment={
                "BUCKET_NAME": bucket.bucket_name,
                "SNS_TOPIC_ARN": sns_topic.topic_arn,
            },
        )

        # Permisos para Lambda
        bucket.grant_read_write(process_image_lambda)
        sns_topic.grant_publish(process_image_lambda)

        # Lambda para manejar formularios de contacto
        contact_form_lambda = _lambda.Function(
            self,
            "ContactFormLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="contact_form.handler",
            code=_lambda.Code.from_asset("lambda_functions/contact_form"),
            environment={
                "CONTACT_TABLE": contact_table.table_name,
                "SNS_TOPIC_ARN": sns_topic.topic_arn,
            },
        )

        # Permisos para Lambda
        contact_table.grant_read_write_data(contact_form_lambda)
        sns_topic.grant_publish(contact_form_lambda)

        # API Gateway para exponer los endpoints
        api = apigateway.RestApi(self, "IdealistaAPI")

        # Endpoint para subir imágenes
        image_upload = api.root.add_resource("upload")
        image_upload_lambda_integration = apigateway.LambdaIntegration(process_image_lambda)
        image_upload.add_method("POST", image_upload_lambda_integration)

        # Endpoint para enviar formulario de contacto
        contact_form = api.root.add_resource("contact")
        contact_form_lambda_integration = apigateway.LambdaIntegration(contact_form_lambda)
        contact_form.add_method("POST", contact_form_lambda_integration)
