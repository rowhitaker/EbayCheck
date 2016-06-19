import requests
from HTMLParser import HTMLParser
from collections import OrderedDict

from LoggerAndArchiver import logger


class MyHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.new_data = None  # dictionary of our table data, created from new_data_list
        self.new_data_list = []
        self.table_data = []  # final list of dictionaries containing new data
        self.recording = 0

        self.reset_new_data()

    def handle_starttag(self, tag, attributes):
        if tag != 'tr':
            return
        if self.recording:
            self.recording += 1
            return
        for name, value in attributes:
            if name.lower().strip() == 'class' and 'reportrowbody' in value.lower().strip():
                self.recording = 1
                break
        else:
            return

    def handle_endtag(self, tag):
        if tag == 'tr' and self.recording:
            self.recording -= 1
            self.finalize_new_data()
            self.table_data.append(self.new_data)
            self.reset_new_data()

    def handle_data(self, data):
        if self.recording:
            if not (u'\r' in data or u'\n' in data or u'\t' in data):
                self.new_data_list.append(data)

    def finalize_new_data(self):
        for data in self.new_data_list:
            print 'data {}'.format(data)
            index_of_list_item_to_add = self.new_data_list.index(data)
            key_in_dict_of_item_to_add = self.new_data.keys()[index_of_list_item_to_add]
            print index_of_list_item_to_add, key_in_dict_of_item_to_add
            self.new_data[key_in_dict_of_item_to_add] = data
            # self.new_data[self.new_data.keys()[self.new_data_list.index(data)]] = data

    def reset_new_data(self):
        '''
        table data should be in the following order,:
        QTY, BRAND, PART #, ITEM TITLE, UPC, SKU, EST. MSRP, TOTAL MSRP

        if not it likely means the table structure on the page changed.
        '''
        self.new_data = OrderedDict()
        self.new_data['qty'] = None
        self.new_data['brand'] = None
        self.new_data['partNum'] = None
        self.new_data['title'] = None
        self.new_data['upc'] = None
        self.new_data['sku'] = None
        self.new_data['estMsrp'] = None
        self.new_data['totalMsrp'] = None

if __name__ == "__main__":

    request_url = 'https://techliquidators.com/index.cfm/p/34/i/1799356'

    log = logger.build_logger(name='EbayScraper', level='DEBUG')
    log.info('Making our request')
    log.info('Request URL: {}'.format(request_url))
    # r = requests.get("https://techliquidators.com/index.cfm/p/34/i/1798967")
    r = requests.get(request_url)
    log.info('Response status code: {}'.format(r.status_code))
    log.debug('Response status cookies: {}'.format(r.cookies))
    log.debug('Response headers: {}'.format(r.headers))
    log.debug('Response content: {}'.format(r.content))

    parser = MyHTMLParser()
    parser.feed(r.content)
    # # print parser.handle_starttag(tag='td', attrs=[('class', 'reportRowBody')])
    # with open('C:\\users\\ricks\\PycharmProjects\\ebayscraper\\ebayscraper\\tests\\TL_Html.txt', 'r') as infile:
        # sample_html = infile.read()

    for thing in parser.table_data:
        print thing
    log.info('Table Data: {}'.format(parser.table_data))
    # log.info('Table data: {}'.format(sample_html))
    # for item in parser.table_data:
        # print item[1]

    log.close()
