import AWS from "aws-sdk";

const dynamodb = new AWS.DynamoDB.DocumentClient();
const sns = new AWS.SNS();

export const handler = async (event) => {
  const contactTable = process.env.CONTACT_TABLE;
  const snsTopicArn = process.env.SNS_TOPIC_ARN;

  try {
    const data = JSON.parse(event.body);

    // Guardar en DynamoDB
    await dynamodb.put({
      TableName: contactTable,
      Item: data,
    }).promise();

    console.log("Contact data saved:", data);

    // Notificar a SNS
    await sns.publish({
      TopicArn: snsTopicArn,
      Subject: "New Contact Form Submission",
      Message: `New contact form submission: ${JSON.stringify(data)}`,
    }).promise();

    console.log("Notification sent");

    return { statusCode: 200, body: "Form submission successful" };
  } catch (error) {
    console.error("Error handling contact form:", error);
    return { statusCode: 500, body: "Error handling contact form" };
  }
};
