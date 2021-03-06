#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""process_detailed_bill.py: Init for this module."""

__author__ = "monkee"
__license__ = "GPLv3.0"
__version__ = "1.2.3"
__maintainer__ = "monk-ee"
__email__ = "magic.monkee.magic@gmail.com"
__status__ = "Development"


import yaml
import csv
from splunk_utilities import *
from datetime import datetime


def main():
    #setup error handling file
    if not os.path.isfile(ERRORLOGFILE):
        handleERRORLOGFILE = open(ERRORLOGFILE, 'w')
    else:
        handleERRORLOGFILE = open(ERRORLOGFILE, 'ab')

    #load configuration
    configurationStream = open(AWSCONFIGFILE, 'r')
    configurationObject = yaml.load(configurationStream)

    #now set detailed billing file
    BILLINGREPORTZIPFILE = os.path.join(path, 'etc', 'apps', 'SplunkAppforAWSBilling', 'tmp',
                                        str(configurationObject['s3']['account_number']) + '_detailed_billing.zip')

    #file name
    billingFileName = str(configurationObject['s3'][
        'account_number']) + "-aws-billing-detailed-line-items-with-resources-and-tags-" + datefilename() + ".csv.zip"

    #now read that stupid file
    csvFileName = str(configurationObject['s3'][
        'account_number']) + "-aws-billing-detailed-line-items-with-resources-and-tags-" + datefilename() + ".csv"
    BILLINGREPORTZIPDIRCSV = os.path.join(path, 'etc', 'apps', 'SplunkAppforAWSBilling', 'csv', csvFileName)

    try:
        ifile = open(BILLINGREPORTZIPDIRCSV, 'rb')
    except IOError:
        #bail out the file does not exist yet
        sys.exit(0)

    #ok read this file
    reader = csv.reader(ifile)

    #processnewcsv
    processedCSVFileName = str(configurationObject['s3'][
        'account_number']) + "-aws-billing-detailed-line-items-with-resources-and-tags-" + datefilename() + ".processed.csv"
    BILLINGREPORTZIPDIRPROCESSEDCSV = os.path.join(path, 'etc', 'apps', 'SplunkAppforAWSBilling', 'csv',
                                                   processedCSVFileName)

    #more complex file situation - the processed file already exists
    #we only want to append the file differences and throw away the header row
    processedFileExists = True
    try:
        with open(BILLINGREPORTZIPDIRPROCESSEDCSV):
            pass
    except IOError:
        #ok now we need to take another path
        processedFileExists = False

    if processedFileExists == False:
        #process new csv
        print "processing a totally new file"
        processedCSVHandle = open(BILLINGREPORTZIPDIRPROCESSEDCSV, 'wb')

        # go loop go
        rownum = 0
        for row in reader:
            newrow = ""
            if rownum == 0:
                #format the header row
                newrow += '"Timestamp",'
                newrow += '"AccountNumber",'
                for col in row:
                    newrow += '"' + str(col) + '",'
                newrow = newrow[:-1]
                newrow += '\r\n'
            elif row[8] == "":
                 #if the subscriptionid is blank - i dont want that record
                rownum += 1
                continue
            else:
                if row[15] != "":
                    try:
                        rowdate = datetime.strptime(row[15], '%Y-%m-%d %H:%M:%S')
                        newdate = rowdate.strftime("%b %d %Y %I:%M:%S %p %z")
                    except Exception:
                        sys.exc_clear()
                        falsedate = datefilename() + "-01 00:00:00"
                        rowdate = datetime.strptime(falsedate, '%Y-%m-%d %H:%M:%S')
                        newdate = rowdate.strftime("%b %d %Y %I:%M:%S %p %z")
                else:
                    falsedate = datefilename() + "-01 00:00:00"
                    rowdate = datetime.strptime(falsedate, '%Y-%m-%d %H:%M:%S')
                    newdate = rowdate.strftime("%b %d %Y %I:%M:%S %p %z")

                newrow = str(newdate) + ', '
                newrow += str(configurationObject['s3']['account_number']) + ', '
                for col in row:
                    newrow += '"' + str(col) + '",'
                newrow = newrow[:-1]
                newrow += '\r\n'
            processedCSVHandle.write(newrow)
            rownum += 1
        #dont shut it you idiot
        processedCSVHandle.close()
    else:
        #process old csv
        #ok at this point we need to count the row total difference
        processedCSVRowCount = sum(1 for row in csv.reader(open(BILLINGREPORTZIPDIRPROCESSEDCSV)))

        #process old csv
        processedCSVHandle = open(BILLINGREPORTZIPDIRPROCESSEDCSV, 'ab')

        # go loop go
        rownum = 0
        for row in reader:
            newrow = ""
            #if the subscriptionid is blank - i dont want that record
            if row[8] == "":
                rownum += 1
                continue
                #format the header row
            if rownum < processedCSVRowCount:
                #do nothing
                rownum += 1
                continue
            else:
                if row[15] != "":
                    try:
                        rowdate = datetime.strptime(row[15], '%Y-%m-%d %H:%M:%S')
                        newdate = rowdate.strftime("%b %d %Y %I:%M:%S %p %z")
                    except Exception:
                        sys.exc_clear()
                        falsedate = datefilename() + "-01 00:00:00"
                        rowdate = datetime.strptime(falsedate, '%Y-%m-%d %H:%M:%S')
                        newdate = rowdate.strftime("%b %d %Y %I:%M:%S %p %z")
                else:
                    falsedate = datefilename() + "-01 00:00:00"
                    rowdate = datetime.strptime(falsedate, '%Y-%m-%d %H:%M:%S')
                    newdate = rowdate.strftime("%b %d %Y %I:%M:%S %p %z")

                newrow = str(newdate) + ', '
                newrow += str(configurationObject['s3']['account_number']) + ', '
                for col in row:
                    newrow += '"' + str(col) + '",'
                newrow = newrow[:-1]
                newrow += '\r\n'
            processedCSVHandle.write(newrow)
            rownum += 1
        #dont shut it you idiot
        processedCSVHandle.close()
    #close that pesky open file
    ifile.close()

if __name__ == "__main__":
    main()