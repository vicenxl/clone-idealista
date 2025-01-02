import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, PutCommand} from "@aws-sdk/lib-dynamodb";
import { SNSClient, PublishCommand } from "@aws-sdk/client-sns";

// Inicialización de clientes
const dynamoClient = new DynamoDBClient({});
const docClient = DynamoDBDocumentClient.from(dynamoClient);
const snsClient = new SNSClient({});

export const handler = async (event) => {
  const contactTable = process.env.CONTACT_TABLE;
  const snsTopicArn = process.env.SNS_TOPIC_ARN;

  console.log("Event received:", JSON.stringify(event));

  try {
    const data = JSON.parse(event.body);

    // Guardar en DynamoDB
    const putCommand = new PutCommand({
      TableName: contactTable,
      Item: data,
    });
    await docClient.send(putCommand);
    console.log("Contact data saved:", data);

    // Notificar a SNS
    const publishCommand = new PublishCommand({
      TopicArn: snsTopicArn,
      Subject: "New Contact Form Submission",
      Message: `New contact form submission: ${JSON.stringify(data)}`,
    });
    await snsClient.send(publishCommand);

    console.log("Notification sent");

    return { statusCode: 200, body: "Form submission successful" };
  } catch (error) {
    console.error("Error handling contact form:", error);
    return { statusCode: 500, body: "Error handling contact form" };
  }
};
