# Setting up your machine

The following tools will be needed
1. Python 3
2. Selenium
3. requests
3. Browsers installed (Chrome and/or firefox)
4. Selenium Browser drivers:  Chromedriver, geckodriver

## Python3

Find and install the python 3 interpreter for your machine

After installing standard python we will need to add some additional libraries

### Requests
you need to install the library "requests"
via (pip install requests)


## Selenium

The following web page explains how to install selenium and where to get the drivers

https://selenium-python.readthedocs.io/installation.html

We do NOT need selenium server at this time.

### Chromedriver
make sure the chromedriver you download and install is the version that
matches the version in your chrome browser - or this tool will not work.

To check what version is your browser:
- click on the the "triple dots" in the upper right area of the browser.
- Select help -> About Google Chrome
- And it will display your browser version

Make sure you install the selenium drivers in a folder that is in your PATH


# Running instances of this test

## Windows
- Open a command window
- Go to the directory where the python programs exist
- Validate you are in the right directory by running the directory command:  dir
-- you should see in the listing "ts_test.py", if not - you are not in the right directory
-run the following command line to start up a unique instance of the program
(you can run this command line multiple times in order to get multiple instances running)
-- start python ts_test.py
- you should see a new command window open and a browser start up and the test will run


# Command line options to change how the program works

| option | type | value | description |
| ------ | ---- | ----- | ----------- |
| AppVersion |  | 1.04 | defines the version number for the app |
| tsfile |  |  | defines the csv filename containing the list of urls of trusted shares to process and # of pages to step through |
| url |  | https://ppe.bancnow.com/collaborations/fVHjFLSC3N4D/granted_access/ifF15XnJIiWRMBQ/?action=open&filename=Sculptor%20Master%20Fund%20Ltd.%20Monthly%20Letter%20and%20Transparency%20Report%20-%20May%202020.pdf | defines the url of the Trusted share we are checking |
| pagecnt | int | 3 | defines the number of pages to step through in the pdf |
| pagewait | int | 3 | defines the number of seconds to sleep between page changes |
| findelementsloopcnt_pdfopen | int | 25 | defines the max number of times we loop for 3 seconds waiting for the pdf to open and render |
| findelementsloopcnt_nextpage | int | 8 | defines the max number of times we loop for 3 seconds waiting for the pdf page to change |
| utcstarttime | datetimezone | None | defines the UTC start time to start processing - we will wait until this time arrives - used to kick off a coordinate load test |
| startinmin | int | 0 | defines the number of minutes in the future to start running, which returns back the command for others to execute - see utcstarttime |
| browser |  | chrome | defines which browser we are using to automate with (chrome, ff, firefox) |

## MacOS
- Open a Terminal
- Go to the directory where the python programs exist
- Validate you are in the right directory by running the directory command:  ls
-- you should see in the listing "ts_test.py", if not - you are not in the right directory
- run the following command line to start up a instance of the program
--  ./run.sh instnum=1, where instnum is a number of the instances of the program
- appropriate number of browsers start up and the test will run in each of them
- for more command line options see table above
