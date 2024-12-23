# HTTP Endpoint Healthcheck

## About this Project

> This program checks the health of a set of HTTP endpoints. It reads an input argument from a file path with a list of HTTP endpoints in YAML format, tests the health of the endpoints in 15 second test cycles and displays results of the UP availability percentage of the HTTP root domains being monitored by the program.

## Built with

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

## Getting Started

### Prerequisites

>The following are the prequisites to run this program. It is assumed that these are configured prior to running the program.

- IDE (such as VsCode)
- Python 3.12.6
- virtual environment

### Installation

1. clone the repo

   ```sh
   git clone https://github.com/Connaker/http_endpoints_healthcheck.git
   ```

2. Start your virtual environment

   ```sh
   macOS: source .\venv\Scripts\activate <br>
   Windows: .\venv\Scripts\activate
   ```

3. Install requiremetns.txt

   ```sh
   pip install -r requirements.txt
   ```

### Update healthcheck.yaml

>Update healthcheck.yaml with Header fields, Body message, method, name and url. Header fields are seperated by colon, key-value pairs in clear-text string format. For this program, Body uses the JSON format. Url is the url of the website you are testing. For this program, method is either GET or POST.

   ```sh
   Example 1:
     - headers:
         user-agent: useragent
       method: GET
       name: Fetch test page
       url: https://example.com/test

   Example 2:
     - body: '{"foo":"bar"}'
       headers:
         content-type: applicaiton/json
         user-agent: useragent
       method: POST
       name: fetch some fake post endpoint
       url: https://example.com
   
   Example 3:
     - name: fetch index page
       url: https://example.com
   ```

### Usage

> to run the program, use `python healtcheck.py`. The program will continue to run until you stop it by using `CTRL+C` at which time the program will exit.

### Notes

> The program is designed to automatically fail any HTTP endpoints with a millisecond greater than 500. It is designed to send both Headers and Data(Body).
