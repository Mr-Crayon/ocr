import text_wrapper
import boto3
import requests
# session = boto3.Session(
#   aws_access_key_id="",
#   aws_secret_access_key="",
# )

# Initialize the clients
s3 = session.client('s3')
textract_client = session.client('textract')


def check_int(text): # Check if the text is an integer
  if "," in text:
    text = text.replace(",", "")
  try:
    int(text)
    return True
  except:
    return False

def detect_text(event): # Detect the text in the file
  ## Statuses to cover all the text we need to collect
  in_status = False
  out_status = False
  net_status = False
  ticket_status = False
  load_slip_status = False
  truck_company_status = False

  ## Initial values
  in_value = 0
  out_value = 0
  net_value = 0
  ticket_value = 0
  load_slip_value = 0
  blocks = []
  truck_company_value = ""
  
  # Truck companies
  truck_companies = ["Dowless Trucking", "Lee Dowless Trucking", "Bettendorf Trucking", "Ron Bowers Inc", "JNB Trucking", "Casey Cooper Trucking"]

  ## Get the file from S3
  obj = s3.get_object(Bucket=event['Records'][0]['s3']['bucket']['name'], Key=event['Records'][0]['s3']['object']['key'])
 
  ## Detect the text in the file
  data = text_wrapper.TextractWrapper(textract_client).detect_file_text(document_bytes=obj['Body'].read())

  ## Add the text to the blocks list
  for block in data['Blocks']:
    if block['BlockType'] != 'PAGE':
      blocks.append(block['Text'])

  ## Iterate through the blocks to collect the text we need
  for i in range(1, len(blocks)):
    if "In:" in blocks[i]:
      if in_status == False:
        if check_int(blocks[i+1]):
          in_status = True
          in_value = blocks[i+1]
    elif "Out:" in blocks[i]:
      if out_status == False:
        if check_int(blocks[i+1]):
          out_status = True
          out_value = blocks[i+1]
    elif "Net" in blocks[i]:
      if net_status == False:
        if check_int(blocks[i+1]):
          if i + 1 < len(blocks):
            net_status = True
            net_value = blocks[i+1]
        elif check_int(blocks[i+2]):
          if i + 2 < len(blocks):
            net_status = True
            net_value = blocks[i+2]
    elif "Ticket" in blocks[i]:
      if ticket_status == False:
        if blocks[i] == "Ticket #:":
          if check_int(blocks[i+1]):
            ticket_status = True
            ticket_value = blocks[i+1]
        elif "#:" in blocks[i+1]:
          if check_int(blocks[i+2]):
            ticket_status = True
            ticket_value = blocks[i+2]
        else:
          ticket_block_split = blocks[i].split(" ")
          if ticket_block_split[0] == "Ticket":
            if ticket_block_split[1] == "#:":
              if check_int(ticket_block_split[2]):
                ticket_status = True
                ticket_value = ticket_block_split[2]
    elif "Slip:" in blocks[i]:
      if load_slip_status == False:
        if "Load".lower() in blocks[i].lower() or "Load".lower() in blocks[i-1].lower():
          if check_int(blocks[i+1]):
            load_slip_status = True
          load_slip_value = blocks[i+1]
    elif "BOL#:" in blocks[i]:
      if load_slip_status == False:
        if check_int(blocks[i+1]):
          load_slip_status = True
          load_slip_value = blocks[i+1]
    elif "Dowless".lower() in blocks[i].lower():
      if truck_company_status == False:
        if "Lee".lower() in blocks[i-1].lower() or "Lee".lower() in blocks[i].lower():
          truck_company_status = True
          truck_company_value = "Lee Dowless Trucking"
        else:
          truck_company_status = True
          truck_company_value = "Dowless Trucking"
    elif "Bettendorf".lower() in blocks[i].lower():
      if truck_company_status == False:
        truck_company_status = True
        truck_company_value = "Bettendorf Trucking"
    elif "Bowers".lower() in blocks[i].lower():
      if truck_company_status == False:
        truck_company_status = True
        truck_company_value = "Ron Bowers Inc"
    elif "JNB".lower() in blocks[i].lower():
      if truck_company_status == False:
        truck_company_status = True
        truck_company_value = "JNB Trucking"
    elif "Cooper".lower() in blocks[i].lower():
      if truck_company_status == False:
        truck_company_status = True
        truck_company_value = "Casey Cooper Trucking"

  ## If all the necessary values are collected, send them to the API
  requests.post("", json={
    "file_name": event['Records'][0]['s3']['object']['key'],
    "in": in_value,
    "out": out_value,
    "net": net_value,
    "ticket": ticket_value,
    "load_slip": load_slip_value,
    "truck_company": truck_company_value
  })

def lambda_handler(event, context):
    ## Statuses to cover all the text we need to collect
  in_status = False
  out_status = False
  net_status = False
  ticket_status = False
  load_slip_status = False
  truck_company_status = False

  ## Initial values
  in_value = 0
  out_value = 0
  net_value = 0
  ticket_value = 0
  load_slip_value = 0
  blocks = []
  truck_company_value = ""
  detect_text(event)
  return {
    'statusCode': 200,
    'body': 'Text detected successfully'
  }
