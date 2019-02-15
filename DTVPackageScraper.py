#-------------------------------------------------------------------------------
# Name:        MyWebScraper
# Purpose:  To automate retrieval of data from website
#       http://licensing.copyright.gov/search/SearchLegalName.jsp'
#       This site accepts a search string like 'Comcast' and takes you to page
#       http://licensing.copyright.gov/search/DisplayLegalName.jsp
#       From this page, user can select the actual company name and view
#       associated information (ID number, first community and state) on page
#       http://licensing.copyright.gov/search/SelectCommunity.jsp
#       From this page user select the community,
#       then click appropriate button to view either filing period or
#       associated communities information.
#       Get Filing Periods take you to page
#       http://licensing.copyright.gov/search/SelectFilingPeriod2.jsp
#       Get Associated communities takes you to page:
#       http://licensing.copyright.gov/search/DisplayAssociatedCommunities.jsp
#       You can go to the associated communities page given beow from
#       "Filing Periods" page as well
#       http://licensing.copyright.gov/search/DisplayAssociatedCommunities2.jsp
# Author:      AnilM
#
# Created:     26/04/2013
# Copyright:   (c) AnilM 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import mechanize
import cookielib
from bs4 import BeautifulSoup
import html2text
import twill.commands
import re,sys
import argparse
import csv
import time

def openSite(mainSite, file, tries):
    try:
        br.open(mainSite)
        return 0
    except (mechanize.HTTPError) as e:
        print (e.reason, myZip)
        print e.code

        if (e.code == 404):
            return -1
        elif (e.code >=400):
            file.close()
            time.sleep(10)
#            file = open(zipFile,'a');
            tries = tries + 1
            return -2
    except (mechanize.URLError) as e1:
        print (e1.reason, myZip)
        file.close()
        time.sleep(10)
#        file = open(zipFile,'a');
        tries = tries + 1
        return tries
    pass

# Main Start here. Get the search string from command line
parser = argparse.ArgumentParser()
parser.add_argument('--url', help='url help')
parser.add_argument('--name', help='name help')
args = parser.parse_args()

# Browser
br = mechanize.Browser()

# Cookie Jar
cj = cookielib.LWPCookieJar()
br.set_cookiejar(cj)

# Browser options
br.set_handle_equiv(True)
br.set_handle_gzip(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)

# Follows refresh 0 but not hangs on refresh > 0
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

# User-Agent (this is cheating, ok?)
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

# Search for Comcast
mainSite = 'http://www.directstartv.com/directv_current_offer.html?formLocation=packagesPage'
myZip = '75024'
#destPath = 'c:\\users\\anilm\\'
destPath = 'C:\\Users\\amanchanda\\Downloads\\Research\\Zips\\'
#destPath = 'C:\\Users\\Anil\\Research\\Zips\\'
##startZip = 13043
##zipFile = destPath + 'AZipSummary_' + '{:0>5d}'.format(startZip) + '.txt'
zipFile = destPath + 'ZipSummaryListN_000.txt'
file = open(zipFile,'a');
startZip = 2866
#file.writelines("Zip|Multi|Counties|State|Area Code|City Type\n")

for imyZip in range(startZip, 99999):
    myZip = '{:0>5d}'.format(imyZip)
    listCounties = ''
    listStates = ''
    multi = 'No'


# The site we will navigate into, handling it's session
    tries = 0
    status = openSite(mainSite, file, tries)
    if (status != 0):
        if (status == -1):
            continue
        if (file.closed == True):
                file = open(zipFile,'a');
        status = openSite(mainSite,file, tries)
        if (status != 0):
            sys.exit(0)
        else:
            if (file.closed == True):
                file = open(zipFile,'a');

    html = br.response().read()
    soup = BeautifulSoup(html)

#print (soup)
# Select the first (index zero) form
#br.select_form(nr=0)
    counties = soup.find(title="Counties :: The counties or parishes where the ZIP Code resides. ZIP Codes can cross county lines and frequently do.")
    if counties is None:
        print (myZip, " Not found0")
        continue
    counties1 = counties.find_parent("tr")
    if counties1 is None:
        print (myZip, " Not found1")
        continue
    counties2 = counties1.find_all("a")
    if counties2 is None:
        print (myZip, counties2)
        continue
    else:
        tag_all = counties2 #.findAll("a")
        i = 0
        for tag in tag_all:
            countyState=[]
            countyState = tag.getText().split(',', 1)
            if (i == 0):
                i = i + 1
            elif (i == 1):
                i = i + 1
                county = countyState[0]
                listStates = countyState[1]
                listCounties = countyState[0] + ' '
            else:
                county = countyState[0]
                listStates = listStates + ',' + countyState[1]
                listCounties = listCounties.strip(" ") + ',' + countyState[0]
                multi = 'Yes'

        aLine = myZip + "|" + multi + "|" + listCounties.strip(" ") + "|" + listStates.strip(" ")
        areaCode = ''
        areaCodeTag = soup.find(title="Area Code :: Telephone area code(s) of this ZIP Code. ZIP Codes that border states or are in large population areas, several Area Codes can be available.")
        if areaCodeTag is None:
            aLine = aLine + "|"
        else:
            areaCodeTag1 = areaCodeTag.find_parent("tr")
            if areaCodeTag1 is None:
                aLine = aLine + "|"
            else:
                areaCodeTag2 = areaCodeTag1.contents[1]
                if areaCodeTag2 is None:
                    aLine = aLine + "|"
                else:
                    areaCodeTag4 = areaCodeTag2.get_text()
                    print (areaCodeTag4)
                    aLine = aLine + "|" + areaCodeTag4

        cityType = ''
        cityTypeTag = soup.find(href= "/zip_database_fields.asp#citytype")
        if cityTypeTag is None:
            aLine = aLine + "|"
        else:
            cityTypeTag1 = cityTypeTag.find_parent("tr")
            if cityTypeTag1 is None:
                aLine = aLine + "|"
            else:
                cityTypeTag2 = cityTypeTag1.findAll('td')
                if cityTypeTag2 is None:
                    aLine = aLine + "|"
                else:
                    cityTypeTag3 = cityTypeTag2[1]
                    if cityTypeTag3 is None:
                        aLine = aLine + "|"
                    else:
                        cityTypeTag4 = cityTypeTag3.get_text()
                        print (cityTypeTag4)
                        aLine = aLine + "|" + cityTypeTag4
        aLine = aLine + "\n"
        file.writelines(aLine)
        print(aLine)
#for link in soup.findAll('a'):
#    print link['title']
#    if (link['title'] != null):
#        i = link['title'].find("Multi County");
#        if (i > 0):
#            print link['title']

# Set the for parameter to srchString
#br.form['selectedLegalName'] = srchString

# Submit the form to go to
# http://licensing.copyright.gov/search/DisplayLegalName.jsp
#br.submit()

# Read the HTML on page
# http://licensing.copyright.gov/search/DisplayLegalName.jsp



# Form with name 'form1' has a select list of options (Company names) to choose
#forms = mechanize.ParseResponse(br.response(), backwards_compat=False)

#forms = mechanize.ParseString(html, 'form1')
#form = forms[0]

#print form
#very useful!

# The select control element
#control = form.controls[0]



#file.writelines( "Search Legal Names: %s\n" % srchString )
#file.writelines("****************************************************************************************************\n")
#legalNameOpts = [item.attrs['value'] for item in control.items]
#file.writelines( "%s\n" % item for item in legalNameOpts )
file.close()




