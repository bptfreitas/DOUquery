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
from time import time,sleep
from email.mime.text import MIMEText
from datetime import date,timedelta
from getpass import getpass

debug = False

def compile_links(html):
	all_tds = []
	all_ths = []

	links = []
	data = []
	for th in html.find_all('th'):
		if 'class' in th.attrs.keys():
			if th['class'][0]=='data':
				#print th.contents[1]['href'].replace('../','http://pesquisa.in.gov.br/imprensa/')
				th.contents[1]['href']=th.contents[1]['href'].replace('../','http://pesquisa.in.gov.br/imprensa/')
				links.append(th.contents[1])

	for td in html.find_all('td'):
		if 'class' in td.attrs.keys():
			if td['class'][0]=='data':
				data.append( td.children )

	return zip(links,data)

today = date.today()	

parser = argparse.ArgumentParser(description='Verifies if ')
parser.add_argument('--email', nargs='+', help='email to send notification if query has results',required=True, type=str)

parser.add_argument('--queries', nargs='+', help='text to search for', required=True, type=str)

parser.add_argument('--inidate', nargs='?', help='initial date for the search', default = (date.today()-timedelta(1) ).strftime("%d/%m"), type=str)

parser.add_argument('--enddate', nargs='?', help='end date for the search', default = date.today().strftime("%d/%m"), type=str)

parser.add_argument('--periodic',action='store_true',help='repeat the query')

parser.add_argument('--period',default=60,help='sets the period for query repetition (in seconds)',type=int)

parser.add_argument('--noemail',action='store_true',help='dont send email, print results on stdout')

args = parser.parse_args()

sys.stdout.write("Email to send notification: " + str(args.email) + "\n")

if args.periodic:
	sys.stdout.write("Making periodic queries\n")
else:
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

message = ''

if not args.noemail:
	login = getpass("Enter your gmail login: ")
	password = getpass("Enter your password: ")

while True:
	total_matches = 0
	output_html = BeautifulSoup('<html><body></body></html>','html.parser') 

	sys.stdout.write("Starting queries ...\n")

	if args.periodic:
		inidate=( date.today()-timedelta(seconds=args.period) ).strftime("%d/%m")
		enddate=date.today().strftime("%d/%m")

		sys.stdout.write("Start date to search: " + str(inidate) + "\n")
		sys.stdout.write("End date to search: " + str(enddate) + "\n")
	else:
		inidate=args.inidate
		enddate=args.enddate

	for query in args.queries:		

		br.open(url)
		br.select_form(name='pesquisaAvancada')

		#print br.form

		br['edicao.txtPesquisa']=query
		br['edicao.dtInicio']=inidate
		br['edicao.dtFim']=enddate

		br.find_control("edicao.jornal").items[0].selected=True

		sys.stdout.write("Querying \"" + query + "\" ... ")
		response1 = br.submit()

		html = BeautifulSoup(response1.get_data(),'html.parser')
		#print html.original_encoding
		#html.prettify()

		prog = re.compile('[0-9]+')
	
		for div in html.find_all('div'):
			if 'id' in div.attrs.keys() and div['id']=='paginacao':
				s = ''.join([ x for x in div.strings])
				results = prog.search(s)
				if results!=None:
					links = compile_links(html)
					matches = int(results.group(0))			
				else:
					links = [ ]
					matches = 0	

				total_matches+=matches

				header = "\tEncontradas " + str(matches) + " ocorrencias para a busca \" " + query + "\"\n"

				#print output_html.prettify()

				output_html.body.append(header)
				output_html.body.append(output_html.new_tag("br"))

				#print output_html.prettify()

				for (link,desc) in links:
					output_html.body.append(link)
					output_html.body.append(output_html.new_tag("br"))
					for d in desc:
						output_html.body.append(d)
					output_html.body.append(output_html.new_tag("br"))

				sys.stdout.write( str(matches) + " matches \n"  )

	#print output_html.prettify()

	if not args.noemail:
		sys.stdout.write("Sending email ... ")

		msg = MIMEText(str(output_html),'html')

		# me == the sender's email address
		# you == the recipient's email address
		me = login
		you = ', '.join(args.email)

		msg['Subject'] = "DOUbot: encontradas " + str(total_matches) + " ocorrências"
		msg['From'] = me
		msg['To'] = ', '.join(args.email)

		# Send the message via our own SMTP server, but don't include the
		# envelope header.
		# s = smtplib.SMTP('localhost')
		s = smtplib.SMTP('smtp.gmail.com', 587)

		s.ehlo()

		s.starttls()

		s.login(login,password)
		r = s.sendmail(me, you, msg.as_string())

		s.quit()

		sys.stdout.write("done\n")
	else:
		sys.stdout.write(output_html.prettify())
		

	if not args.periodic:		
		break
	else:
		sys.stdout.write("Sleeping for " +str(args.period)+ " seconds ... \n")
		sys.stdout.flush()
		sleep(args.period)
		
		

