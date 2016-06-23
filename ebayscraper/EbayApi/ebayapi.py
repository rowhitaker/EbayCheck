# -*- coding: utf-8 -*-
import requests
import json

app_id = 'RickyWhi-EbayChec-PRD-65a6153ed-82a69392'
dev_id = 'c82144dc-8041-480e-9b5e-2d8d4c67ef09'
cert_id = 'SBX-5a63948ad0ad-8f6a-4ceb-8093-316a'

header_dict = {'X-EBAY-SOA-SECURITY-APPNAME': app_id,
               'X-EBAY-SOA-OPERATION-NAME': 'findItemsByKeywords',
               'X-EBAY-SOA-REQUEST-DATA-FORMAT': 'JSON',
               'X-EBAY-SOA-RESPONSE-DATA-FORMAT': 'JSON',
               'X-EBAY-SOA-SERVICE-VERSION': '1.0.0'}

variable_post_url = 'http://svcs.ebay.com/services/search/FindingService/v1'

final_request_dict = {'jsonns.xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                      'jsonns.xs': 'http://www.w3.org/2001/XMLSchema',
                      'jsonns.tns': 'http://www.ebay.com/marketplace/search/v1/services',
                      'tns.findItemsByKeywordsRequest': {'keywords': 'harry potter phoenix',
                                                         'paginationInput': {'entriesPerPage': 50,
                                                                             'pageNumber': 2}}}

body = json.dumps(final_request_dict)

s = requests.Session()
s.headers.update(header_dict)
r = s.post(url=variable_post_url, data=body)

return_json = json.loads(r.content)

return_dict = return_json['findItemsByKeywordsResponse'][0]

print return_dict