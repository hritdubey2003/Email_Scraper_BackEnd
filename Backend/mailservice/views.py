
# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from utils import custom_exceptions
from django.http import JsonResponse
from scrapyd_api import ScrapydAPI
from django.http import HttpResponse
import subprocess


import json
import os


# Create your views here.


def home( request ):
    return render(request, "index.html")
def ensure(request):
    try:
        if request.method != "GET":
            raise custom_exceptions.CustomError(f"Method - {request.method} is not Allowed")
        
        response = {"success": "true", "status": "online"}
        return JsonResponse(response)
    
    except Exception as e:
        return JsonResponse({"success":"false", "error":f"{e}"})
    
@csrf_exempt 
def mail_scrap(request):
    try:
        if request.method != "POST":
            raise custom_exceptions.CustomError(f"Method - {request.method} is not Allowed")
        
        req_data = json.loads(request.body.decode('utf-8'))
        print("Recieved Data in the backend!")
        for key in ["url", "keyword" , "Subject" , "Body" ]:
            if key not in req_data.keys():
                raise custom_exceptions.CustomError(f"The parameter {key} in JSON Body is missing")

        # Run the Scrapy spider using subprocess
        # process = subprocess.Popen(
        #     ['scrapy', 'crawl', 'email_spider'],
        #     stdout=subprocess.PIPE,
        #     stderr=subprocess.PIPE,
        #     cwd='C:/Users/hriti/Desktop/Mail_scrapper/Backend/emailtool'
        # )
        
        # stdout, stderr = process.communicate()
        
        with open('./emailtool/emailtool/spiders/log.json', 'w') as f:
            json.dump(req_data, f)
        f.close()

        # Connect to Scrapyd service
        scrapyd = ScrapydAPI('http://localhost:6800')
        # Schedule a new crawling task
        # task = scrapyd.schedule('default', 'email_spider')
        
        task = scrapyd.schedule('default', 'email_spider', settings={'url': req_data["url"], 'keyword': req_data["keyword"] , 'Subject': req_data["Subject"] , 'Body': req_data["Body"]  })
        
        return JsonResponse({"success":"true", "task_id":task})
    
    except Exception as e:
        return JsonResponse({"success":"false", "error":f"{e}"})
    

@csrf_exempt 
def download_email(request):
    try:
        if request.method != "GET":
            raise custom_exceptions.CustomError(f"Method - {request.method} is not Allowed")
        
        file_path = './emailtool/emails.csv'
        
        # Open the file and read its content
        with open(file_path, 'rb') as file:
            data = file.read()

        # Return the file content as an HTTP response
        response = HttpResponse(data, content_type='application/csv')
        response['Content-Disposition'] = 'attachment; filename="emails.csv"'
        return response
    
    except Exception as e:
        return JsonResponse({"success": "false", "error": str(e)})