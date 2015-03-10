#!/usr/bin/python3

'''
Directory Replication Script

A simple script that replicates specified directories over to one centralized,
remote location, using SSH and rsync, and notifies administrators of such progress
via email.

-----------------------

The MIT License (MIT)

Copyright (c) 2015 Steven Peguero

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

def send_mail_notification(args, mail_subject, mail_message):
	import smtplib

	mail_headers      = ''
	mail_headers_list = [
		'From: '    + args.mail_smtp_user,
		'Subject: ' + mail_subject,
		'To: '      + args.mail_recipient,
		'MIME-Version: 1.0',
		'Content-Type: text/html'
	]

	for header in mail_headers_list:
		mail_headers += header + '\n'

	mail_body = mail_headers + '\r\n\r\n' + mail_message

	try:
		server = smtplib.SMTP(args.mail_smtp_server, args.mail_smtp_port)
		server.ehlo()
		server.starttls()
		server.ehlo
		server.login(args.mail_smtp_user, args.mail_smtp_password)

		server.sendmail(args.mail_smtp_user, args.mail_recipient, mail_body)
		server.quit()
		return(0)

	except OSError as why:
		return(why)

def split_source_directories(source_directories):
	try:
		result = source_directories.split(',')
		return(result)
	except OSError as why:
		raise('Splitting source directories resulted in an error. Details: %s' % why)

def main():
	from argparse import ArgumentParser
	import datetime
	import os
	import platform
	import subprocess
	import sys
	import time

	# ---- ARGUMENTS ----

	parser = ArgumentParser()
	parser.add_argument('--src-dir',            dest = 'source_directory',      required = True, type = split_source_directories)
	parser.add_argument('--dest-dir',           dest = 'destination_directory', required = True)
	parser.add_argument('--dest-hostname',      dest = 'destination_hostname',  required = True)
	parser.add_argument('--dest-ssh-user',      dest = 'destination_ssh_user',  required = True)
	parser.add_argument('--dest-ssh-port',      dest = 'destination_ssh_port',  required = True)
	parser.add_argument('--mail-smtp-server',   dest = 'mail_smtp_server',      required = True)
	parser.add_argument('--mail-smtp-port',     dest = 'mail_smtp_port',        required = True)
	parser.add_argument('--mail-smtp-user',     dest = 'mail_smtp_user',        required = True)
	parser.add_argument('--mail-smtp-password', dest = 'mail_smtp_password',    required = True)
	parser.add_argument('--mail-recipient',     dest = 'mail_recipient',        required = True)
	args = parser.parse_args()

	# ---- VARIABLES ----

	current_directory       = os.path.dirname(os.path.realpath(__file__))
	exit_code               = 0
	log_time                = time.strftime('%Y-%m-%d_%H-%M-%S')
	log_file_name           = args.destination_hostname + '_' + log_time
	mail_subject            = 'Directory Replication'
	required_subdirectories = {
		'exclude' : current_directory + '/exclude',
		'log'     : current_directory + '/log'
	}
	rsync_executable_local  = '/usr/bin/rsync'
	rsync_executable_remote = '/usr/bin/sudo /usr/bin/rsync'
	rsync_initial_arguments = '-avrtpzP'
	
	# ---- COMPATIBILITY VERIFICATION ----
	
	if platform.system() == 'Windows':
		print('ERROR: This script is not compatible with the Windows platform, but was written with Linux in mind.')
		sys.exit(1)

	if os.path.exists(rsync_executable_local) == False:
		print('ERROR: "%s" was not found on this system and is required to utilize this script.' % rsync_executable_local)
		sys.exit(1)

	# ---- SCRIPT SUBDIRECTORY VERIFICATION ----

	for subdirectory_name in required_subdirectories.keys():
	    subdirectory_path           = required_subdirectories[subdirectory_name]
	    subdirectory_path_existence = os.path.isdir(subdirectory_path)

	    if subdirectory_path_existence == True:
	        continue
	    else:
	        try:
	            os.mkdir(subdirectory_path)
	            print('\n\033[32mOK\033[0m: Created (Required Script Subdirectory) - "%s".' % subdirectory_path)
	        except OSError as why:
	            print('\n\033[31mERROR\033[0m: Required script subdirectory "%s" could not be created. Details: %s' % (subdirectory_path, why), file = sys.stderr)
	            sys.exit(1)

	# ---- SOURCE DIRECTORY BACKUP PROCESS ----

	for source_directory_path in args.source_directory:
		source_directory_name                  = source_directory_path.split('/')[-1]
		source_directory_path_with_underscores = source_directory_path.replace('/', '_')
		source_directory_path_existence        = os.path.isdir(source_directory_path)
		rsync_exclude_list                     = required_subdirectories['exclude'] + '/' + source_directory_path_with_underscores + '-' + args.destination_hostname + '.conf'
		rsync_exclude_list_existence           = os.path.exists(rsync_exclude_list)
		rsync_log_file_path                    = required_subdirectories['log'] + '/' + log_file_name + '.log'

		print('\n\033[31m\033[1m---- %s ----\033[0m\n' % source_directory_name.upper())

		# ---- SOURCE DIRECTORY VERIFICATION ----

		if source_directory_path_existence == False:
			print('\033[31mERROR\033[0m: Directory "%s" is nonexistent.' % source_directory_path, file = sys.stderr)
			exit_code = 1
			continue
		else:
			print('\033[32mOK\033[0m: Found (Directory) - "%s"' % source_directory_path)

		# ---- RSYNC EXCLUDE LIST VERIFICATION ----

		if rsync_exclude_list_existence == False:
			try:
				new_exclude_list = open(rsync_exclude_list, 'w')
				new_exclude_list.write('')
				new_exclude_list.close()
				print('\033[32mOK\033[0m: Created (Exclude List) - "%s".' % rsync_exclude_list)
			except OSError as why:
				print('\033[31mERROR\033[0m: Exclude list "%s" could not be created. Details: %s' % (rsync_exclude_list, why), file = sys.stderr)
				exit_code = 1
				continue
		else:
			print('\033[32mOK\033[0m: Found (Exclude List) - "%s"' % rsync_exclude_list)

		# ---- RSYNC INVOCATION ----

		rsync_arguments_list = (
			rsync_executable_local,
			rsync_initial_arguments,
			'--rsync-path="' + rsync_executable_remote + '"',
			'-e',
			'"ssh -p ' + args.destination_ssh_port + '"',
			'--delete',
			'--exclude-from="' + rsync_exclude_list + '"',
			'"' + source_directory_path + '"',
			args.destination_ssh_user + '@' + args.destination_hostname + ':"' + args.destination_directory + '/"',
			'--log-file="' + rsync_log_file_path + '"'
		)

		rsync_arguments_string = ''
		for argument in rsync_arguments_list:
			rsync_arguments_string += argument + ' '

		print('\n----\n')
		print('\033[33mInvoking Command: %s\033[0m\n' % rsync_arguments_string)
		rsync_output = subprocess.call(
			rsync_arguments_string,
			shell=True
		)
		print('\n----\n')
		
		if rsync_output == 0:
			print('\033[32mOK\033[0m: Invocation attempt was successful.')
		else:
			print('\033[31mERROR\033[0m: Invocation attempt resulted in a non-zero exit code (%s). Check log "%s" for details.' % (rsync_output, rsync_log_file_path), file = sys.stderr)
			exit_code = 1

	# ---- EMAIL NOTIFICATION ----
	
	if exit_code == 0:
		exit_status  = 'SUCCESS'
		mail_message = 'Process completed successfully.'
	else:
		exit_status  = 'FAIL'
		mail_message = 'Process failed. Check log for details.'

	mail_subject = mail_subject + ' [' + log_file_name  + '] (' + exit_status + ')'
	mail_notification_status = send_mail_notification(args, mail_subject, mail_message)

	if mail_notification_status == 0:
		print('\033[32mOK\033[0m: Notification attempt was successful.')
	else:
		print('\033[31mERROR\033[0m: Notification attempt failed. Details: %s' % mail_notification_status, file = sys.stderr)
		exit_code = 1

	print('\nProcess finished. (%s)\n' % exit_code)
	sys.exit(exit_code)

if __name__ == '__main__':
	main()
