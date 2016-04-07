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
from datetime import date,timedelta

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

sys.stdout.write("Starting queries ...\n")

message = ''
total_matches = 0

output_html = BeautifulSoup('<html><body></body></html>','html.parser') 

for query in args.queries:
	sys.stdout.write("Querying \"" + query + "\" ... ")

	br.open(url)
	br.select_form(name='pesquisaAvancada')

	#print br.form

	br['edicao.txtPesquisa']=query
	br['edicao.dtInicio']=args.inidate
	br['edicao.dtFim']=args.enddate
	br.find_control("edicao.jornal").items[0].selected=True
	response1 = br.submit()

	html = BeautifulSoup(response1.get_data(),'html.parser')
	print html.original_encoding
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
			
	if debug:
		print message

#print output_html.prettify()

if not debug:
	login = raw_input("Enter your gmail login: ")
	password = raw_input("Enter your password: ")

	sys.stdout.write("Sending email ... ")

	msg = MIMEText(str(output_html),'html')

	# me == the sender's email address
	# you == the recipient's email address
	me = login
	you = ', '.join(args.email)

	print you

	msg['Subject'] = "DOUbot: encontradas " + str(total_matches) + "ocorrencias"
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
		

