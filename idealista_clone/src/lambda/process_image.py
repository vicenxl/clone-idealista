import boto3
import os

def handler(event, context):
    s3_client = boto3.client("s3")
    sns_client = boto3.client("sns")
    bucket_name = os.environ["BUCKET_NAME"]
    sns_topic_arn = os.environ["SNS_TOPIC_ARN"]

    for record in event["Records"]:
        key = record["s3"]["object"]["key"]
        # Aquí procesarías la imagen y agregarías la marca de agua
        # Ejemplo: Descargar, modificar y subir
        response = s3_client.copy_object(
            Bucket=bucket_name,
            CopySource={"Bucket": bucket_name, "Key": key},
            Key=f"processed/{key}",
        )
        # Notificación
        sns_client.publish(
            TopicArn=sns_topic_arn,
            Subject="Imagen procesada",
            Message=f"La imagen {key} fue procesada y almacenada.",
        )
    return {"statusCode": 200, "body": "Procesamiento completado"}
