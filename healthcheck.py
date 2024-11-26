import requests
import yaml
import time
from urllib.parse import urlparse
import math

def file_check(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)

        if not data or 'resources' not in data:
            raise ValueError("Invalid file format")
        
        check = []
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

    endpoint_healthcheck(check)

def endpoint_healthcheck(urls):
    cycle_count = 0
    start_time = 0 
    data = []

    while True:
        print(f"Test cycle #{cycle_count + 1} at time = {start_time} seconds")
        for item in urls:
            method = item['method']
            up_count=0
            try:
                if method == 'POST':
                    response = requests.post(item['url'], data=item['body'], headers=item['headers'])
                else:
                    response = requests.get(item['url'], data=item['body'], headers=item['headers'])

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
            data.append({
                "url": item['url'],
                "up_count": up_count,
            })

        cycle_count +=1
        print(f"Test cycle #{cycle_count} ends. The program logs to the console:")
        health_check_results(data)
        start_time += 15

def health_check_results(data):
    combined_results={}
    
    for item in data:
        base_url = get_base_url(item["url"])
        up_count = item["up_count"]

        if base_url in combined_results:
            combined_results[base_url]["up_count"] += up_count
            combined_results[base_url]["count"] += 1
           
        else:
            combined_results[base_url] = {"up_count": up_count, "count": 1}

    for key, value in combined_results.items():
        uc = value['up_count']
        c = value['count']
        totals = 100 * uc / c
        
        print(f"{base_url} has {math.ceil(totals)} availability percentage")
    time.sleep(15)

def get_base_url(url):
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"

file_path = 'healthcheck.yaml'
config_data = file_check(file_path)