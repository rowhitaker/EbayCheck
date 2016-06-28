# -*- coding: utf-8 -*-
import requests
import json


class EbayItemFinder(object):
    def __init__(self):
        self.app_id = 'RickyWhi-EbayChec-PRD-65a6153ed-82a69392'
        self.dev_id = 'c82144dc-8041-480e-9b5e-2d8d4c67ef09'
        self.cert_id = 'SBX-5a63948ad0ad-8f6a-4ceb-8093-316a'

        self.header_dict = {'X-EBAY-SOA-SECURITY-APPNAME': self.app_id,
                            'X-EBAY-SOA-OPERATION-NAME': 'findItemsByKeywords',
                            'X-EBAY-SOA-REQUEST-DATA-FORMAT': 'JSON',
                            'X-EBAY-SOA-RESPONSE-DATA-FORMAT': 'JSON',
                            'X-EBAY-SOA-SERVICE-VERSION': '1.0.0'}
        self.variable_post_url = 'http://svcs.ebay.com/services/search/FindingService/v1'

        self.final_request_dict = {'jsonns.xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                                   'jsonns.xs': 'http://www.w3.org/2001/XMLSchema',
                                   'jsonns.tns': 'http://www.ebay.com/marketplace/search/v1/services',
                                   'tns.findItemsByKeywordsRequest': {'keywords': 'harry potter phoenix',
                                                                      'paginationInput': {'entriesPerPage': 50,
                                                                                          'pageNumber': 2}}}
        self.item_list = [
            {'sku': '4447801', 'title': 'VZW IPHONE 6S 64GB SPACE GRAY', 'totalMsrp': '799.99', 'brand': 'Apple',
             'upc': '8884625006', 'qty': '1', 'partNum': 'MKRY2LL/A', 'estMsrp': '799.99'},
            {'sku': '4447901', 'title': 'Apple - iPhone 6s 64GB - Gold (Verizon Wireless)', 'totalMsrp': '799.99',
             'brand': 'Apple', 'upc': '8884625006', 'qty': '1', 'partNum': 'MKT12LL/A', 'estMsrp': '799.99'},
            {'sku': '4447902', 'title': 'VZW IPHONE 6S 64GB ROSE GOLD', 'totalMsrp': '3999.95', 'brand': 'Apple',
             'upc': '8884625006', 'qty': '5', 'partNum': 'MKT22LL/A', 'estMsrp': '799.99'},
            {'sku': '4447501', 'title': 'VZW IPHONE 6S 16GB SPACE GRAY', 'totalMsrp': '6299.91', 'brand': 'Apple',
             'upc': '8884625006', 'qty': '9', 'partNum': 'MKRR2LL/A', 'estMsrp': '699.99'},
            {'sku': '4447601', 'title': 'VZW IPHONE 6S 16GB  SILVER', 'totalMsrp': '1399.98', 'brand': 'Apple',
             'upc': '8884625006', 'qty': '2', 'partNum': 'MKRT2LL/A', 'estMsrp': '699.99'},
            {'sku': '4447700', 'title': 'VZW IPHONE 6S 16GB  GOLD', 'totalMsrp': '699.99', 'brand': 'Apple',
             'upc': '8884625006', 'qty': '1', 'partNum': 'MKRW2LL/A', 'estMsrp': '699.99'},
            {'sku': '4447701', 'title': 'VZW IPHONE 6S 16GB  ROSE GOLD', 'totalMsrp': '4199.94', 'brand': 'Apple',
             'upc': '8884625006', 'qty': '6', 'partNum': 'MKRX2LL/A', 'estMsrp': '699.99'}]
        self.current_item = {}
        self.body = None
        self.return_data = []

    def build_json_request_dict(self):
        item_desc = '{} {}'.format(self.current_item.get('brand'), self.current_item.get('title'))
        current_request_dict = {'keywords': item_desc,
                                'paginationInput': {'entriesPerPage': 50,
                                                    'pageNumber': 2}}
        self.final_request_dict['tns.findItemsByKeywordsRequest'] = current_request_dict

    def make_requests(self):
        s = requests.Session()
        s.headers.update(self.header_dict)

        for self.current_item in self.item_list:
            self.build_json_request_dict()
            body = json.dumps(self.final_request_dict)

            r = s.post(url=self.variable_post_url, data=body)

            return_json = json.loads(r.content)

            return_dict = return_json['findItemsByKeywordsResponse'][0]


            print return_dict['paginationOutput'][0]['totalEntries']
            for this, that in return_dict.iteritems():
                print this, that
            # print return_dict.get('itemSearchURL')


if __name__ == "__main__":
    this = EbayItemFinder()
    this.make_requests()