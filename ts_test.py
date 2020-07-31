'''
@author:   Ken Venner
@contact:  ken@venerllc.com
@version:  1.04

Using Selenium and Chrome/Firefox - screen scrape wine websites to draw
down wine pricing and availiability information

'''

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

import requests

import kvutil
import kvcsv

import time
import re
import datetime
import sys


# logging - 
import kvlogger
config=kvlogger.get_config(kvutil.filename_create(__file__, filename_ext='log', path_blank=True), loggerlevel='INFO') #single file
kvlogger.dictConfig(config)
logger=kvlogger.getLogger(__name__)

# added logging feature to capture and log unhandled exceptions
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception


# application variables
optiondictconfig = {
    'AppVersion' : {
        'value' : '1.04',
        'description' : 'defines the version number for the app',
        'sortorder' : 1,
    },
    'tsfile' : {
        'value' : '',
        'description' : 'defines the csv filename containing the list of urls of trusted shares to process and # of pages to step through',
        'sortorder' : 10,
    },
    'url' : {
        'value' : '',
        'description' : 'defines the url of the Trusted share we are checking',
        'sortorder' : 20,
    },
    'pagecnt' : {
        'value' : 3,
        'type'  : 'int',
        'description' : 'defines the number of pages to step through in the pdf',
        'sortorder' : 30,
    },
    'pagewait' : {
        'value' : 3,
        'type'  : 'int',
        'description' : 'defines the number of seconds to sleep between page changes',
        'sortorder' : 40,
    },
    'findelementsloopcnt_pdfopen' : {
        'value' : 25,
        'type'  : 'int',
        'description' : 'defines the max number of times we loop for 3 seconds waiting for the pdf to open and render',
        'sortorder' : 50,
    },
    'findelementsloopcnt_nextpage' : {
        'value' : 8,
        'type'  : 'int',
        'description' : 'defines the max number of times we loop for 3 seconds waiting for the pdf page to change',
        'sortorder' : 60,
    },
    'utcstarttime' : {
        'value' : None,
        'type'  : 'datetimezone',
        'description' : 'defines the UTC start time to start processing - we will wait until this time arrives - used to kick off a coordinate load test',
        'sortorder' : 70,
    },
    'startinmin'   : {
        'value' : 0,
        'type'  : 'int',
        'description' : 'defines the number of minutes in the future to start running, which returns back the command for others to execute - see utcstarttime',
        'sortorder' : 80,
    },
    

    # control the type of browser we are using to do the automation
    'browser' : {
        'value' : 'chrome',
        'description' : 'defines which browser we are using to automate with (chrome, ff, firefox)',
        'sortorder' : 90,
    },

}

# -----------------------------------------------------------------------

# CHROME SPECIFIC FEATURES #

# created this because upgrade to ChromeDriver 75 broke this script
def create_webdriver_from_global_var( browser, message=None ):

    if message:
        logger.info('%s:start up webdriver:%s', message, browser)

    if browser == 'chrome':
        # turn off w3c - implemented 20190623;kv
        opt = webdriver.ChromeOptions()
        opt.add_experimental_option('w3c', False)
        driver = webdriver.Chrome(chrome_options=opt)
    else:
        driver = webdriver.Firefox()

    return driver

    
# function to create browser and go to a url (optionally)
def create_selenium_driver_worker( browser, url=None ):

    # Create driver
    driver=create_webdriver_from_global_var( browser )

    # debugging
    logger.info('created browser of type:%s', browser )
    
    # Open the website
    if url:
        logger.info('going to url:%s', url)
        driver.get( url )

    # return the driver
    return driver


   
# attempt to find a set of elements in a page
def find_elements_looped(driver, name, byType, msg, msg2, loopcnt=4, waitsecs=3, displayFailure=True, debug=False ):
    if byType in ('by_class_name', 'byClassName', 'class_name', 'className'):
        results = driver.find_elements_by_class_name( name )
    elif byType in ('by_name', 'byName', 'name'):
        results = driver.find_elements_by_name( name )
    elif byType in ('by_xpath', 'byXpath', 'xpath'):
        results = driver.find_elements_by_xpath( name )
    elif byType in ('by_id', 'byID', 'id'):
        results = driver.find_elements_by_id( name )

    while not results and loopcnt:
        if displayFailure:
            logger.info('%s:%s:%s:%d',msg,msg2,name,loopcnt)
        loopcnt -= 1
        time.sleep(waitsecs)

        if byType in ('by_class_name', 'byClassName', 'class_name', 'className'):
            results = driver.find_elements_by_class_name( name )
        elif byType in ('by_name', 'byName', 'name'):
            results = driver.find_elements_by_name( name )
        elif byType in ('by_xpath', 'byXpath', 'xpath'):
            results = driver.find_elements_by_xpath( name )
        elif byType in ('by_id', 'byID', 'id'):
            results = driver.find_elements_by_id( name )

    return results


def seconds_until_start( utcstarttime ):
    # get the current utc timestamp
    utcnow=datetime.datetime.now(tz=datetime.timezone.utc)
    # determine how many more seconds until this start time hits
    timediff = optiondict['utcstarttime'] - utcnow
    # convert to seconds
    return timediff.total_seconds()



# ---------------------------------------------------------------------------
if __name__ == '__main__':

    # capture the command line
    optiondict = kvutil.kv_parse_command_line( optiondictconfig, debug=False )

    # check if the browser is set
    if optiondict['browser'] in ('ff', 'firefox'):
        browser = 'firefox'


    # read in the list of urls
    if optiondict['tsfile']:
        urls = kvcsv.readcsv2list(optiondict['tsfile'])
    else:
        urls = []

    # read in the command line url
    if optiondict['url']:
        urls.append({'url' : optiondict['url'], 'pagecnt' : optiondict['pagecnt']})

    # fail if we have no urls to process
    if not urls:
        raise Exception('No URLs to process - terminating')

    # if we want a future start - define it
    if optiondict['startinmin']:
        # calc the utc time now and in the future
        utcnow=datetime.datetime.now(tz=datetime.timezone.utc)
        utcfuture = utcnow +  + datetime.timedelta(minutes=optiondict['startinmin'])
        # set the optiondict as though we read this in
        optiondict['utcstarttime'] = utcfuture
        # display that we are waiting until that time to start
        print('\n\nYou defined a start time in the future.  Please tell others to use this command line:')
        print('windows:    start python ts_test.py utcstarttime=%s' % (utcfuture.isoformat()))
        print('mac/linux:  nohup python ts_test.py utcstarttime=%s' % (utcfuture.isoformat()))
        print('\n\n')

    # user wants to control the start time of this run
    # most likely coordinating this with others.
    if optiondict['utcstarttime']:
        # tell what we are doing
        print('\nWe are starting this test at:%s' % ( optiondict['utcstarttime'].isoformat() ))
        # get the time until start
        timediffsec = seconds_until_start( optiondict['utcstarttime'] )

        # if the time is negative we have a problem
        if timediffsec < 0:
            raise Exception('utcstartime is in the past - we can not start')
        # now loop until the time gets here
        while timediffsec > 60:
            print('Minutes until we start:%d' % (int(timediffsec/60)))
            time.sleep(60)
            timediffsec = seconds_until_start( optiondict['utcstarttime'] )
        print('Seconds until we start:%d' % (timediffsec))
        time.sleep(timediffsec)
            
    # build out simple use case one browser one url
    logger.info('create browser')
    driver = create_selenium_driver_worker( optiondict['browser'] )

    for rec in urls:
        url = rec['url']
        pagecnt = rec['pagecnt']

        # prepping to make this a URL loop
        logger.info('url:%s', url)
        starttime = time.time()
        driver.get(url)

        # find the confirm button
        results = find_elements_looped(driver, 'btn_brand-default', 'byClassName', 'findTou', '', loopcnt=optiondict['findelementsloopcnt'], waitsecs=3, displayFailure=True, debug=False )
        endtime = time.time()
        logger.info('count of confirm buttons returned:%d:seconds:%d', len(results),  endtime-starttime)

        # click on the confirm button
        logger.info('click on the confirm button')
        starttime = time.time()
        results[0].click()
        
        # look for the pdf page to arrive with the move to next page button
        logger.info('waiting for pdf page to render')
        results = find_elements_looped(driver, 'toolbar-next-button', 'byClassName', 'nextPageButton', '', loopcnt=optiondict['findelementsloopcnt_pdfopen'], waitsecs=3, displayFailure=True, debug=False )
        
        # stepping through pages
        for i in range(int(pagecnt)):
            results = find_elements_looped(driver, 'toolbar-next-button', 'byClassName', 'nextPageButton', '', loopcnt=optiondict['findelementsloopcnt_nextpage'], waitsecs=3, displayFailure=True, debug=False )
            if not results:
                raise Exception( "NextPageButton Not Found" )
            endtime = time.time()
            logger.info('page count:%d:seconds:%d', i, endtime-starttime)
            logger.info('number of next page buttons from pdf viewer:%d', len(results))
            logger.info('click next page')
            results[0].click()
            logger.info('wait between pages time:%d', optiondict['pagewait'])
            time.sleep(optiondict['pagewait'])
            starttime = time.time()
            
    # done so close the browser
    driver.quit()

# eof
