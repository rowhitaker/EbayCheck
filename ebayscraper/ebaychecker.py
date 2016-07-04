import requests
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash
import logging
from HTMLParsers import TechLiquidatorHTMLParser as TLHTML
from datetime import datetime as DT
from EbayApi import ebayapi
from copy import deepcopy

testing = True

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
            print 'vars: {}'.format(session)
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
        abort(401)
    app.logger.info('Rendering "INPUT_URL"')
    return render_template('input_url.html')


@app.route('/display_results', methods=['POST'])
def display_results():
    set_step(step_name='display results', method=request.method)
    request_url = request.form['url']
    app.logger.info('The URL that was requested: {}'.format(request_url))

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

    p_data = {'parser.output_data': parser.output_data}
    my_ebay_api = ebayapi.EbayItemFinder()
    my_ebay_api.input_dict_list = parser.output_data
    my_ebay_api.make_requests()
    app.logger.debug('Output data from our Ebay Finder API: {}'.format(my_ebay_api.output_data))

    table_data = deepcopy(my_ebay_api.output_data)
    for item in table_data:
        print 'keys: {}'.format(item.keys())
        erd = item['ebay_return_data']
        print erd
        print len(erd)
        avg_price = 0
        i = 0
        for item_data in erd:
            i += 1
            print 'keys again: {}'.format(item_data.keys())
            item_price= item_data['sellingStatus']['currentPrice'][0]['__value__']
            item_price = float(item_price)
            avg_price += item_price
        avg_price = avg_price / i

        item['average_item_price'] = avg_price

        print 'our table data for this item: {}'.format(item)



    return render_template('display_results.html', table_data=table_data)


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
