import requests
import yaml
import time
from urllib.parse import urlparse
import math


def file_check(file_path):
    """Parse the YAML file and extract resources."""
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
        if not data or 'resources' not in data:
            raise ValueError("Invalid file format")

        return [
            {
                'url': resource.get('url'),
                'headers': resource.get('headers', {}),
                'method': resource.get('method', 'GET'),
                'body': resource.get('body', None),
            }
            for resource in data['resources']
        ]


def send_request(item):
    """Send HTTP request based on the resource configuration."""
    try:
        if item['method'] == 'POST':
            return requests.post(item['url'], json=item['body'], headers=item['headers'])
        return requests.get(item['url'], headers=item['headers'])
    except requests.RequestException as e:
        print(f"Error with {item['url']}: {e}")
        return None


def endpoint_healthcheck(resources, test_cycles=None):
    """Check the health of endpoints in test cycles."""
    cycle_count = 0
    results = {}

    try:
        while test_cycles is None or cycle_count < test_cycles:
            print(f"Starting test cycle #{cycle_count + 1}")
            for resource in resources:
                response = send_request(resource)
                url = resource['url']
                base_url = get_base_url(url)
                latency = response.elapsed.total_seconds() * 1000 if response else None

                # Initialize base_url data
                if base_url not in results:
                    results[base_url] = {'up_count': 0, 'total_count': 0}

                if response and response.status_code // 100 == 2 and (latency <= 500 if latency is not None else False):
                    results[base_url]['up_count'] += 1
                    print(f"{url} is UP. Status: {response.status_code}, Latency: {math.ceil(latency)}ms")
                else:
                    print(f"{url} is DOWN. Status: {response.status_code if response else 'N/A'}, Latency: {math.ceil(latency) if latency is not None else 'N/A'}ms")

                results[base_url]['total_count'] += 1

            health_check_results(results)
            cycle_count += 1
            print(f"End of test cycle #{cycle_count}. Waiting for 15 seconds...")
            time.sleep(15)

    except KeyboardInterrupt:
        print("Program interrupted. Stopping gracefully.")


def health_check_results(results):
    """Calculate and log the availability percentages."""
    print("Current Availability Results:")
    for base_url, data in results.items():
        availability = 100 * data['up_count'] / data['total_count']
        print(f"{base_url}: {availability:.2f}% availability")


def get_base_url(url):
    """Extract the base URL from a full URL."""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


if __name__ == "__main__":
    file_path = 'local_healthcheck.yaml'
    resources = file_check(file_path)
    endpoint_healthcheck(resources, test_cycles=None)  # Set test_cycles=N for N cycles, or None for infinite.
