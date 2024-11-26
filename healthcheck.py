import requests
import yaml
import time
from urllib.parse import urlparse
import math

"""

This program checks the health of a set of HTTP endpoints. It reads an input argument from a file path with a list of HTTP endpoints in YAML format, 
tests the health of the endpoints in 15 second test cycles and displays results of the availability percentage of the HTTP root domains being monitored 
by the program.


The Program is broken into 4 functions.

file_check: Parses the YAML file, retrieves required data and appends to dictionary
endpoint_healthcheck: Takes collected data from dictionary and checks the Endpoint health. Sends URL, JSON and Headers as GET or POST. If status 200, counts.
health_check_results: Takes collected data from dictionary and combines root domain URLS and returns results in percentages.
get_base_url: verifies root domain for health_check_results

"""


def file_check(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)

        if not data or 'resources' not in data:                                                # validates data and file format
            raise ValueError("Invalid file format")
        
        check = []
        # Retrives required data from YAML file, stores in check dictionary.
        for resource in data['resources']:
            url = resource.get('url')
            headers = []
            headers = resource.get('headers')
            method = resource.get('method')
            body = resource.get('body')
            check.append({
                'url': url,
                'headers': headers,
                'method': method,
                'body': body,
            })

    endpoint_healthcheck(check)                                                                 # Sends dictionary to endpoint_healthcheck

def endpoint_healthcheck(urls):
    cycle_count = 0
    start_time = 0 
    data = []

    while True:                                                                                 # Loop that keeps program running until break (CTRL+C)
        
        print(f"Test cycle #{cycle_count + 1} at time = {start_time} seconds")                  # Starts Cycle test. Each cycle count increases by one, each start time increase by 15

        """
            FOR LOOP: 
                Loops through all items in the argument (url)
                        Sets up_count to 0
                        IF statements used to verifies:
                                If method is POST or GET
                                If item has url, body, headers or url, headers or url
                        Verifies status
                        Verifies Millisecond count. If greater than 600, automatically sets it as DOWN even if UP
                        Try and Except used to catch any RequestExceptions
        """
        for item in urls:
            method = item['method']
            up_count=0
            try:
                if method == 'POST':

                    if item['body'] and item['headers']:
                        response = requests.post(item['url'], json=item['body'], headers=item['headers'])
                    else:
                        response = requests.post(item['url'], headers=item['headers'])
                else:
                    if item['body'] and item['headers']:
                        response = requests.get(item['url'], data=item['body'], headers=item['headers'])
                    elif item['headers'] and not item['body']:
                        print(f"GET: {item['url']}, headers={item['headers']}")
                        response = requests.get(item['url'], headers=item['headers'])
                    else:
                        response = requests.get(item['url'])
                        

                if response and response.status_code // 100 == 2:
                    mseconds_check = response.elapsed.total_seconds() * 1000

                    if mseconds_check > 600:
                        print(f"Endpoint with the name {item['url']} has HTTP response code {response.status_code} and the response latency {math.ceil(mseconds_check)} => DOWN")
                    else:
                        up_count +=1
                        print(f"Endpoint with the name {item['url']} has HTTP response code {response.status_code} and the response latency {math.ceil(mseconds_check)} => UP")        

                else:
                    print(f"Endpoint with the name {item['url']} has HTTP response code {response.status_code} and the response latency {math.ceil(mseconds_check)} => DOWN")


            except requests.RequestException as e:
                print(f"Error checking {item['url']}: {e}")

            # Collects URL and Up Count totals for each URL ran through the Loop.
            data.append({
                "url": item['url'],
                "up_count": up_count,
            })

        cycle_count +=1                                                                             # Updates cycle Count for next Loop
        print(f"Test cycle #{cycle_count} ends. The program logs to the console:")                  # Prints End of Cycle Test
        health_check_results(data)                                                                  # Sends results (data dictionary) to health_check_reesults function
        start_time += 15                                                                            # Updates start time by 15 seconds

def health_check_results(data):
    combined_results={}
    
    """
        FOR LOOP:
            Loops through each item in data.
            creates variables for url and up count
            Uses get_base_url function to identify root domains
            combines all root domain urls as one along with up count metrics
            adds count to dictionary for percentage calculation
    """

    for item in data:
        base_url = get_base_url(item["url"])
        up_count = item["up_count"]

        if base_url in combined_results:
            combined_results[base_url]["up_count"] += up_count
            combined_results[base_url]["count"] += 1
           
        else:
            combined_results[base_url] = {"up_count": up_count, "count": 1}

    """
        FOR LOOP:
            Loops through combined results dictionary
            Creates variables for up count and count
            Identifies percentage (100 * (Number of HTTP requests that had an outcome of UP / number of HTTP
            requests))
            prints percentage results
    """

    for key, value in combined_results.items():
        uc = value['up_count']
        c = value['count']
        totals = 100 * uc / c
        
        print(f"{base_url} has {math.ceil(totals)} availability percentage")
    time.sleep(15)                                                                                  # stops the program for 15 seconds

def get_base_url(url):
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"

file_path = 'healthcheck.yaml'
config_data = file_check(file_path)