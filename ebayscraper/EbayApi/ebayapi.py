# -*- coding: utf-8 -*-
import requests
import json
import time

testing = True


# http://www.ebay.com/sch/i.html?&_nkw=FDRAX33/B&LH_Complete=1&LH_Sold=1&rt=nc


class EbayItemFinder(object):
    def __init__(self):
        self.app_id = 'RickyWhi-EbayChec-PRD-65a6153ed-82a69392'
        self.dev_id = 'c82144dc-8041-480e-9b5e-2d8d4c67ef09'
        self.cert_id = 'SBX-5a63948ad0ad-8f6a-4ceb-8093-316a'

        self.header_dict = {'X-EBAY-SOA-SECURITY-APPNAME': self.app_id,
                            'X-EBAY-SOA-OPERATION-NAME': 'findCompletedItems',
                            'X-EBAY-SOA-REQUEST-DATA-FORMAT': 'JSON',
                            'X-EBAY-SOA-RESPONSE-DATA-FORMAT': 'JSON',
                            'X-EBAY-SOA-SERVICE-VERSION': '1.0.0'}
        self.variable_post_url = 'http://svcs.ebay.com/services/search/FindingService/v1'

        self.final_request_dict = {'jsonns.xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                                   'jsonns.xs': 'http://www.w3.org/2001/XMLSchema',
                                   'jsonns.tns': 'http://www.ebay.com/marketplace/search/v1/services',
                                   'tns.findCompletedItemsRequest': {'keywords': 'harry potter phoenix',
                                                                     'paginationInput': {'entriesPerPage': 100,
                                                                                         'pageNumber': 1},
                                                                     'itemFilter': {'name': 'SoldItemsOnly',
                                                                                    'value': 'true'}},
                                   }
        self.input_dict_list = []
        self.current_item_id = 0
        self.current_parsed_data = {}
        self.body = None
        self.final_request_dict_by_part_num = {}
        self.output_data_by_id = {}
        self.request_data_key = ''
        self.return_data_key = ''
        self.return_dict_key = ''

    def build_request_headers_for_completed_listings(self):
        self.header_dict = {'X-EBAY-SOA-SECURITY-APPNAME': self.app_id,
                            'X-EBAY-SOA-OPERATION-NAME': 'findCompletedItems',
                            'X-EBAY-SOA-REQUEST-DATA-FORMAT': 'JSON',
                            'X-EBAY-SOA-RESPONSE-DATA-FORMAT': 'JSON',
                            'X-EBAY-SOA-SERVICE-VERSION': '1.0.0'}
        self.request_data_key = 'tns.findCompletedItemsRequest'
        self.return_data_key = 'findCompletedItemsResponse'
        self.return_dict_key = 'completed_sale'

    def build_request_headers_for_current_listings(self):
        self.header_dict = {'X-EBAY-SOA-SECURITY-APPNAME': self.app_id,
                            'X-EBAY-SOA-OPERATION-NAME': 'findItemsByKeywords',
                            'X-EBAY-SOA-REQUEST-DATA-FORMAT': 'JSON',
                            'X-EBAY-SOA-RESPONSE-DATA-FORMAT': 'JSON',
                            'X-EBAY-SOA-SERVICE-VERSION': '1.0.0'}
        self.request_data_key = 'tns.findItemsByKeywordsRequest'
        self.return_data_key = 'findItemsByKeywordsResponse'
        self.return_dict_key = 'live_auction'

    def build_request_json_body_by_part_num_for_sold_items(self):
        current_request_dict = {'keywords': self.current_parsed_data.get('partNum'),
                                'paginationInput': {'entriesPerPage': 100,
                                                    'pageNumber': 1,
                                                    'itemFilter': {'name': 'SoldItemsOnly',
                                                                   'value': 'true'}},
                                }
        self.final_request_dict_by_part_num['tns.findCompletedItemsRequest'] = current_request_dict

    def build_request_json_body_by_title_for_sold_items(self):
        current_request_dict = {'keywords': self.current_parsed_data.get('title'),
                                'paginationInput': {'entriesPerPage': 100,
                                                    'pageNumber': 1,
                                                    'itemFilter': {'name': 'SoldItemsOnly',
                                                                   'value': 'true'}},
                                }
        self.final_request_dict_by_part_num['tns.findCompletedItemsRequest'] = current_request_dict

    def make_request(self, search_type):
        new_output_data = []
        item_count = 0
        print '\n\nSEARCHING BY {}'.format(search_type)
        if search_type == 'by_title':
            self.build_request_json_body_by_title_for_sold_items()
        else:
            self.build_request_json_body_by_part_num_for_sold_items()

        self.build_request_headers_for_completed_listings()
        s = requests.Session()
        s.headers.update(self.header_dict)

        body = json.dumps(self.final_request_dict_by_part_num)

        r = s.post(url=self.variable_post_url, data=body)
        i = 0
        while r.status_code != 200 and i < 10:
            time.sleep(10)
            r = s.post(url=self.variable_post_url, data=body)
            i += 1
        return_json = json.loads(r.content)

        return_dict = return_json[self.return_data_key][0]  # confirmed this is correct. {[{}]}
        if 'item' in return_dict['searchResult'][0].keys():
            try:
                item_count = return_dict['searchResult'][0]['@count']
                for item in return_dict['searchResult'][0]['item']:
                    if item['sellingStatus'][0]['sellingState'][0] == 'EndedWithoutSales':
                        continue
                    current_item_data = {}
                    for key, value in item.iteritems():
                        current_item_data[key] = value[0]
                    new_output_data.append(current_item_data)

            except Exception, e:
                print 'serious error\n{}\nerror: {}\n\n'.format(return_dict['searchResult'], e)
                return 'error'
        else:
            # TODO This is where we can handle the ones with low counts
            print 'this entry has no... entries'
            print return_dict['searchResult'][0]['@count']

        self.output_data_by_id[self.current_item_id] = {
            'itemSearchURL': return_dict.get('itemSearchURL', [None])[0],
            'return_data_by_type': {self.return_dict_key: {search_type: {'item_count': item_count, 'data': new_output_data}}}}
        print 'our output dict: {}'.format(self.output_data_by_id[self.current_item_id])






    def make_requests(self):
        # TODO: all the notes and requirement orders
        '''
        :requires:
        :return:
        '''
        s = requests.Session()
        s.headers.update(self.header_dict)
        for current_item in self.input_dict_list:
            new_output_data = []
            item_count = 0
            self.current_item_id = current_item['id']
            print 'id: {}'.format(self.current_item_id)
            self.current_parsed_data = current_item['parsed_data']
            self.build_request_json_body_by_part_num_for_sold_items()
            body = json.dumps(self.final_request_dict_by_part_num)

            r = s.post(url=self.variable_post_url, data=body)
            i = 0
            while r.status_code != 200 and i < 10:
                time.sleep(10)
                r = s.post(url=self.variable_post_url, data=body)
                i += 1
            return_json = json.loads(r.content)
            print 'return json: {}'.format(return_json)
            return_dict = return_json['findCompletedItemsResponse'][0]  # confirmed this is correct. {[{}]}
            print 'return dict: {}'.format(return_dict)
            print 'total entries (from pagination output): {}'.format(
                return_dict['paginationOutput'][0]['totalEntries'])
            if 'item' in return_dict['searchResult'][0].keys():
                item_count = return_dict['searchResult'][0]['@count']
                print 'dict keys of this search result (probably item, @count): {}'.format(
                    return_dict['searchResult'][0].keys())
                try:
                    for item in return_dict['searchResult'][0]['item']:
                        if item['sellingStatus'][0]['sellingState'][0] == 'EndedWithoutSales':
                            continue
                        current_item_data = {}
                        for key, value in item.iteritems():
                            current_item_data[key] = value[0]
                        new_output_data.append(current_item_data)

                except Exception, e:
                    print 'serious error\n{}\nerror: {}\n\n'.format(return_dict['searchResult'], e)
                    continue
            else:
                # TODO This is where we can handle the ones with low counts
                print 'this entry has no... entries'
                print return_dict['searchResult'][0]['@count']

            self.output_data_by_id[self.current_item_id] = {
                'itemSearchURL': return_dict.get('itemSearchURL', [None])[0],
                'return_data_by_type': {'completed_sale': {'by_part_num': {'item_count': item_count, 'data': new_output_data}}}}

                # for name, value in return_dict.iteritems():
                #     if name == 'searchResult':
                #         for item in value[0]['item']:
                #             for this, that in item.iteritems():
                #                 print this, that
                # print return_dict.get('itemSearchURL')


if __name__ == "__main__":
    this = EbayItemFinder()
    this.make_requests()
