import requests
from pprint import pprint
import json
import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

def txtanalyze():
    # Credential & Endpoint
    credential  = os.environ.get("credential")
    subscription_key = credential

    #get the blob storage details where the audio file is stored and where the converted text file has to be uploaded
    blob_connection_string = os.environ.get("blob_connection_string")
    blob_service_client = BlobServiceClient.from_connection_string(blob_connection_string)
    input_container_name = "output-text"
    output_container_name = "output-json"
    input_filename = "Diabetes interview 1.wav-converted.txt"
    blob_container_client = blob_service_client.get_container_client(container=input_container_name)
    blob_client = blob_service_client.get_blob_client(container=input_container_name, blob=input_filename)

    data = blob_client.download_blob()
    data = data.readall()
    data = data.decode()
    data = data.strip()
    str_text = data[:-5120]
    #print(str_text)
    #str_text = data.strip()

    #form the json string in the required structure to pass as the input to the api call
    myList = {"documents": [ {"language": "en", "id": "1", "text": str_text}]}
    jsonString = json.dumps(myList, indent=4)
    jsonString = json.loads(jsonString)
    documents = jsonString

   
    text_analytics_base_url = 'https://lyarvindtextanalyticsforhealthdemo.cognitiveservices.azure.com/text/analytics/v3.1/entities/health/jobs'

    post_results = requests.post(text_analytics_base_url, json = documents, headers={"Ocp-Apim-Subscription-Key": subscription_key}) 
    status_code = 0
    IsItStillRunning = True
    while IsItStillRunning:
        get_results = requests.get(post_results.headers["operation-location"], headers={"Ocp-Apim-Subscription-Key":subscription_key})
        print(get_results.status_code)
        IsItStillRunning = get_results.json()["status"] in ("running","notStarted")
        output = get_results.json()

    file_name = r"speech-to-text-nlp-output.json"
    json_output = json.dumps(output)

    input_filename_json = input_filename+r"-txt-analytics-out.json"
    def json_str_upload_to_blob(localfilename):
        blob = BlobClient.from_connection_string(conn_str=blob_connection_string, container_name=output_container_name, blob_name=input_filename_json)
        data = localfilename
        blob.upload_blob(data, overwrite=True)

    json_str_upload_to_blob(json_output)
    return output

