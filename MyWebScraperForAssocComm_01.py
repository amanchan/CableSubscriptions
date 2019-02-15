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

def openSite(mainSite, tries):
    try:
        br.open(mainSite)
        return 0
    except (mechanize.HTTPError,mechanize.URLError) as e:
        fileCommunity.close()
        dataFile.close()
        time.sleep(25)
        tries = tries + 1
        return tries
    pass

def openPage():
    status = openSite(mainSite, 2)
    if (status != 0):
        exit

    # Select the first (index zero) form
    br.select_form(nr=0)

    # Set the for parameter to srchString
    br.form['community'] = srchCommunity
    br.form['state'] = [srchState]
    # Submit the form to go to
    # http://licensing.copyright.gov/search/DisplayCommunity.jsp
    br.submit()

    # Read the HTML on page
    # http://licensing.copyright.gov/search/DisplayCommunity.jsp
    html = br.response().read()
    soup = BeautifulSoup(html)
    #print (soup)

    pass

# Retrieve Filing Data for a community from
# http://licensing.copyright.gov/search/SelectFilingPeriod2.jsp
def retrieveAssociatedCommunities(br, opt1, primComm):
    br.select_form(name='form1')
    tmp=[]
    tmp.append(opt1)

    br.form['filingPeriods'] = tmp
#   br.form[] ='filingPeriods'
    br.submit('getAssociatedCommunities')

    html = br.response().read()
    soup = BeautifulSoup(html)
#   soup = soup.prettify(formatter=lambda s: s.replace(u'\xa0', '|'))
    list_items = [list_item for list_item in soup.findAll('h4')]

    doneProcessing1 = 1
    try:
        systemId = list_items[0].get_text().split(':', 2)
        legalName = list_items[1].get_text().split(':', 2)
        filingPeriod = list_items[2].get_text().split(':', 2)
    except:
        doneProcessing1 = 0

#    print (soup)
    forms = mechanize.ParseResponse(br.response(), backwards_compat=False)
    form = forms[0]
    control1 = form.controls[0] # the select
    valOpts1= [item.attrs['value'] for item in control1.items]
    mySelect = soup.find('select')
    contents = []
    contents1 = [(x.split(' ', 1)[1].strip() + "!" + x.split(' ', 1)[0].strip()) for x in valOpts1]
    contents2 = [re.sub(r'(\*\s)+', "|y|", x) for x in contents1]
    doneProcessing = 0
    while (doneProcessing == 0):
        doneProcessing = 1
        try:
            contents4 = [re.sub(r'^([^\|])+', "|n|" + x, x) for x in contents2]
            contents3 = [re.sub(r'(\!)+', "|" , x) for x in contents4]
        except:
            doneProcessing = 0
            processError(contents2)
            contents2.remove(x)
        continue

#    contents2 = [primComm[0] + "|" + primComm[1] + "|" + legalName[1].strip() + "|" + (filingPeriod[1].strip()  + "|" + systemId[1].strip() + "|" +  x.split(' ', 1)[1].strip()) for x in valOpts1]
    contents = [(primComm[0] + "|" + primComm[1] + "|" + legalName[1].strip() + "|" + filingPeriod[1].strip()  + "|" + systemId[1].strip() + x) for x in contents3]

#    print (contents)
    fileCommunity.writelines( "%s\n" % item for item in contents )
    pass

def retrieveFilingData(br, opt2, commName):
    br.select_form(name='form1')
    tmp=[]
    tmp.append(opt2)

    br.form['idAndLegalName'] = tmp
#   br.form[] ='Get Filing Periods'
    br.submit('getFilingPeriods')

    html = br.response().read()
    soup = BeautifulSoup(html)
#   soup = soup.prettify(formatter=lambda s: s.replace(u'\xa0', '|'))
    list_items = [list_item for list_item in soup.findAll('h4')]
    systemId = list_items[0].get_text().split(':',2)[1]
    commTemp = list_items[1].get_text().split(':',2)[1]
    primCommunity = commTemp.strip().split(' ', 1)

#    print (soup)
    forms = mechanize.ParseResponse(br.response(), backwards_compat=False)
    form = forms[0]
    control1 = form.controls[0] # the select
#    valOpts1 = [item.attrs['value'] for item in control1.items]
#    fileCommunity.writeLines( "%s\n" % item for item in valOpts1 )
    valOpts1 = [item.attrs['value'] for item in control1.items]
    opt4= []
    contents = []
    contentsOld = []
    opt4 = opt2.split(' ',1)
#    mySelect = soup.find('select').prettify(formatter=lambda s: s.replace(u'\xa0', '|'))
    mySelect = soup.find('select') #.prettify(formatter=lambda s: re.sub(r'(\xa0)+', "|", s))
#    contents1 = [re.sub(r'null', "|", opt) + re.sub(r'(\xa0)+', "|", x.text) for x in mySelect.find_all('option')]
    contents1 = [primCommunity[0] + "|" + primCommunity[1] + "|" + opt4[0] + "|" + re.sub(r'(\xa0)+', "|", x.text) for x in mySelect.find_all('option')]
    contents2 = [re.compile(r"(PENDING.*\|.*\|.*\|.*\|)(.*\|.*)").sub(r"\1 |\2", x) for x in contents1]
#    for filingDataLine in contents2:
#        if (filingDataLine.find('2014/') >= 0 or filingDataLine.find('2013/') >= 0 or filingDataLine.find('2012/') >= 0):
#            contents.append(filingDataLine)
#        else:
#            contentsOld.append(filingDataLine)

#    print (contents)
#    dataFile.writelines( "%s\n" % item for item in contents )
#    dataFileHist.writelines( "%s\n" % item for item in contentsOld )

    for filingDataLine in valOpts1:
        if (filingDataLine.find('2014/') >= 0 or filingDataLine.find('2013/') >= 0 or filingDataLine.find('2012/') >= 0):
            retrieveAssociatedCommunities(br, filingDataLine, primCommunity)
            response = br.back(1)
    pass

# Retrieve Data from about Communities from
# http://licensing.copyright.gov/search/SelectCommunity.jsp
def retrieveData(br, opt3):
    br.select_form(name='form1')
    tmp=[]
    tmp.append(opt3)

    br.form['communities'] = tmp
    br.submit()

    namedCommunity = []
    namedCommunity = opt3.split(' ',2)

    html = br.response().read()
    soup = BeautifulSoup(html)
#    soup = soup.prettify(formatter=lambda s: s.replace(u'\xa0', '|'))

#    print (soup)
    forms = mechanize.ParseResponse(br.response(), backwards_compat=False)
    form = forms[0]
    control1 = form.controls[0] # the select
    communityNameOpts = [item.attrs['value'] for item in control1.items]

    if len(communityNameOpts) > 0:
        retrieveFilingData(br, communityNameOpts[0], namedCommunity[2])
        response = br.back(1)
#    html = response.read()
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
#print parser.parse_args(['--name'])
mainSite = 'http://licensing.copyright.gov/search/SearchCommunity.jsp'
srchStates = ['Alabama', 'Alaska', 'Arizona', 'Arkansas']
#'AL', 'AK', 'AZ', 'AR', 'CA', CO, CT, DE, FL, GA, HI, ID, IL, IN, IA, KS, KY, LA, ME, MD, MA, MI, MN, MS, MO,MT,NE,NV,--NH,
# NJ, NM, NY, NC, ND, OH, OK, OR, PA, RI, SC,SD, TN, TX, UT, VT, VA, WA, WI, WV, WY
# AS, DC, FM, GU, MH, MP, PW, PR, VI
#MN,MS
srchState = 'ID'
# AL, AK, AZ, AR, CA, CO, CT, 'DE', FL, GA, HI, IL, IN, IA, KS, KY, LA
# MT, NC, NJ, NY, TN, TX, UT, VA, WA, WI, WV, WY
#print legalNameOpts

destPath = 'C:\\Users\\amanchanda\\Downloads\\Research\\Video_05262015\\Comm\\'
dataFileName = destPath + srchState + '_FilingData.txt'
dataFile = open(dataFileName,'a');

dataFileNameHist = destPath + srchState + '_FilingData_Hist.txt'
dataFileHist = open(dataFileNameHist,'a');

communityFilename = destPath +  srchState + '_AssocCommunities' + '.txt'
fileCommunity = open(communityFilename,'a');
fileCommunity.writelines("State|Primary Community|LegalName|Filing Period|PrimaryID|FirstCommunityServedFlag|Assoc Community\n")

# Write the header
dataFile.writelines("State|Community|Id|Filing Period|SA|Receipt Date|Gross Receipts|Filing Fee|Royalty Payment|Interest|1st Set Subscr|1st Set Rate|Correspondence?|File Available?|Legal Name\n")
dataFileHist.writelines("State|Community|Id|Filing Period|SA|Receipt Date|Gross Receipts|Filing Fee|Royalty Payment|Interest|1st Set Subscr|1st Set Rate|Correspondence?|File Available?|Legal Name\n")
processedSystemId = []
#srchCommunities= ['C','D','E','F','G', 'H', 'I', 'J', 'K' ,'L']
srchCommunities= ['A','B','C','d','E','F','G', 'H', 'I', 'J', 'K' ,'L','M', 'N','O','P', 'Q', 'R','S','T', 'U','V','W','X','Y','Z']
#srchCommunities= ['']
for srchCommunity in srchCommunities:
    srchCommunity = srchCommunity.rstrip('\r\n')
    # The site we will navigate into, handling it's session
    #br.open(mainSite)
    skip = 0
    finished = "false"
    print 'Search Community:' + srchCommunity
    while (finished == "false"):
        finished = "true"
        try:
            openPage()
        except (mechanize.HTTPError,mechanize.URLError) as e:
            #fileCommunity.close()
            #dataFile.close()
            break ;
        # Form with name 'form1' has a select list of options (Community names) to choose
        forms = mechanize.ParseResponse(br.response(), backwards_compat=False)

        #forms = mechanize.ParseString(html, 'form1')
        form = forms[0]

        #print form
        #very useful!

        # The select control element
        control = form.controls[0]
        communityOpts = [item.attrs['value'] for item in control.items]
        i = 0
        if len(communityOpts) > 0:
            if communityOpts[0].find('no records found') < 0:
                for aCommunity in communityOpts:
                    if (skip > 0):
                        skip = skip - 1
                    else:
                        #print control
                        try:
                            namedCommunity = []
                            namedCommunity = aCommunity.split(' ',2)
                            id = namedCommunity[0].strip()
                            if (id in processedSystemId):
                                continue
                            processedSystemId.append(id)
                            retrieveData(br, aCommunity)
                            i = i + 1
                        except (mechanize.HTTPError,mechanize.URLError) as e:
                            #fileCommunity.close()
                            #dataFile.close()
                            skip = i
                            i = 0
                            finished = "false"
                            break
                        response = br.back(1)
                        html = response.read()
fileCommunity.close()
dataFile.close()
dataFileHist.close()


