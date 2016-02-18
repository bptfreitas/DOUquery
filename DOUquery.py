#!/usr/bin/python
# encoding: latin1

import mechanize
import cookielib
import re
import smtplib
import argparse
import datetime
import sys

from bs4 import BeautifulSoup
from time import time
from email.mime.text import MIMEText
from datetime import date

parser = argparse.ArgumentParser(description='Verifies if ')
parser.add_argument('--email', nargs='+', help='email to send notification if query has results',required=True, type=str)

parser.add_argument('--queries', nargs='+', help='text to search for', required=True, type=str)

parser.add_argument('--inidate', nargs='?', help='initial date for the search', default = date.today().strftime("%d/%m"), type=str)

parser.add_argument('--enddate', nargs='?', help='end date for the search', default = date.today().strftime("%d/%m"), type=str)

args = parser.parse_args()

sys.stdout.write("Email to send notification: " + str(args.email) + "\n")
sys.stdout.write("Start date to search: " + str(args.inidate) + "\n")
sys.stdout.write("End date to search: " + str(args.enddate) + "\n")

if args.enddate<args.inidate:
	sys.stderr.write("Error: initial date is greater than end date\n")
	sys.exit(-1)

url = "http://portal.imprensanacional.gov.br"

# browserowser
br = mechanize.Browser()
# Cookie Jar
# cj = cookielib.LWPCookieJar()
# browser.set_cookiejar(cj)
# browserowser options
br.set_handle_equiv(True)
#browser.set_handle_gzip(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
# User-Agent
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

sys.stdout.write("Queries:\n")	
body = ''
matches = 0
for query in args.queries:
	br.open(url)
	br.select_form(name='pesquisaAvancada')

	#print br.form

	br['edicao.txtPesquisa']=query
	br['edicao.dtInicio']=args.inidate
	br['edicao.dtFim']=args.enddate
	br.find_control("edicao.jornal").items[0].selected=True
	response1 = br.submit()

	html = BeautifulSoup(response1.get_data(),'html.parser')
	#html.prettify()

	prog = re.compile('[0-9]+')
	
	for div in html.find_all('div'):
		if 'id' in div.attrs.keys() and div['id']=='paginacao':
			s = ''.join([ x for x in div.strings])
			results = prog.search(s)
			if results!=None:
				tmp_msg = "\t\"" + query + "\": found " + str(results.group(0)) + "\n"
				body+=tmp_msg
				matches+=int(results.group(0))
			else:
				tmp_msg = "\t\"" + query + "\": found 0\n"
			
			sys.stdout.write(tmp_msg)

if matches>0:
	msg = MIMEText(body)

	# me == the sender's email address
	# you == the recipient's email address
	me = "DOUbot.net"
	you = args.email

	msg['Subject'] = "Found occurences on DOU"
	msg['From'] = me
	msg['To'] = ', '.join(args.email)

	sys.stdout.write("Found occurences... sending email\n")

	# Send the message via our own SMTP server, but don't include the
	# envelope header.
	s = smtplib.SMTP('localhost')
	s.sendmail(me, you , msg.as_string())
	s.quit()
		

