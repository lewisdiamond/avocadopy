import requests
import json
import urllib
import uuid
import re
try:
    from urllib.parse import urljoin
    from urllib.parse import urlsplit
except ImportError:
    from urlparse import urljoin
    from urlparse import urlsplit

class Response(object):
    def __init__(self, headers=None, status_code=None, body=None):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def json(self):
        return json.loads(self.body)


def request_to_string(request, client_id=None):
    part_headers = {'Content-type': 'application/x-arango-batchpart'}
    if client_id is not None:
        part_headers['Client-Id'] = client_id
    x = '\r\n'.join('{}: {}'.format(k, v) for k, v in request.headers.items())
    url_path = urlsplit(request.url)[2]
    return '{part_headers}\r\n\r\n{request}{headers}{body}'.format(
        part_headers='\n\r'.join('{}: {}'.format(k, v) for k, v in part_headers.items())
        ,request='{} {} {}'.format(request.method, url_path, 'HTTP/1.1')
        ,headers='\r\n' + '\r\n'.join('{}: {}'.format(k, v) for k, v in request.headers.items())
        ,body=('\r\n\r\n' + request.body) if request.body is not None else '',
    )


def create_batch(request_list, base_url):
    batch_url = urljoin(base_url, '_api/batch')
    part_delim = str(uuid.uuid4())
    content_id = range(len(request_list))
    content_id.reverse()
    data = '\r\n'.join('--{delim}\r\n{req}'.format(delim=part_delim, req=request_to_string(r, content_id.pop())) for r in request_list)
    data = data + '--{delim}--'.format(delim=part_delim)
    req = requests.Request('POST',
        batch_url,
        data=data,
        headers={
            "Content-Type": "multipart/form-data; boundary=" + part_delim
        },
    ).prepare()
    return req

def extract_batch_responses(response):
    responses = []
    try:
        boundary = re.search('(?:.|\s)*boundary=(?P<boundary>.*)\s*$', response.headers['content-type']).group('boundary')
        text = response.text
        response_text = text.split(boundary)[1:-1]
        for t in response_text:
            response_parts = re.search('\r\n(?P<wrapper_headers>.*?)\r\n\r\n(?P<http>.*?)\r\n(?P<headers>(.|\r\n)*?)\r\n\r\n(?P<body>(.|\s)*?)\r\n--'.format(boundary=boundary), t)
            headers = {k.split(':')[0].strip(): k.split(':')[1].strip() for k in response_parts.group('headers').split('\r\n')}
            status_code = int(response_parts.group('http').split(' ')[1])
            response = Response(headers=headers, status_code=status_code, body=response_parts.group('body'))
            try:
                response['json'] = json.loads(response_parts.group('body'))
            except:
                pass
            responses.append(response)

    except:
        pass
    return responses



