import requests
from LoggerAndArchiver import logger
from HTMLParsers import TechLiquidatorHTMLParser as TLHTML


if __name__ == "__main__":

    request_url = 'https://techliquidators.com/index.cfm/p/34/i/1799356'

    log = logger.build_logger(name='EbayScraper', level='DEBUG')
    # log.info('Making our request')
    # log.info('Request URL: {}'.format(request_url))
    # # r = requests.get("https://techliquidators.com/index.cfm/p/34/i/1798967")
    # r = requests.get(request_url)
    # log.info('Response status code: {}'.format(r.status_code))
    # log.debug('Response status cookies: {}'.format(r.cookies))
    # log.debug('Response headers: {}'.format(r.headers))
    # log.debug('Response content: {}'.format(r.content))
    #
    # parser = TLHTML.TLHTMLParser()
    # parser.feed(r.content.replace('&', '{amp}'))
    #
    # log.info('Table Data: {}'.format(parser.table_data))

    log.close()
