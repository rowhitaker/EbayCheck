import requests


app_id = 'RickyWhi-EbayChec-SBX-55a63948a-3a217a11'
dev_id = 'c82144dc-8041-480e-9b5e-2d8d4c67ef09'
cert_id = 'SBX-5a63948ad0ad-8f6a-4ceb-8093-316a'

# base_url = 'http://open.api.ebay.com/shopping'
base_url = 'https://api.sandbox.ebay.com/ws/api.dll'
response_encoding = 'XML'  # also JSON, SOAP

full_get_url = '{0}/shopping?callname=FindProducts&responseencoding={1}&appid={2}&siteid=0&version=525&QueryKeywords=harry%20potter&MaxEntries=2'.format(base_url, response_encoding, app_id)

full_get_url = 'http://open.api.ebay.com/shopping?callname=FindProducts&responseencoding=XML&appid=RickyWhi-EbayChec-PRD-65a6153ed-82a69392&siteid=0&version=525&QueryKeywords=harry%20potter&AvailableItemsOnly=true&MaxEntries=2'
print 'full get url: {}'.format(full_get_url)

r = requests.get(full_get_url)


'''

http://open.api.ebay.com/shopping?callname=FindProducts
responseencoding=XML
appid=YourAppIDHere
siteid=0
version=525
QueryKeywords=harry%20potter
AvailableItemsOnly=true
MaxEntries=2
'''

print r.content
print r.headers
print r.cookies
print r.status_code


body_xml = """
<?xml version="1.0" encoding="utf-8"?>
<FindProductsRequest xmlns="urn:ebay:apis:eBLBaseComponents">
  <QueryKeywords>Harry Potter</QueryKeywords>
</FindProductsRequest>
"""

s = requests.post(url=base_url, data=body_xml)

print r.content
print r.headers
print r.cookies
print r.status_code



