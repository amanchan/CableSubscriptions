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

def retrieveFilingData(br, opt, commName):
    br.select_form(name='form1')
    tmp=[]
    tmp.append(opt)

    br.form['idAndLegalName'] = tmp
#   br.form[] ='Get Filing Periods'
    br.submit('getFilingPeriods')

    html = br.response().read()
    soup = BeautifulSoup(html)
#   soup = soup.prettify(formatter=lambda s: s.replace(u'\xa0', '|'))

#    print (soup)
    forms = mechanize.ParseResponse(br.response(), backwards_compat=False)
    form = forms[0]
    control1 = form.controls[0] # the select
#    fileCommunity.writelines("****************************************************************************************************\n")
    fileCommunity.writelines("Community Name : %s\n"  % commName)
    fileCommunity.writelines("Legal Name: %s\n" % opt)
#    fileCommunity.writelines("****************************************************************************************************\n")
#    valOpts1 = [item.attrs['value'] for item in control1.items]
#    fileCommunity.writeLines( "%s\n" % item for item in valOpts1 )
    valOpts1 = [item.attrs['value'] for item in control1.items]
    opt1= []
    contents = []
    contentsOld = []
    opt1 = opt.split(' ',1)
#    mySelect = soup.find('select').prettify(formatter=lambda s: s.replace(u'\xa0', '|'))
    mySelect = soup.find('select') #.prettify(formatter=lambda s: re.sub(r'(\xa0)+', "|", s))
#    contents1 = [re.sub(r'null', "|", opt) + re.sub(r'(\xa0)+', "|", x.text) for x in mySelect.find_all('option')]
    contents1 = [srchState + "|" + commName + "|" + opt1[0] + "|" + re.sub(r'(\xa0)+', "|", x.text) for x in mySelect.find_all('option')]
    contents2 = [re.compile(r"(PENDING.*\|.*\|.*\|.*\|)(.*\|.*)").sub(r"\1 |\2", x) for x in contents1]
    for filingDataLine in contents2:
        if (filingDataLine.find('2014/') >= 0):
            contents.append(filingDataLine)
        else:
            contentsOld.append(filingDataLine)

#    print (contents)
    dataFile.writelines( "%s\n" % item for item in contents )
    pass

# Retrieve Data from about Communities from
# http://licensing.copyright.gov/search/SelectCommunity.jsp
def retrieveData(br, opt):
    br.select_form(name='form1')
    tmp=[]
    tmp.append(opt)

    br.form['communities'] = tmp

    br.submit()
    namedCommunity = []
    namedCommunity = opt.split(' ',3)

    html = br.response().read()
    soup = BeautifulSoup(html)
#    soup = soup.prettify(formatter=lambda s: s.replace(u'\xa0', '|'))

#    print (soup)
    forms = mechanize.ParseResponse(br.response(), backwards_compat=False)
    form = forms[0]
    control1 = form.controls[0] # the select
    communityNameOpts = [item.attrs['value'] for item in control1.items]
    fileCommunity.writelines("****************************************************************************************************\n")
#    fileCommunity.writelines("Legal Name: %s\n" % opt)
#    fileCommunity.writelines("****************************************************************************************************\n")
    fileCommunity.writelines( "%s\n" % item for item in communityNameOpts )
#    valOpts1 = [item.attrs['value'] for item in control1.items]
#    mySelect = soup.find('select').prettify(formatter=lambda s: s.replace(u'\xa0', '|'))
#    mySelect = soup.find('select') #.prettify(formatter=lambda s: re.sub(r'(\xa0)+', "|", s))
#    contents = [opt + re.sub(r'(\xa0)+', "|", x.text) for x in mySelect.find_all('option')]
#    print (contents)
#    fileCommunity.writerow(contents)
#    fileCommunity.writelines( "%s\n" % item for item in contents )

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
#'AL', 'AK', 'AZ', 'AR', CO, , GA, HI, ID, IL, IN, IA, KS, KY, LA, ME, MI, MN, MS, MO,MT,NE,NV,--NH,
#CT, MA, RI, NY, PA, DE, NJ, MD, VA, DC, NC, TX, FL, , 'VT'
srchState = 'DE'
#print legalNameOpts
#destPath = 'c:\\users\\anilm\\'
destPath = 'C:\\Users\\amanchanda\\Downloads\\Research\\Video_20140918\\AssciatedCommunities\\'
communityFilename = destPath +  srchState + '_Communities' + '.txt'
fileCommunity = open(communityFilename,'a');
# Write the header
fileCommunity.writelines("State|Community|Id|Filing Period|SA|Receipt Date|Gross Receipts|Filing Fee|Royalty Payment|Interest|1st Set Subscr|1st Set Rate|Correspondence?|File Available?|Legal Name\n")
##inFilename = destPath + "CommunityLists\\" + srchState + '_CommIn' + '.txt'
##infile = open(inFilename,'r');
##srchCommunities = infile.readlines()



#'A','B','C','d'
srchCommunities= ['a','B','C','d','E','F','G', 'H', 'I', 'J', 'K' ,'L','M', 'N','O','P', 'Q', 'R','S','T', 'U','V','W','X','Y','Z']
#srchCommunities= ['']
for srchCommunity in srchCommunities:
    srchCommunity = srchCommunity.rstrip('\r\n')
    # The site we will navigate into, handling it's session
    #br.open(mainSite)
    skip = 0
    finished = "false"
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
#dataFile.close()
#infile.close()


