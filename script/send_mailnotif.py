#!/usr/bin/python3

from argparse import ArgumentParser
import smtplib
import sys

parser = ArgumentParser()
parser.add_argument('-S', '--smtp-server',   required = True)
parser.add_argument('-P', '--smtp-port',     required = True)
parser.add_argument('-u', '--smtp-user',     required = True)
parser.add_argument('-p', '--smtp-password', required = True)
parser.add_argument('-s', '--subject',       required = True)
parser.add_argument('-b', '--body',          required = True)
parser.add_argument('-r', '--recipient',     required = True)
args = parser.parse_args()

mail_headers      = ''
mail_headers_list = [
	'From: '    + args.smtp_user,
	'Subject: ' + args.subject,
	'To: '      + args.recipient,
	'MIME-Version: 1.0',
	'Content-Type: text/html']

for header in mail_headers_list:
	mail_headers += header + '\n'

mail_body = mail_headers + '\r\n\r\n' + args.body

try:
	server = smtplib.SMTP(args.smtp_server, args.smtp_port)
	server.ehlo()
	server.starttls()
	server.ehlo
	server.login(args.smtp_user, args.smtp_password)
	
	server.sendmail(args.smtp_user, args.recipient, mail_body)
	server.quit()

except OSError as why:
	print('\nERROR: %s' % why, file=sys.stderr)
	exit(1)

exit(0)
