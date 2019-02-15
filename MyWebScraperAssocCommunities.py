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

# Retrieve Filing Data for a community from
# http://licensing.copyright.gov/search/SelectFilingPeriod2.jsp
def retrieveAssociatedCommunities(br, opt):
    br.select_form(name='form1')
    tmp=[]
    tmp.append(opt)

    br.form['communities'] = tmp
#   br.form[] ='Get Associated Communites'
    br.submit('getAssociatedCommunities')

    html = br.response().read()
    soup = BeautifulSoup(html)
#   soup = soup.prettify(formatter=lambda s: s.replace(u'\xa0', '|'))

    print (soup)
    forms = mechanize.ParseResponse(br.response(), backwards_compat=False)
    form = forms[0]
    control1 = form.controls[0] # the select
#    fileCommunity.writelines("****************************************************************************************************\n")
#    fileCommunity.writelines("Legal Name: %s\n" % opt)
#    fileCommunity.writelines("****************************************************************************************************\n")
#    valOpts1 = [item.attrs['value'] for item in control1.items]
#    fileCommunity.writeLines( "%s\n" % item for item in valOpts1 )
    valOpts1 = [item.attrs['value'] for item in control1.items]
#    mySelect = soup.find('select').prettify(formatter=lambda s: s.replace(u'\xa0', '|'))
    mySelect = soup.find('select') #.prettify(formatter=lambda s: re.sub(r'(\xa0)+', "|", s))
    opt1= []
    opt1 = opt.split(' ',2)
#    contents2 = [re.sub(r'(\*)+', "|y|", x.text) for x in mySelect.find_all('option')]
#    contents1 = [re.sub(r'null', "|", legalName) + "|" + opt1[0] + "|" + re.sub(r'null', "|", opt1[1]) + re.sub(r'(\xa0)+', "|n|", x) for x in contents2]
    contents2 = [srchString + "|" + re.sub(r'null', "|", legalName) + "|" + opt1[0] + "|" + re.sub(r'null', "", opt1[2]) + "|"+ re.sub(r'(\xa0)+', "|n|", x.text) for x in mySelect.find_all('option')]
    contents3 = [re.sub(r'(\*)+', "|y|", x) for x in contents2]
    contents4 = [re.sub(r'(\|y\| )+', "|y|", x) for x in contents3]
    contents = [re.sub(r'(\|n\| )+', "|n|", x) for x in contents4]
#    contents = [re.sub(r'^ ', '', x) for x in contents3]
#re.sub(r'^[^a]*', '')
#    contents = [re.compile(r"(PENDING.*\|.*\|.*\|.*\|)(.*\|.*)").sub(r"\1 |\2", x) for x in contents1]

#    print (contents)
    fileAssocCommunity.writelines( "%s\n" % item for item in contents )
    pass

def retrieveFilingData(br, opt):
    br.select_form(name='form1')
    tmp=[]
    tmp.append(opt)

    br.form['communities'] = tmp
#   br.form[] ='Get Filing Periods'
    br.submit('getFilingPeriods')

    html = br.response().read()
    soup = BeautifulSoup(html)
#   soup = soup.prettify(formatter=lambda s: s.replace(u'\xa0', '|'))

    print (soup)
    forms = mechanize.ParseResponse(br.response(), backwards_compat=False)
    form = forms[0]
    control1 = form.controls[0] # the select
#    fileCommunity.writelines("****************************************************************************************************\n")
#    fileCommunity.writelines("Legal Name: %s\n" % opt)
#    fileCommunity.writelines("****************************************************************************************************\n")
#    valOpts1 = [item.attrs['value'] for item in control1.items]
#    fileCommunity.writeLines( "%s\n" % item for item in valOpts1 )
    valOpts1 = [item.attrs['value'] for item in control1.items]
    opt1= []
    opt1 = opt.split(' ',1)
#    mySelect = soup.find('select').prettify(formatter=lambda s: s.replace(u'\xa0', '|'))
    mySelect = soup.find('select') #.prettify(formatter=lambda s: re.sub(r'(\xa0)+', "|", s))
#    contents1 = [re.sub(r'null', "|", opt) + re.sub(r'(\xa0)+', "|", x.text) for x in mySelect.find_all('option')]
    contents1 = [opt1[0] + "|" + re.sub(r'null', "", opt1[1]) + "|" + re.sub(r'(\xa0)+', "|", x.text) for x in mySelect.find_all('option')]
    contents = [re.compile(r"(PENDING.*\|.*\|.*\|.*\|)(.*\|.*)").sub(r"\1 |\2", x) for x in contents1]

#    print (contents)
#    fileCommunity.writerow(contents)
    fileData.writelines( "%s\n" % item for item in contents )
    pass

# Retrieve Data from about Communities from
# http://licensing.copyright.gov/search/SelectCommunity.jsp
def retrieveData(br, opt):
    br.select_form(name='form1')
    tmp=[]
    tmp.append(opt)

    br.form['communities'] = tmp
    br.submit()

    html = br.response().read()
    soup = BeautifulSoup(html)
#    soup = soup.prettify(formatter=lambda s: s.replace(u'\xa0', '|'))

    print (soup)
    forms = mechanize.ParseResponse(br.response(), backwards_compat=False)
    form = forms[0]
    control1 = form.controls[0] # the select
    communityNameOpts = [item.attrs['value'] for item in control1.items]
#    fileCommunity.writelines("****************************************************************************************************\n")
#    fileCommunity.writelines("Legal Name: %s\n" % opt)
#    fileCommunity.writelines("****************************************************************************************************\n")
#    valOpts1 = [item.attrs['value'] for item in control1.items]
#    fileCommunity.writeLines( "%s\n" % item for item in valOpts1 )
    valOpts1 = [item.attrs['value'] for item in control1.items]
#    mySelect = soup.find('select').prettify(formatter=lambda s: s.replace(u'\xa0', '|'))
    mySelect = soup.find('select') #.prettify(formatter=lambda s: re.sub(r'(\xa0)+', "|", s))
    contents = [opt + re.sub(r'(\xa0)+', "|", x.text) for x in mySelect.find_all('option')]
#    print (contents)
#    fileCommunity.writerow(contents)
    fileCommunity.writelines( "%s\n" % item for item in contents )
    for communityVal in communityNameOpts:
#       print control
#        retrieveFilingData(br, communityVal)
#        response = br.back(1)
#        html = response.read()
        retrieveAssociatedCommunities(br, communityVal)
        response = br.back(1)
        html = response.read()
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
mainSite = 'http://licensing.copyright.gov/search/SearchLegalName.jsp'
srchString = 'Indiana_Bell'
#'Michigan Bell'
#'Nevada Bell'
#'Pacific Bell'
#'Ohio Bell'
#'Wisconsin BELL'
#'ILLINOIS BELL'
#'Comcast',  'cox',
# 'csc', 'cablevision'
#'brighthouse', 'bright house',
# 'verizon', 'GTE Southwest',
# 'insight', 'Time Warner', 'Oceanic Time Warner', 'twc'
# 'at&t', 'Southern New England Telephone', 'bellsouth' 'SouthernWestern Bell' 'Southwestern Bell'
# 'Cequel Communications' (Suddenlik inheadend)
# charter, Falcon Cable Systems
# The site we will navigate into, handling it's session
companyNames = ['bresnan'
#'MediaCom'
#'Indiana_Bell'
#'Michigan_Bell'
#'Nevada_Bell'
#'Pacific_Bell'
#'Ohio_BELL'
#'Wisconsin_BELL'
#'ILLINOIS_BELL'
#'Comcast',
#'cox',
#'csc',
#'cablevision'
#'brighthouse', 'bright house',
# 'verizon',
#'GTE Southwest',
#'insight', 'Time Warner', 'Oceanic Time Warner', 'twc',
#'at&t', 'Southern New England Telephone', 'bellsouth', #'SouthernWestern Bell' 'Southwestern Bell'
#'Cequel Communications', #(Suddenlik inheadend)
#'charter', 'Falcon Cable Systems'
]

for srchString in companyNames:
    br.open(mainSite)

# Select the first (index zero) form
    br.select_form(nr=0)

# Set the for parameter to srchString
    br.form['selectedLegalName'] = srchString

# Submit the form to go to
# http://licensing.copyright.gov/search/DisplayLegalName.jsp
    br.submit()

# Read the HTML on page
# http://licensing.copyright.gov/search/DisplayLegalName.jsp
    html = br.response().read()
    soup = BeautifulSoup(html)
    print (soup)

# Form with name 'form1' has a select list of options (Company names) to choose
    forms = mechanize.ParseResponse(br.response(), backwards_compat=False)

#forms = mechanize.ParseString(html, 'form1')
    form = forms[0]

#print form
#very useful!

# The select control element
    control = form.controls[0]

    legalNameOpts = [item.attrs['value'] for item in control.items]

#print legalNameOpts
#destPath = 'c:\\users\\anilm\\'
    destPath = 'C:\\Users\\amanchanda\\Downloads\\Research\\082014\\Video3\\' + srchString + '\\'
    legalNameFile = destPath + srchString + '_LegalNames.txt'
    file = open(legalNameFile,'w');

#file.writelines( "Search Legal Names: %s\n" % srchString )
#file.writelines("****************************************************************************************************\n")
    file.writelines( "%s\n" % item for item in legalNameOpts )
    file.close()

# Now parse thru each Legal Name and and jump to page
# http://licensing.copyright.gov/search/SelectCommunity.jsp
# to select community information
# data on this page ha a select with options
# ID#       1st Community Served       State

    communityFilename = destPath + srchString + '_Communities' + '.txt'
    fileCommunity = open(communityFilename,'w');
#fileCommunity = csv.writer(open(communityFilename,"w"), delimiter='|',quoting=csv.QUOTE_NONE)
# This file will be CSV with each row of data as
# LegalName ID#       1st Community Served       State

#dataFilename = destPath + srchString + '_FilingData' + '.txt'
#fileData = open(dataFilename,'w');

    assocCommunityFilename = destPath + srchString + '_AssocCommunities' + '.txt'
    fileAssocCommunity = open(assocCommunityFilename,'w');
    fileAssocCommunity.writelines("Name|LegalName|PrimaryID|Primary Community|State|FirstCommunityServedFlag|Assoc Community\n")
# This file will be CSV with each row of data as
# LegalName ID#       1st Community Served       State
# Filing   SA     Receipt  Gross     Royalty            1st Set  1st Set  Corre-     File       Legal
# Period   Form   Date     Receipts  Payment  Interest  Subscr   Rate     spondence? Available  Name

    i = 1
# Write the header
#fileCommunity.writerow("LegalName ID#       1st Community Served       State")
    fileCommunity.writelines("LegalName|ID#|1st Community Served|State|\n")

# Write data rows
    for legalName in legalNameOpts:
#    print control
        retrieveData(br, legalName)
        response = br.back(1)
        html = response.read()
#    i = i + 1
#    if (i == 4):
#        break ;

    fileAssocCommunity.close()
    fileCommunity.close()
# Filing   SA     Receipt  Gross     Royalty            1st Set  1st Set  Corre-     File       Legal
# Period   Form   Date     Receipts  Payment  Interest  Subscr   Rate     spondence? Available  Name
#fileData.close()


