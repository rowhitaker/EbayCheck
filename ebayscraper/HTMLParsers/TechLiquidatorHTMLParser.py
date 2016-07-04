from HTMLParser import HTMLParser


class TLHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.parsed_data = {}  # dictionary of our item data, created from parsed_data_list
        self.parsed_data_list = []  # a list of our incoming data, this is a list of data elements
        self.output_data = []  # final list of dictionaries containing new data
        self.recording = 0
        self.data_id = 0

    def handle_starttag(self, tag, attributes):
        if tag == 'tr':
            for name, value in attributes:
                if name.lower().strip() == 'class' and 'reportrowbody' in value.lower().strip():
                    self.recording += 1
                    break
        else:
            return

    def handle_endtag(self, tag):
        if tag == 'tr' and self.recording:
            self.recording -= 1
            self.finalize_parsed_data()
            self.output_data.append({'id': self.data_id, 'parsed_data': self.parsed_data})
            self.data_id += 1

    def handle_data(self, data):
        if self.recording:
            if not (u'\r' in data or u'\n' in data or u'\t' in data):
                self.parsed_data_list.append(data)

    def finalize_parsed_data(self):
        # TODO: you know the order in the list, use the list element location as your key
        template = [(0, 'qty'), (1, 'brand'), (2, 'partNum'), (3, 'title'), (4, 'upc'), (5, 'sku'), (6, 'estMsrp'),
                    (7, 'totalMsrp')]
        self.parsed_data = {}
        self.parsed_data_list.reverse()

        for template_index in xrange(8):
            parsed_data_key = template[template_index][1]
            self.parsed_data[parsed_data_key] = self.parsed_data_list.pop().replace('{amp}', '&')
