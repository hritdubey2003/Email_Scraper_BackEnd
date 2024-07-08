import scrapy
import re
import pymongo
import csv
import smtplib
import ssl
import json
import os


class EmailSpider(scrapy.Spider):
    name = 'email_spider'

    def __init__(self, *args, **kwargs):
        super(EmailSpider, self).__init__(*args, **kwargs)
        # Connecting to MongoDb
        self.mongo_uri = 'mongodb://localhost:27017/'
        self.mongo_db = 'Employee'
        self.mongo_collection = 'emails'
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

        # Creating a new csv file and then adding the email and the url in a row
        self.csv_file = open('emails.csv', 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(['Email', 'URL'])

    def closed(self, reason):
        # Closing the connection from the MongoDB and closing the csv file
        self.client.close()
        self.csv_file.close()

    def sendemail( self , receiver_email , subject , message ):
        smtp_port = 587
        smtp_server = "smtp.gmail.com"

        #email_from = input("Enter your email:")
        #pswd = input("Enter the password:")
        
        email_from = "ece21128@iiitkalyani.ac.in"

        pswd = ""


        email_text = f"Subject: {subject}\n\n{message}"

        simple_email_context = ssl.create_default_context()
        try:
           print("connecting to server.....")
           TIE_server = smtplib.SMTP( smtp_server , smtp_port )
           TIE_server.starttls( context = simple_email_context )
           TIE_server.login( email_from , pswd )
           print("Connected to the server...")

           print()
           print(f"Sending email to - { receiver_email }")
           TIE_server.sendmail( email_from , receiver_email , email_text )
           print(f"Email successfully sent to - { receiver_email }")

        except Exception as e:
           print(e)

        finally:
           TIE_server.quit()

    def start_requests(self):
        # URLS array for scrapping the results
        #url = self.settings.get('url')
        
        url = ''
        print("Initiated re data resp", end="\n\n\n\n")
        print(os.getcwd())
        
        try:
            with open('./emailtool/spiders/log.json', 'r') as f:
                print("File opened")
                req_data = json.load(f)
                keyword = req_data['keyword']
                print("Initiated re data resp", req_data, end="\n\n\n\n")                
            f.close()
        except Exception as e:
            print(e)
        
        
        url = f'https://www.googleapis.com/customsearch/v1?key=AIzaSyB4dnSFOXIY2o6Ujl-wD212RlxklfrlNyo&cx=c0efd18568f864abd&q={keyword}'
        yield scrapy.Request(url=url , callback=self.link_extractor )
        with open('./emailtool/spiders/log.json', 'r') as f:
                req_data = json.load(f)
                url = req_data['url']
        f.close()
       


    def link_extractor( self , response ):
        links = self.extract_urls( response.text.lower() )
        for link in links:
            print(link)
            yield scrapy.Request(url=link , callback=self.parse )
           

    def parse(self, response):
        keyword = ""
        with open('./emailtool/spiders/log.json', 'r') as f:
            req_data = json.load(f)
            keyword = req_data['keyword']
            subject = req_data['Subject']
            message = req_data['Body']
        f.close()
        # keyword = self.settings.get("keyword")  # Specify your keyword here
        # Check if the keyword is present in the response body
        if keyword.lower() in response.text.lower():
            # Extract email addresses using regex regular expression
            val = response.text
            print(val)
            emails = self.extract_emails(response.text)
            for email in emails:
                # Save email to MongoDB
                self.save_to_mongodb(email, response.url)
                # Write email to CSV file
                self.csv_writer.writerow([email, response.url])

#                 subject = "Hello Folks! Hiring for the PHP developer!"
#                 message = """ 
# Dear Folk,

#             I hope this email finds you well. I am writing to inform you about an exciting job opportunity for the position of PHP Developer at UMID Infotech.

#             UMID Infotech is a dynamic and innovative company that specializes in [brief description of company]. We are currently expanding our team and are seeking a talented PHP Developer to join us in creating cutting-edge web applications and solutions.
# Role: PHP Developer
# Location: [Location]
# Employment Type: [Full-time/Part-time/Contract]
# Salary: [Salary Range]

# Key Responsibilities:
# - Develop, test, and maintain PHP-based web applications
# - Collaborate with cross-functional teams to design and implement new features
# - Optimize application performance and scalability
# - Troubleshoot and debug issues to ensure seamless operation
# - Stay updated with industry trends and best practices

# Requirements:
# - Bachelor's degree in Computer Science, Engineering, or related field
# - Proven experience as a PHP Developer or similar role
# - Strong understanding of PHP, HTML, CSS, JavaScript, and related technologies
# - Experience with frameworks such as Laravel, Symfony, etc.
# - Familiarity with database systems (MySQL, PostgreSQL, etc.)
# - Excellent problem-solving and communication skills

# At UMID Infotech, we offer a vibrant work environment, opportunities for growth and development, and competitive compensation packages.

# If you are passionate about web development and want to be part of a dynamic team driving innovation, we would love to hear from you. Please send your resume and cover letter to [Contact Email/Link].

# Thank you for considering this opportunity. We look forward to hearing from you soon.

# Best regards,

# Hritik Dubey
# 
# UMID Infotech
# [Contact Information]"""
                self.sendemail( email , subject , message= message )
    

    def extract_emails(self, text):
        # Regular expression pattern to extract email addresses
        pattern = r'[\w\.-]+@[\w\.-]+'
        return re.findall(pattern, text)

    def extract_urls( self , text ):
        pattern = r"\bhttps?://\S+"
        return re.findall(pattern, text)

    def save_to_mongodb(self, email, url):
        # Insert email into MongoDB
        self.db[self.mongo_collection].insert_one({
            'email': email,
            'url': url
        })
