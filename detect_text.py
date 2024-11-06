import text_wrapper
import boto3
import requests
# session = boto3.Session(
#   aws_access_key_id="",
#   aws_secret_access_key="",
# )

s3 = session.client('s3')
textract_client = session.client('textract')
in_status = False
out_status = False
net_status = False

in_value = 0
out_value = 0
net_value = 0

def check_int(text):
  if "," in text:
    text = text.replace(",", "")
  try:
    int(text)
    return True
  except:
    return False

def detect_text(event):
  in_status = False
  out_status = False
  net_status = False

  in_value = 0
  out_value = 0
  net_value = 0
  obj = s3.get_object(Bucket=event['Records'][0]['s3']['bucket']['name'], Key=event['Records'][0]['s3']['object']['key'])
  data = text_wrapper.TextractWrapper(textract_client).detect_file_text(document_bytes=obj['Body'].read())
  blocks = []
  for block in data['Blocks']:
    if block['BlockType'] != 'PAGE':
      blocks.append(block['Text'])
# print(blocks)

  for i in range(1, len(blocks)):
    if "In:" in blocks[i]:
      if in_status == False:
        if check_int(blocks[i+1]):
          print(f"{blocks[i]} {blocks[i+1]}")
          in_status = True
          in_value = blocks[i+1]
    elif "Out:" in blocks[i]:
      if out_status == False:
        if check_int(blocks[i+1]):
          print(f"{blocks[i]} {blocks[i+1]}")
          out_status = True
          out_value = blocks[i+1]
    elif "Net" in blocks[i]:
      if net_status == False:
        if check_int(blocks[i+1]):
          if i + 1 < len(blocks):
            print(f"{blocks[i]} {blocks[i+1]}")
            net_status = True
            net_value = blocks[i+1]
        elif check_int(blocks[i+2]):
          if i + 2 < len(blocks):
            print(f"{blocks[i]} {blocks[i+1]} {blocks[i+2]}")
            net_status = True
            net_value = blocks[i+2]
  print(blocks)
  if in_status and out_status and net_status:
    requests.post("", json={
      "in": in_value,
      "out": out_value,
      "net": net_value
    })

def lambda_handler(event, context):
  detect_text(event)
  return {
    'statusCode': 200,
    'body': 'Text detected successfully'
  }
