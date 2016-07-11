import sys
import json
import requests
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash
import logging
from HTMLParsers import TechLiquidatorHTMLParser as TLHTML
from datetime import datetime as DT
from EbayApi import ebayapi
from copy import deepcopy

p_data = {}
p_data['item_dicts_by_id'] = {}


def reinitialize_p_data():
    p_data = {}
    p_data['item_dicts_by_id'] = {}
    p_data['request_url'] = ''

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.logger.setLevel(logging.INFO)

# Load default config and override config from an environment variable
app.config.update(dict(
    SECRET_KEY='Th1sIs0uRSt0opidS33cr3tP@sSW0rd!#!#$%%*',
    LOGINCREDS={'rwhitaker': 'abc123', 'guest': '123abc', 'ben': 'weatherl'}
))

app.config.from_envvar('EBAYCHECKER_SETTINGS',
                       silent=True)  # can also use from_object() to import config from associated object


@app.route('/', methods=['GET', 'POST'])
def login():
    try:
        set_step(step_name='Login', method=request.method)
        error_msg = None
        if request.method == 'POST':
            submitted_login = request.form['loginname']
            submitted_pwd = request.form['password']

            app.logger.critical('Login name requesting access: {}'.format(submitted_login))
            if submitted_login not in app.config['LOGINCREDS'].keys():
                app.logger.error('Invalid Login Name')
                error_msg = 'Invalid username or password'

            elif submitted_pwd != app.config['LOGINCREDS'][submitted_login]:
                app.logger.error('Invalid Password')
                error_msg = 'Invalid username or password'
            else:
                session['logged_in'] = True
                session['loginname'] = submitted_login
                app.logger.info('Successfully logged in')
                app.logger.info('Redirecting to "INPUT_URL"')
                return redirect(url_for('input_url'))
        app.logger.info('Rendering "LOGIN"')
        return render_template('login.html', error_msg=error_msg)
    except Exception, e:
        app.logger.error('Ran into an error: {}'.format(e))


@app.route('/logout')
def logout():
    set_step(step_name='Logout', method=request.method)
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))


@app.route('/input_url', methods=['GET'])
def input_url():
    try:
        set_step(step_name='input url', method=request.method)
        if not session.get('logged_in'):
            app.logger.error('User was not logged in: "bouncer, trash this request"')
            # abort(401)
            return redirect(url_for('login'))
        app.logger.info('Rendering "INPUT_URL"')

        default_url = ''
        if session['loginname'] == 'guest':
            flash('Hey {}!'.format(session['loginname']))
            flash('Thanks for checking out my tool.')
            flash('why don\'t you try hitting submit on the button below')
            default_url = 'https://techliquidators.com/index.cfm/p/34/i/1803366'

        return render_template('input_url.html', default_url=default_url)

    except Exception, e:
        app.logger.error('Ran into an error: {}'.format(e))


@app.route('/display_results', methods=['POST'])
def display_results():
    try:
        reinitialize_p_data()
        reloading = request.form.get('reload')
        set_step(step_name='display results', method=request.method)
        request_url = request.form['url']
        p_data['request_url'] = request_url
        app.logger.critical('The URL that was requested: {}'.format(request_url))

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
                p_data['item_dicts_by_id'][data_id]['display_selection'] = 'by_part_num'

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
            display_selection = item_data['display_selection']
            avg_price = []
            avg_shipping_price = []
            for sub_item in item_data['return_data_by_type'][display_selection]['data']:
                index = item_data['return_data_by_type'][display_selection]['data'].index(sub_item)
                item_price = sub_item['sellingStatus']['currentPrice'][0]['__value__']
                item_price = float(item_price)
                avg_price.append(item_price)

                if sub_item['shippingInfo']['shippingType'][0].lower() == 'flat':
                    shipping_cost = sub_item['shippingInfo']['shippingServiceCost'][0]['__value__']
                    p_data['item_dicts_by_id'][item_id]['return_data_by_type'][display_selection]['data'][index]['shipping_cost'] = shipping_cost
                    p_data['item_dicts_by_id'][item_id]['return_data_by_type'][display_selection]['data'][index]['shipping_method'] = 'Flat'
                    avg_shipping_price.append(float(shipping_cost))
                elif sub_item['shippingInfo']['shippingType'][0].lower() == 'free':
                    p_data['item_dicts_by_id'][item_id]['return_data_by_type'][display_selection]['data'][index]['shipping_cost'] = 0
                    p_data['item_dicts_by_id'][item_id]['return_data_by_type'][display_selection]['data'][index]['shipping_method'] = 'Free'
                    avg_shipping_price.append(0)
                else:
                    p_data['item_dicts_by_id'][item_id]['return_data_by_type'][display_selection]['data'][index]['shipping_cost'] = ''
                    p_data['item_dicts_by_id'][item_id]['return_data_by_type'][display_selection]['data'][index]['shipping_method'] = 'Calculated'

            if len(avg_price) > 0:
                p_data['item_dicts_by_id'][item_id]['return_data_by_type'][display_selection]['average_item_price'] = sum(avg_price) / len(avg_price)
            else:
                p_data['item_dicts_by_id'][item_id]['return_data_by_type'][display_selection]['average_item_price'] = 0

            if len(avg_shipping_price) > 0:
                p_data['item_dicts_by_id'][item_id]['return_data_by_type'][display_selection]['average_shipping_price'] = sum(avg_shipping_price) / len(avg_shipping_price)
            else:
                p_data['item_dicts_by_id'][item_id]['return_data_by_type'][display_selection]['average_shipping_price'] = 0

        app.logger.debug('Our p_data keys: {}'.format(p_data.keys()))
        app.logger.debug('Our p_data: {}'.format(p_data))

        app.logger.critical('Returning data')

        return render_template('display_results.html', p_data=p_data)
    except Exception, e:
        app.logger.error('Ran into an error: {}'.format(e))


@app.route('/resubmit', methods=['POST'])
def resubmit():
    try:
        reinitialize_p_data()
        set_step(step_name='resubmit', method=request.method)
        app.logger.debug('our incoming stuff: {}'.format(request.form))

        p_data = json.loads(request.form['submission_data'])
        request_url = p_data['request_url']

        my_ebay_api = ebayapi.EbayItemFinder()

        table_data = deepcopy(p_data['item_dicts_by_id'])
        for item_id, item_data in table_data.iteritems():
            display_selection = item_data['display_selection']
            p_data['item_dicts_by_id'][item_id]['return_data_by_type'] = {display_selection: {}}
            p_data['item_dicts_by_id'][item_id]['display_selection'] = display_selection

            my_ebay_api.current_item_id = item_id
            my_ebay_api.current_parsed_data = item_data['parsed_data']
            my_ebay_api.make_request(display_selection)

        for data_id, data_dict in my_ebay_api.output_data_by_id.iteritems():
            p_data['item_dicts_by_id'][data_id]['return_data_by_type'].update(data_dict['return_data_by_type'])
            p_data['itemSearchURL'] = data_dict['itemSearchURL']

        app.logger.debug('Our p_data: {}'.format(p_data))

        table_data = deepcopy(p_data['item_dicts_by_id'])
        for item_id, item_data in table_data.iteritems():
            display_selection = item_data['display_selection']
            avg_price = []
            avg_shipping_price = []
            for sub_item in item_data['return_data_by_type'][display_selection]['data']:
                index = item_data['return_data_by_type'][display_selection]['data'].index(sub_item)
                item_price = sub_item['sellingStatus']['currentPrice'][0]['__value__']
                item_price = float(item_price)
                avg_price.append(item_price)

                if sub_item['shippingInfo']['shippingType'][0].lower() == 'flat':
                    shipping_cost = sub_item['shippingInfo']['shippingServiceCost'][0]['__value__']
                    p_data['item_dicts_by_id'][item_id]['return_data_by_type'][display_selection][
                        'data'][index]['shipping_cost'] = shipping_cost
                    p_data['item_dicts_by_id'][item_id]['return_data_by_type'][display_selection][
                        'data'][index]['shipping_method'] = 'Flat'
                    avg_shipping_price.append(float(shipping_cost))
                elif sub_item['shippingInfo']['shippingType'][0].lower() == 'free':
                    p_data['item_dicts_by_id'][item_id]['return_data_by_type'][display_selection][
                        'data'][index]['shipping_cost'] = 0
                    p_data['item_dicts_by_id'][item_id]['return_data_by_type'][display_selection][
                        'data'][index]['shipping_method'] = 'Free'
                    # avg_shipping_price.append(0)
                else:
                    p_data['item_dicts_by_id'][item_id]['return_data_by_type'][display_selection][
                        'data'][index]['shipping_cost'] = ''
                    p_data['item_dicts_by_id'][item_id]['return_data_by_type'][display_selection][
                        'data'][index]['shipping_method'] = 'Calculated'

            if len(avg_price) > 0:
                p_data['item_dicts_by_id'][item_id]['return_data_by_type'][display_selection][
                    'average_item_price'] = sum(avg_price) / len(avg_price)
            else:
                p_data['item_dicts_by_id'][item_id]['return_data_by_type'][display_selection][
                    'average_item_price'] = 0

            if len(avg_shipping_price) > 0:
                p_data['item_dicts_by_id'][item_id]['return_data_by_type'][display_selection][
                    'average_shipping_price'] = sum(avg_shipping_price) / len(avg_shipping_price)
            else:
                p_data['item_dicts_by_id'][item_id]['return_data_by_type'][display_selection][
                    'average_shipping_price'] = 0


        # TODO: This is where we'll call our analytics engine

        app.logger.debug('Our p_data keys: {}'.format(p_data.keys()))
        app.logger.debug('Our p_data: {}'.format(p_data))

        app.logger.critical('Returning data')

        return render_template('display_results.html', p_data=p_data)

    except Exception, e:
        app.logger.error('Ran into an error: {}'.format(e))



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
    app.logger.critical('{} Login: {} '.format('*' * 25, session.get('loginname')).ljust(100, '*'))
    app.logger.critical('*' * 100)


def close():
    completed_message = 'Closing down logger, Thanks for playing :-)'
    message_length = len(completed_message) + 26
    app.logger.critical('*' * message_length)
    app.logger.critical('{0} {1} {0}'.format('*' * 12, completed_message))
    app.logger.critical('*' * message_length)
    logging.shutdown()


def main():

    ip = '0.0.0.0'
    app.run(debug=False, host=ip)

if __name__ == '__main__':

    sys.exit(main())
