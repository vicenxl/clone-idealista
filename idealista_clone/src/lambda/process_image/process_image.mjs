import { S3Client, CopyObjectCommand } from "@aws-sdk/client-s3";
import { SNSClient, PublishCommand } from "@aws-sdk/client-sns";

const s3 = new S3Client();
const sns = new SNSClient();

export const handler = async (event) => {
  const bucketName = process.env.BUCKET_NAME;
  const snsTopicArn = process.env.SNS_TOPIC_ARN;
  const allowedExtensions = [".jpg", ".png"];

  console.log("Event received:", JSON.stringify(event));
  try {
    for (const record of event.Records) {
      const key = record.s3.object.key;

      // Filtrar extensiones
      if (!allowedExtensions.some((ext) => key.endsWith(ext))) {
        console.log(`File ${key} does not match allowed extensions.`);
        continue; // Ignora archivos no válidos
      }

      // Verificar si el archivo ya está en el directorio 'processed/'
      if (key.startsWith("processed/")) {
        console.log(`File ${key} is already processed. Skipping.`);
        continue; // Ignorar este archivo
      }

      // Simulamos el procesamiento de la imagen
      console.log(`Processing image: ${key}`);
      const copyKey = `processed/${key}`;

      // Ejecutar el comando de copia de objeto
      const copyCommand = new CopyObjectCommand({
        Bucket: bucketName,
        CopySource: `${bucketName}/${key}`,
        Key: copyKey,
      });
      await s3.send(copyCommand);

      console.log(`Image processed and saved to ${copyKey}`);

      // Notificación a SNS
      const publishCommand = new PublishCommand({
        TopicArn: snsTopicArn,
        Subject: "Image Processed",
        Message: `Image ${key} has been processed and stored in ${copyKey}.`,
      });
      await sns.send(publishCommand);

      console.log("Notification sent");
    }

    return { statusCode: 200, body: "Processing complete" };
  } catch (error) {
    console.error("Error processing image:", error);
    return { statusCode: 500, body: "Error processing image" };
  }
};
