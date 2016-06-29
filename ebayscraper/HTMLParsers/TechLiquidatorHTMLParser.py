from HTMLParser import HTMLParser


class TLHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.new_data = {}  # dictionary of our table data, created from new_data_list
        self.new_data_list = []
        self.table_data = []  # final list of dictionaries containing new data
        self.recording = 0

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
            self.finalize_new_data()
            self.table_data.append(self.new_data)

    def handle_data(self, data):
        if self.recording:
            if not (u'\r' in data or u'\n' in data or u'\t' in data):
                self.new_data_list.append(data)

    def finalize_new_data(self):
        template = [(0, 'qty'), (1, 'brand'), (2, 'partNum'), (3, 'title'), (4, 'upc'), (5, 'sku'), (6, 'estMsrp'),
                    (7, 'totalMsrp')]
        self.new_data = {}
        self.new_data_list.reverse()

        for template_index in xrange(8):
            new_data_key = template[template_index][1]
            self.new_data[new_data_key] = self.new_data_list.pop().replace('{amp}', '&')
