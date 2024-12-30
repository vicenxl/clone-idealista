import AWS from "aws-sdk";

const s3 = new AWS.S3();
const sns = new AWS.SNS();

export const handler = async (event) => {
  const bucketName = process.env.BUCKET_NAME;
  const snsTopicArn = process.env.SNS_TOPIC_ARN;

  try {
    for (const record of event.Records) {
      const key = record.s3.object.key;

      // Simulamos el procesamiento de la imagen
      console.log(`Processing image: ${key}`);
      const copyKey = `processed/${key}`;

      await s3.copyObject({
        Bucket: bucketName,
        CopySource: `${bucketName}/${key}`,
        Key: copyKey,
      }).promise();

      console.log(`Image processed and saved to ${copyKey}`);

      // Notificación a SNS
      await sns.publish({
        TopicArn: snsTopicArn,
        Subject: "Image Processed",
        Message: `Image ${key} has been processed and stored in ${copyKey}.`,
      }).promise();

      console.log("Notification sent");
    }

    return { statusCode: 200, body: "Processing complete" };
  } catch (error) {
    console.error("Error processing image:", error);
    return { statusCode: 500, body: "Error processing image" };
  }
};
