import os
import json
import boto3
from apryse_sdk.PDFNetPython import PDFDoc, PDFNet, SDFDoc
from botocore.exceptions import ClientError

from models import PDFData

# Initialize the S3 and DynamoDB clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')


def fill_pdf_worker(template_path: str, output_path: str, pdf_data: PDFData) -> None:
    """Fill PDF form fields with data and save the output PDF."""
    license_key = os.getenv('APRYSE_LICENSE_KEY')
    PDFNet.Initialize(license_key)

    doc = PDFDoc(template_path)

    pdf_form_dict = pdf_data.to_form_schema_dict()

    for field_name, field_val in pdf_form_dict.items():
        field = doc.GetField(field_name)
        if field:
            field.SetValue(field_val)
            field.RefreshAppearance()

    doc.FlattenAnnotations()
    doc.Save(output_path, SDFDoc.e_linearized)
    doc.Close()


def download_template_from_s3(bucket: str, key: str, download_path: str) -> None:
    """Download a file from S3 to a specified local path."""
    try:
        s3_client.download_file(bucket, key, download_path)
    except ClientError as e:
        raise Exception(f'Error downloading template: {e}')


def upload_filled_pdf_to_s3(bucket: str, key: str, upload_path: str) -> None:
    """Upload a file to S3 from a specified local path."""
    try:
        s3_client.upload_file(upload_path, bucket, key)
    except ClientError as e:
        raise Exception(f'Error uploading filled PDF: {e}')


def update_dynamodb_record(table_name: str, user_id: str, pdf_path: str) -> None:
    """Update the DynamoDB record with the PDF path."""
    table = dynamodb.Table(table_name)
    try:
        table.update_item(
            Key={'userId': user_id},
            UpdateExpression='SET pdf_path = :val1',
            ExpressionAttributeValues={':val1': pdf_path},
        )
    except ClientError as e:
        raise Exception(f'Error updating DynamoDB: {e}')


def fill_pdf(event, context):
    """Lambda handler function to fill a PDF form and upload it to S3."""
    _ = context
    # Fetch query parameters
    query_params = event.get('queryStringParameters', {})
    owner_id = query_params.get('ownerId', None)

    # Fetch request body
    pdf_data_dict_str = event.get('body', '{}')
    pdf_data_dict = json.loads(pdf_data_dict_str)

    if not owner_id or not pdf_data_dict:
        return {
            'statusCode': 400,
            'body': json.dumps('Missing required parameters: user_id, template_key, or pdf_data'),
        }

    pdf_data = PDFData(**pdf_data_dict)

    input_bucket = 'dev-template-pdfs-01j2ktf90m3ansb11x0xmj13d6'
    output_bucket = 'dev-user-pdfs-01j2ktf90m3ansb11x0xmj13d6'
    dynamodb_table_name = 'users'

    template_key = 'sample.pdf'
    template_path = '/tmp/template.pdf'
    output_path = f'/tmp/output_{owner_id}.pdf'
    output_key = f'filled_pdfs/{owner_id}.pdf'
    pdf_s3_path = f's3://{output_bucket}/{output_key}'

    try:
        download_template_from_s3(input_bucket, template_key, template_path)
        fill_pdf_worker(template_path, output_path, pdf_data)
        upload_filled_pdf_to_s3(output_bucket, output_key, output_path)
        update_dynamodb_record(dynamodb_table_name, owner_id, pdf_s3_path)
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps(str(e))}

    return {
        'statusCode': 200,
        'body': json.dumps(f'PDF successfully processed and stored at {pdf_s3_path}'),
    }
