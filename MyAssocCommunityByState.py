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
dataFile.writelines("State|Community|Id|Filing Period|SA|Receipt Date|Gross Receipts|Filing Fee|Royalty Payment|Interest|1st Set Subscr|1st Set Rate|Correspondence?|File Available?|Legal Name\n")
##inFilename = destPath + "CommunityLists\\" + srchState + '_CommIn' + '.txt'
##infile = open(inFilename,'r');
##srchCommunities = infile.readlines()


#WY. comcast
#'CODY', 'RAWLINS', 'POWELL', 'THERMOPOLIS', 'GREYBULL', 'BUFFALO', 'NEWCASTLE', 'RIVERTON', 'SHERIDAN'
#MT
#'GLASGOW','BUTTE','LIVINGSTON','LEWISTOWN','ANACONDA',
#,'SUPERIOR', 'THOMPSON FALLS', 'CASCADE','DILLON', 'DEER LODGE', 'WOLF POINT', 'HAMILTON', 'HAVRE', 'CHINOOK', 'CHOTEAU', 'MALTA'
#,'HARLEM', 'TOWNSEND','CONRAD','FT BENTON', 'BUTTE',
#GA
##'WASHINGTON','MONTEZUMA','GLENNVILLE'
#WA
#'RAYMOND'
#IN
#'AVILLA'
#CO
#'MEEKER','RANGELY','WALSENBURG','PAONIA','ALAMOSA','LEADVILLE','SALIDA','CRAIG','STERLING','FT MORGAN','LA JUNTA'
#UT
#'DELTA','CEDAR CITY'
#TX, Cequel
##'QUANAH','CANADIAN','ANDREWS','JUNCTION','NOCONA','WELLINGTON','PITTSBURG','MT VERNON','DIMMITT', 'PADUCAH','LAMPASAS'
##,'GATESVILLE','HAWKINS','INGRAM','ELECTRA','HENRIETTA','CALDWELL','LOST PINES','DAINGERFIELD','LOWRY CROSSING'
##,'RUSK','JARRELL','CLARENDON','SHAMROCK','PARIS','ONALASKA','SNYDER','GAINESVILLE','TRINITY','CLARKSVILLE','GRAPELAND'
##,'WHITESBORO','MT PLEASANT','CENTER','KERMIT','MONAHANS','ROCKDALE','HAMLIN','ANSON','SWEETWATER','ROTAN','PRAIRIE VIEW'
##,'SEYMOUR','BURKBURNETT','ALBANY','EASTLAND','VERNON','OLNEY','BRECKENRIDGE','SONORA','BRADY','ATHENS','WINNSBORO','MINEOLA'
##,'HEARNE','BIG LAKE','BRENHAM','CRANE','MINERAL WELLS','PECOS','JACKSONVILLE','HENDERSON','SULPHUR SPRINGS','NACOGDOCHES'
##,'NACOGDOCHES','BIG SPRING','PLAINVIEW','KRUM','SAN BABA','LUCAS','ROCKDALE'
#AR
##'HEBER SPRINGS','EL DORADO','ATKINS','DOVER','MT IDA','HAZEN','BATESVILLE','BOONEVILLE','CLARKSVILLE','RUSSELLVILLE','OZARK'
##,'HOXIE','GURDON','MARVELL','HUGHES','CHARLESTON','WALDRON','NASHVILLE','MORRILTON','MALVERN','ARKADELPHIA','POCAHONTAS','MAGNOLIA'
##,'NEWPORT','STUTTGART','JONESBORO','DEWITT','HELENA'
#OK
##'HUGO','WOODWARD','IDABEL','STILLWATER','PURCELL','OKMULGEE','SEMINOLE','HEALDTON','ANADARKO','HEAVENER','SPIRO','FAIRVIEW','PAULS VALLEY'
##,'WEWOKA','ALVA','FT SILL','SALLISAW','GRANITE','HENRYETTA','WEATHERFORD','POTEAU','CUSHING','FT SUPPLY WILLIAM','ATOKA','HELENA'
##,'HODGEN','STRINGTOWN','MCALESTER','MUSKOGEE','CHICKASHA','PERRY','LINDSAY'
#MO
##'TRENTON','BROOKFIELD','NEOSHO','NIXA','COLE COUNTY','LEXINGTON','CARTHAGE','MARYVILLE','BOONVILLE','BRANSON','MONETT'
##,'TIPTON','SAINT JOSEPH','LAMAR'
#AZ
##'PARKER','GOLDEN VALLEY','ELOY','LAKE HAVASU','PANE','ELOY'
#KS
##'PAOLA','ANTHONY','FT SCOTT','LANSING'

#KY
##'RUSSELLVILLE', 'PIKEVILLE','GRAYSON','LAGRANGE','DANVILLE','EDDYVILLE','ADAIRVILLE','SAINT MARY','PEEWEE'
#NC
##'WASHINGTON','MARTIN','KINSTON'
#LA
##'WINNFIELD','VILLE PLATTE','MOREAUVILLE','BOYCE','JONESBORO','MANY','MINDEN','LEESVILLE','ST JOSEPH','DERIDDER','IOWA','KILLONA'
##,'JENA','BASTROP','NATCHITOCHES','LECOMPTE','SIBLEY'
#CA
##'BLYTHE','HUMBOLDT','SHAVER LAKE ','FORESTHILL','FORRESTHILL','BISHOP','MAMMOTH LAKES'
#VA
##'BUCHANAN','CLARKSVILLE','LAWRENCEVILLE','FARMVILLE','IBERIA','OAKWOOD','STATE FARM','MITCHELL','WAVERLY','BASKERVILLE','CAPRON'
##,'BLAND','JARRETT','GREENVILLE','ALBERTA'
#IN
##'ODON','LAWRENCE','BUNKER HILL','CARLISLE','WEST'
#IL
##'ARGENTA','VIENNA','SUMNER','CAVE-IN-ROCK','SHERIDAN'
#OH
##'SENECAVILLE','KNOX','CAMBRIDGE'
#WV
##'KERMIT','BEVERLY'
#ID
##'SPIRIT LAKE','OROFINO','ST MARIES','OSBURN','KUNA'
#CO
##'LIMON','DELTA','STERLING','OLNEY','MODEL'
#PA
##'HUNLOCK','MERCER','KARTHAUS','WAYMART','GRATERFORD','EAST MILLSBORO','COAL','ALBION','CAMBRIDGE','FRACKVILLE'
#NE
##'TECUMSEH','YORK'
#MT
##'DEER LODGE'
#NV
##'CARLIN','ELY','NORTH LAS VEGAS','INDIAN SPRINGS','WINNEMUCCA','JEAN JEAN','LOVELOCK','TONOPAH','PIOCHE','TONOPAH'
##,'WELLS WELLS'
#WI
##'BLACK RIVER','LAKE TOMAHAWK','GORDON'
#NM
#'SANTA ROSA'
#MS
##'GREENWOOD'
#MD
##'WESTOVER','BOYD'
#NY
##'VALHALLA'
#TXcox,
##'ANDREWS','PITTSBURG','JARRELL'
#CA
##'SUN CITY','SANTA BARBARA','SAN JUAN','BONITA','RANCHO'
#AZ
##'GILA BEND'
#AR
##'BERRYVILLE','HARRISON'
#NC
##'WASHINGTON'
srchCommunities = [
#TX
##'GEORGE WEST','SEADRIFT','COLUMBUS','GONZALES','EAGLE PASS', 'DILLEY','CRYSTAL CITY','DEL RIO','UVALDE'
#LA
##'WINNFIELD', 'JONESBORO','MINDEN','DERIDDER','BASTROP','NATCHITOCHES'
##,'VILLE PLATTE','MOREAUVILLE','BOYCE','MANY','LEESVILLE','ST JOSEPH','IOWA','KILLONA'
##,'JENA','LECOMPTE','SIBLEY'
#OH
##'VERSAILLES','CALDWELL','SCIO','LEESVILLE','HOPEDALE','JEWETT','PAULDING','COMMERCIAL POINT','ATHENS','ALBANY','NEW HOLLAND','BAINBRIDGE'
##,'ASHLEY CORNER','SCPIO','MIDWAY','BOWERSTON'
#OK
##'LINDSAY','CHICKASHA','PAULS VALLEY','FT SUPPLY','DRUMRIGHT'
#CA
##'BAKERSFIELD','PALM SPRINGS','AVENAL','BANNING','BARSTOW','EL CENTRO','BLAISDELL','PACIFIC BEACH','SAN DIEGO','SHABER LAKE'
#NV
##'JEAN','WELLS'
#AL
##'CLIO','EUFAULA','GREENVILLE','FT PAYNE'
#WV
##'KERMIT','BEVERLY'
#NY
##'MOUNT VERNON','STATEN ISLAND','MANHATTAN','PORT CHESTER', 'RIVERHEAD','BEDFORD'
#IA
##'STORM LAKE','MASON CITY','KEOKUK','WAVERLY','CHARITON','NEWTON','RED OAK','NORTH LIBERTY','APLINGTON','MARSHALLTOWN'
#KS
##'GREAT BEND','SALINA','GARDEN CITY','PITTSBURG','DODGE CITY','CHANUTE','EMPORIA','INDEPENDENCE'
#FL
##'CEDAR KEY','BLOUNTSTOWN','DE FUNIAK','CHATTAHOOCHEE'
#MO
##'LAMAR','MONETT','BRANSON','CARTHAGE'
#CO
##'MEEKER','CRESTED BUTTE','TELLURIDE'
#IN
#'MARION','GRANT COUNTY','MADISON'
#WI
##'MARINETTE','HAWKINS'
#HI
##'WAILUKU','OAHU','KAUAI','KEALAKEKUA'
#KY
##'VANCEBURG','CLAY','BULAN','LEBANON'
#VA
##'NEWCASTLE','FLOYD TOWN'
#ME
##'CARIBOU','PRESQUE ISLE'
#TN
##'BROWNSVILLE','BOLIVAR'
#MT
##'TROY','LIBBY'
#IL
##'CARTHAGE'
#ID
##'SUN VALLEY'
#GA
##'MACON'
#NH
##'BERLIN'

#WA
##'PULLMAN'
#AZ
##'PINE'
#NE
##'TRENTON'

#MS
##'CLEVELAND'
#GA
#'WASHINGTON','MONTEZUMA','GLENNVILLE'

#ID
'DAWSON','PROVIDENCE'
]

next1 = [

#CO
'MEEKER','RANGELY','DURANGO','Buena Vista','WALSENBURG','PAONIA','SILT','ALAMOSA','LEADVILLE','SALIDA','DURANGO','MONTROSE','FT MORGAN','CRAIG','CANON','STERLING'
'GRAND','LA JUNTA'
#ID,
'PRESTON','FISH HAVEN'
#IL
'BENTON'
#IN
'AVILLA','FLORA','COVINGTON','MONTPELIER','MORGAN','MONROEVILLE'
#MT
'ANACONDA','BILLINGS', 'BOULDER','BOZEMAN','BUTTE','CASCADE','CHINOOK','CHOTEAU', 'CONRAD','CUT BANK','DILLON','DEER LODGE', 'FT BENTON', 'GLASGOW'
,'GREAT FALLS','HAMILTON', 'HARLEM','HAVRE','HELENA','KALISPELL', 'LEWISTOWN','LIVINGSTON','MISSOULA','MALTA'
,'SHELBY', 'POLSON', 'STEVENSVILLE',  'SUPERIOR'
,'THOMPSON','WOLF','TOWNSEND'
#TX
'HARRIS', 'GARLAND'
#UT
'CEDAR CITY','DELTA','NEPHI'
#WA
'RAYMOND'
#WY
'BUFFALO','CASPER','CHEYENNE','CODY','GILLETTE','GREYBULL','JACKSON','LARAMIE','NEWCASTLE','POWELL','RAWLINS','RIVERTON','SHERIDAN''THERMOPOLIS','WORLAND'


]
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
dataFile.close()
#infile.close()


