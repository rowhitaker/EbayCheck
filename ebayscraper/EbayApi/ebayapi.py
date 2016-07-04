# -*- coding: utf-8 -*-
import requests
import json
import time

testing = False


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
        self.input_dict_list = []
        self.current_item_id = 0
        self.current_parsed_data = {}
        self.body = None
        self.final_request_dict_by_part_num = {}
        self.output_data = []

    def build_json_request_dict_by_part_num(self):
        current_request_dict = {'keywords': self.current_parsed_data.get('partNum'),
                                'paginationInput': {'entriesPerPage': 100,
                                                    'pageNumber': 1}}
        self.final_request_dict_by_part_num['tns.findItemsByKeywordsRequest'] = current_request_dict

    def make_request(self, current_item=None):
        s = requests.Session()
        s.headers.update(self.header_dict)

        self.build_json_request_dict_by_part_num()
        body = json.dumps(self.final_request_dict_by_part_num)

        r = s.post(url=self.variable_post_url, json=body)

    def make_requests(self):
        # TODO: all the notes and requirement orders
        '''
        :requires:
        :return:
        '''
        s = requests.Session()
        s.headers.update(self.header_dict)
        for current_item in self.input_dict_list:
            self.current_item_id = current_item['id']
            self.current_parsed_data = current_item['parsed_data']
            new_output_data = {}
            self.build_json_request_dict_by_part_num()
            body = json.dumps(self.final_request_dict_by_part_num)
            if testing:
                body = json.dumps(self.final_request_dict)

            r = s.post(url=self.variable_post_url, data=body)
            i = 0
            while r.status_code != 200 and i < 10:
                time.sleep(10)
                r = s.post(url=self.variable_post_url, data=body)
                i += 1
            return_json = json.loads(r.content)
            print 'return json: {}'.format(return_json)
            return_dict = return_json['findItemsByKeywordsResponse'][0]  # confirmed this is correct. {[{}]}
            print 'return dict: {}'.format(return_dict)
            print 'total entries (from pagination output): {}'.format(
                return_dict['paginationOutput'][0]['totalEntries'])
            if 'item' in return_dict['searchResult'][0].keys():
                print 'dict keys of this search result (probably item, @count): {}'.format(
                    return_dict['searchResult'][0].keys())

                try:
                    for item in return_dict['searchResult'][0]['item']:

                        for key, value in item.iteritems():
                            new_output_data[key] = (value[0])
                except Exception, e:
                    print 'serious error\n{}\nerror: {}\n\n'.format(return_dict['searchResult'], e)
                    continue
            else:
                print 'this entry has no... entries'
                print return_dict['searchResult'][0]['@count']

            if len(new_output_data) > 0:
                self.output_data.append({'id': self.current_item_id,
                                         'parsed_data': self.current_parsed_data,
                                         'ebay_return_data': new_output_data})

        for item in self.output_data:
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
