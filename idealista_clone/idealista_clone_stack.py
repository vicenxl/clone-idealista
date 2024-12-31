from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_s3_notifications as s3_notifications,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
    aws_apigateway as apigateway,
    aws_iam as iam,
)
from constructs import Construct

class IdealistaCloneStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Bucket para imágenes
        bucket = s3.Bucket(self, "IdealistaImagesBucket", versioned=True,  )

        # SNS Topic para notificaciones por correo
        sns_topic = sns.Topic(self, "ImageUploadNotification")
        sns_topic.add_subscription(subscriptions.EmailSubscription("vdiaz@avaloninformatica.com"))

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
            function_name="process_image",
            runtime=_lambda.Runtime.NODEJS_22_X,
            handler="process_image.handler",
            code=_lambda.Code.from_asset("idealista_clone/src/lambda/process_image"),
            environment={
                "BUCKET_NAME": bucket.bucket_name,
                "SNS_TOPIC_ARN": sns_topic.topic_arn,
            },
        )

        # Asocia la Lambda al evento de subida de objetos en el bucket
        bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,  # Evento de subida de archivos
            s3_notifications.LambdaDestination(process_image_lambda),
            s3.NotificationKeyFilter(prefix="uploads/")
        )

        # Permisos para Lambda
        bucket.grant_read_write(process_image_lambda)
        sns_topic.grant_publish(process_image_lambda)

        # Lambda para manejar formularios de contacto
        contact_form_lambda = _lambda.Function(
            self,
            "ContactFormLambda",
            function_name="contact_form",
            runtime=_lambda.Runtime.NODEJS_22_X,
            handler="contact_form.handler",
            code=_lambda.Code.from_asset("idealista_clone/src/lambda/contact_form"),
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
