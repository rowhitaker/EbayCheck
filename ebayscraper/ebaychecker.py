import json
import requests
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash
import logging
from HTMLParsers import TechLiquidatorHTMLParser as TLHTML
from datetime import datetime as DT
from EbayApi import ebayapi
from copy import deepcopy

testing = True

cached_page_data_by_url = {}

p_data = {}
p_data['item_dicts_by_id'] = {}


def reinitialize_p_data():
    p_data = {}
    p_data['item_dicts_by_id'] = {}
    p_data['request_url'] = ''

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    SECRET_KEY='Th1sIs0uRSt0opidS33cr3tP@sSW0rd!#!#$%%*',
    LOGINNAME='rwhitaker',
    PASSWORD='abc123'
))

app.config.from_envvar('EBAYCHECKER_SETTINGS',
                       silent=True)  # can also use from_object() to import config from associated object


@app.route('/', methods=['GET', 'POST'])
def login():
    set_step(step_name='Login', method=request.method)
    error_msg = None
    if request.method == 'POST':
        app.logger.info('login name requesting access: {}'.format(request.form['loginname']))
        if request.form['loginname'] != app.config['LOGINNAME']:
            app.logger.error('Invalid Login Name')
            error_msg = 'Invalid username or password'
        elif request.form['password'] != app.config['PASSWORD']:
            app.logger.error('Invalid Password')
            error_msg = 'Invalid username or password'
        else:
            session['logged_in'] = True
            flash('Hi {}! I hope you\'re having a great day so far!'.format(request.form['loginname']))
            app.logger.info('Successfully logged in')
            app.logger.info('Redirecting to "INPUT_URL"')
            return redirect(url_for('input_url'))
    app.logger.info('Rendering "LOGIN"')
    return render_template('login.html', error_msg=error_msg)


@app.route('/logout')
def logout():
    set_step(step_name='Logout', method=request.method)
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))


@app.route('/input_url', methods=['GET'])
def input_url():
    set_step(step_name='input url', method=request.method)
    if not session.get('logged_in'):
        app.logger.error('User was not logged in: "bouncer, trash this request"')
        # abort(401)
        return redirect(url_for('login'))
    app.logger.info('Rendering "INPUT_URL"')
    return render_template('input_url.html')


@app.route('/display_results', methods=['POST'])
def display_results():
    reinitialize_p_data()
    reloading = request.form.get('reload')
    set_step(step_name='display results', method=request.method)
    request_url = request.form['url']
    p_data['request_url'] = request_url
    app.logger.info('The URL that was requested: {}'.format(request_url))

    if reloading and cached_page_data_by_url.get(request_url):
        app.logger.info('Hard reload requested, purging cached data')
        cached_page_data_by_url.pop(request_url)

    if cached_page_data_by_url.get(request_url) is None:
        cached_page_data_by_url[request_url] = {}

    if cached_page_data_by_url[request_url].get('item_dicts_by_id') is None:
        app.logger.info('We don\'t have this data cached, pulling fresh.')
        app.logger.debug('Creating an HTTP requests Session')
        s = requests.Session()

        try:
            app.logger.info('Making our HTTP request')
            r = s.get(request_url)
        except Exception, e:
            app.logger.error('Uh oh, failed to make our HTTP request')
            app.logger.error('Error was: {}'.format(e))
            return error_return(e)

        app.logger.info('Made our HTTP Request, status code was: {}'.format(r.status_code))

        if r.status_code != 200:
            return error_return('Unable to successfully call "{}"'.format(request_url))

        app.logger.debug('Response status cookies: {}'.format(r.cookies))
        app.logger.debug('Response headers: {}'.format(r.headers))
        # app.logger.debug('Response content: {}'.format(r.content))  # the actual html, it's huge

        app.logger.info('Attempting to parse return HTML')
        parser = TLHTML.TLHTMLParser()
        parser.feed(r.content.replace('&', '{amp}'))

        app.logger.debug('Parsed data: {}'.format(parser.output_data))

        for item in parser.output_data:
            data_id = item['id']
            if p_data['item_dicts_by_id'].get(data_id) is None:
                p_data['item_dicts_by_id'][data_id] = {}
                p_data['item_dicts_by_id'][data_id]['return_data_by_type'] = {}
                p_data['item_dicts_by_id'][data_id]['itemSearchURL'] = ''
                p_data['item_dicts_by_id'][data_id]['average_item_price'] = float(0)
                p_data['item_dicts_by_id'][data_id]['display_selection'] = ('completed_sale', 'by_part_num')

            p_data['item_dicts_by_id'][data_id]['parsed_data'] = item['parsed_data']

        my_ebay_api = ebayapi.EbayItemFinder()
        my_ebay_api.input_dict_list = parser.output_data
        my_ebay_api.make_requests()
        app.logger.debug('Output data from our Ebay Finder API: {}'.format(my_ebay_api.output_data_by_id))

        for item_id, item_dict in my_ebay_api.output_data_by_id.iteritems():

            p_data['item_dicts_by_id'][item_id]['return_data_by_type'].update(item_dict['return_data_by_type'])


        # TODO: This is where we'll call our analytics engine

        table_data = deepcopy(p_data['item_dicts_by_id'])
        for item_id, item_data in table_data.iteritems():
            avg_price = []
            for sub_item in item_data['return_data_by_type']['completed_sale']['by_part_num']:
                item_price = sub_item['sellingStatus']['currentPrice'][0]['__value__']
                item_price = float(item_price)
                avg_price.append(item_price)

            p_data['item_dicts_by_id'][item_id]['average_item_price'] = sum(avg_price) / len(avg_price)

        cached_page_data_by_url[request_url]['item_dicts_by_id'] = p_data['item_dicts_by_id']
        app.logger.debug('Our p_data keys: {}'.format(p_data.keys()))
        app.logger.debug('Our p_data: {}'.format(p_data))

    else:
        app.logger.info('Super, we have cached data, no need to pull fresh :-D')
        app.logger.debug('Our p_data keys: {}'.format(p_data.keys()))
        app.logger.debug('Our p_data: {}'.format(p_data))
        p_data['item_dicts_by_id'] = cached_page_data_by_url[request_url]['item_dicts_by_id']
        p_data['request_url'] = request_url

    return render_template('display_results.html', p_data=p_data)


@app.route('/resubmit', methods=['POST'])
def resubmit():
    reinitialize_p_data()
    set_step(step_name='resubmit', method=request.method)
    app.logger.debug('our incoming stuff: {}'.format(request.form))

    p_data = json.loads(request.form['submission_data'])
    request_url = p_data['request_url']

    my_ebay_api = ebayapi.EbayItemFinder()

    table_data = deepcopy(p_data['item_dicts_by_id'])
    for item_id, item_data in table_data.iteritems():
        display_selection = item_data['display_selection']
        p_data['item_dicts_by_id'][item_id]['return_data_by_type'] = {display_selection[0]: {display_selection[1]: {}}}
        p_data['item_dicts_by_id'][item_id]['display_selection'] = (display_selection[0], display_selection[1])

        my_ebay_api.current_item_id = item_id
        my_ebay_api.current_parsed_data = item_data['parsed_data']
        my_ebay_api.make_request(display_selection[1])

    for data_id, data_dict in my_ebay_api.output_data_by_id.iteritems():
        p_data['item_dicts_by_id'][data_id]['return_data_by_type'].update(data_dict['return_data_by_type'])
        p_data['itemSearchURL'] = data_dict['itemSearchURL']

    app.logger.debug('Our p_data: {}'.format(p_data))

    table_data = deepcopy(p_data['item_dicts_by_id'])
    for item_id, item_data in table_data.iteritems():
        avg_price = []
        display_selection = item_data['display_selection']
        for sub_item in item_data['return_data_by_type'][display_selection[0]][display_selection[1]]:
            item_price = sub_item['sellingStatus']['currentPrice'][0]['__value__']
            item_price = float(item_price)
            avg_price.append(item_price)

        if len(avg_price) > 0:
            p_data['item_dicts_by_id'][item_id]['average_item_price'] = sum(avg_price) / len(avg_price)
        else:
            p_data['item_dicts_by_id'][item_id]['average_item_price'] = 0


    # TODO: This is where we'll call our analytics engine

    if cached_page_data_by_url.get(request_url) is None:
        cached_page_data_by_url[request_url] = {}
    cached_page_data_by_url[request_url]['item_dicts_by_id'] = p_data['item_dicts_by_id']
    app.logger.debug('Our p_data keys: {}'.format(p_data.keys()))
    app.logger.debug('Our p_data: {}'.format(p_data))

    return render_template('display_results.html', p_data=p_data)




    # TODO: build out our ajax call, refresh and repopulate the submitted stuff




@app.route('/shutdown', methods=['GET'])
def shutdown():
    shutdown_server()
    return 'Sever shutdown'


def error_return(error_msg):
    set_step(step_name='error return', method=request.method)
    return render_template('error.html', error_msg=error_msg)


def shutdown_server():
    set_step(step_name='shutdown server', method=request.method)
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    close()


def set_step(step_name, method):
    current_step = step_name.replace(' ', '_').upper()
    app.logger.critical('*' * 100)
    app.logger.critical('{} Current Step: {} '.format('*' * 25, current_step).ljust(100, '*'))
    app.logger.critical('{} Method: {} '.format('*' * 25, method).ljust(100, '*'))
    app.logger.critical('{} Session: {} '.format('*' * 25, session.get('session')).ljust(100, '*'))
    app.logger.critical('*' * 100)


def close():
    completed_message = 'Closing down logger, Thanks for playing :-)'
    message_length = len(completed_message) + 26
    app.logger.critical('*' * message_length)
    app.logger.critical('{0} {1} {0}'.format('*' * 12, completed_message))
    app.logger.critical('*' * message_length)
    logging.shutdown()


def main():
    log_dir = 'Logs'

    date_format = '%Y%m%d'
    current_date = DT.now().strftime(date_format)
    current_time = DT.now().strftime('%H%M%S%f')

    # build logger
    name = 'EbayChecker'
    file_hdlr = logging.FileHandler('./{}/{}_{}_{}.{}'.format(log_dir, name, current_date, current_time, 'log'))
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y%m%d_%H%M%S')
    file_hdlr.setLevel(logging.DEBUG)
    file_hdlr.setFormatter(formatter)

    app.logger.addHandler(file_hdlr)
    app.run(debug=True, host='0.0.0.0')


if __name__ == '__main__':

    try:
        ip = '0.0.0.0'
        if testing:
            import os

            log_dir = 'Logs'

            date_format = '%Y%m%d'
            current_date = DT.now().strftime(date_format)
            current_time = DT.now().strftime('%H%M%S%f')

            # create our log folders if they don't already exist
            if not os.path.isdir(log_dir):
                os.mkdir(log_dir)

            # build logger
            name = 'EbayChecker'
            file_hdlr = logging.FileHandler('./{}/{}_{}_{}.{}'.format(log_dir, name, current_date, current_time, 'log'))
            formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                          datefmt='%Y%m%d_%H%M%S')
            file_hdlr.setLevel(logging.DEBUG)
            file_hdlr.setFormatter(formatter)

            app.logger.addHandler(file_hdlr)
            app.logger.info('hello world')
            ip = '127.0.0.1'

        app.run(debug=True, host=ip)

    except Exception, e:
        print 'uh oh, we ran into an exception: {}'.format(e)