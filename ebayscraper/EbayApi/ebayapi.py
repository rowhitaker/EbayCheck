# -*- coding: utf-8 -*-
import requests
import json
import logging
import time


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
        # self.item_list = [{'sku': '4917304', 'title': 'SAMSUNG GEARS2 CLASSIC PREMIUM RS GLD', 'totalMsrp': '449.99',
        #                    'brand': 'Samsung', 'upc': '8872761394', 'qty': '1', 'partNum': 'SM-R7320ZDAXAR',
        #                    'estMsrp': '449.99'},
        #                   {'sku': '4917304', 'title': 'SAMSUNG GEARS2 CLASSIC PREMIUM RS GLD', 'totalMsrp': '449.99',
        #                    'brand': 'Samsung', 'upc': '8872761394', 'qty': '1', 'partNum': 'SM-R7320ZDAXAR',
        #                    'estMsrp': '449.99'},
        #                   {'sku': '4637900', 'title': 'VZW GEAR S2 CONNECTED/LTE, BLACK', 'totalMsrp': '349.99',
        #                    'brand': 'Samsung', 'upc': '8872761245', 'qty': '1', 'partNum': 'SM-R730VZKAVZW',
        #                    'estMsrp': '349.99'}, {'sku': '4472000',
        #                                           'title': 'Samsung - Gear S2 Classic Smartwatch 40mm Stainless Steel - Black Leather',
        #                                           'totalMsrp': '1049.97', 'brand': 'Samsung', 'upc': '8872761264',
        #                                           'qty': '3', 'partNum': 'SM-R7320ZKAXAR', 'estMsrp': '349.99'},
        #                   {'sku': '4471702',
        #                    'title': 'Samsung - Gear S2 Smartwatch 42mm Stainless Steel - Black Elastomer',
        #                    'totalMsrp': '2999.90', 'brand': 'Samsung', 'upc': '8872761228', 'qty': '10',
        #                    'partNum': 'SM-R7200ZKAXAR', 'estMsrp': '299.99'}, {'sku': '4471900',
        #                                                                        'title': 'Samsung - Gear S2 Smartwatch 42mm Stainless Steel - White Elastomer',
        #                                                                        'totalMsrp': '299.99',
        #                                                                        'brand': 'Samsung', 'upc': '8872761235',
        #                                                                        'qty': '1', 'partNum': 'SM-R7200ZWAXAR',
        #                                                                        'estMsrp': '299.99'}, {'sku': '4471900',
        #                                                                                               'title': 'Samsung - Gear S2 Smartwatch 42mm Stainless Steel - White Elastomer',
        #                                                                                               'totalMsrp': '899.97',
        #                                                                                               'brand': 'Samsung',
        #                                                                                               'upc': '8872761235',
        #                                                                                               'qty': '3',
        #                                                                                               'partNum': 'SM-R7200ZWAXAR',
        #                                                                                               'estMsrp': '299.99'}]
        self.item_list = []
        self.current_item = {}
        self.body = None
        self.return_data = []
        self.final_request_dict_by_part_num = {}
        self.table_data = []


    def build_json_request_dict_by_part_num(self):
        item_desc = self.current_item.get('partNum')
        current_request_dict = {'keywords': item_desc,
                                'paginationInput': {'entriesPerPage': 100,
                                                    'pageNumber': 2}}
        self.final_request_dict_by_part_num['tns.findItemsByKeywordsRequest'] = current_request_dict

    def make_request(self, current_item=None):
        s = requests.Session()
        s.headers.update(self.header_dict)

        self.build_json_request_dict_by_part_num()
        body = json.dumps(self.final_request_dict_by_part_num)

        r = s.post(url=self.variable_post_url, json=body)


    def make_requests(self):
        s = requests.Session()
        s.headers.update(self.header_dict)
        for self.current_item in self.item_list:
            new_table_data = {}
            self.build_json_request_dict_by_part_num()
            body = json.dumps(self.final_request_dict_by_part_num)

            '''
            response = requests.get(url)
         while response.status_code != 200 and number_retries < max_retries:
            time.sleep(delay)
            response = requests.get(url)
            number_retries += 1
        response.raise_for_sta

            '''

            r = s.post(url=self.variable_post_url, data=body)
            i = 0
            while r.status_code != 200 and i < 10:
                time.sleep(10)
                r = s.post(url=self.variable_post_url, data=body)
                i += 1
            return_json = json.loads(r.content)
            print 'return json: {}'.format(return_json)
            return_dict = return_json['findItemsByKeywordsResponse'][0]
            print 'return dict: {}'.format(return_dict)
            print 'total entries (from pagination output): {}'.format(return_dict['paginationOutput'][0]['totalEntries'])
                # if return_dict['searchResult'][0]['item'][0]:
                # return_dict['searchResult'][0]['item'][0]
            if 'item' in return_dict['searchResult'][0].keys():
                print '@count: {}'.format(return_dict['searchResult'][0].keys())

                try:
                    for item in return_dict['searchResult'][0]['item']:

                        for key, value in item.iteritems():
                            new_table_data[key] = (value[0])
                            # self.table_data.append((key, value[0]))
                except Exception, e:
                    print 'fuck\n{}\nerror: {}\n\n'.format(return_dict['searchResult'], e)
                    continue
            else:
                print 'this entry has no... entries'
                print return_dict['searchResult'][0]['@count']

            if len(new_table_data) > 0:
                self.table_data.append(new_table_data)

        for item in self.table_data:
            print 'here is what were giving back: {}'.format(item)

                    # for name, value in return_dict.iteritems():
            #     if name == 'searchResult':
            #         for item in value[0]['item']:
            #             for this, that in item.iteritems():
            #                 print this, that
                            # print return_dict.get('itemSearchURL')


if __name__ == "__main__":
    this = EbayItemFinder()
    this.make_requests()
