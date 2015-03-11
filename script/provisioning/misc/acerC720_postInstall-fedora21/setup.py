#!/usr/bin/python3

def main():
	import fileinput
	import os
	import shutil
	import sys
	
	exitStatus        = 0
	files             = {
		'50-cros-touchpad.conf'        : '/etc/X11/xorg.conf.d',
		'cros-acpi-wakeup.conf'        : '/etc/tmpfiles.d',
		'cros-sound-suspend.sh'        : '/usr/lib/systemd/system-sleep',
		'disable-touchpad-wakeup.conf' : '/etc/tmpfiles.d'
	}
	grub_appendStatus = 1 # Changes to zero, if modifications are made to grub.
	grub_arguments    = {
		'tpm_tis.interrupts'           : 0,
		'tpm_tis.force'                : 1
	}
	grub_configFile   = '/etc/default/grub'
	grub_parameter    = 'GRUB_CMDLINE_LINUX="'
	
	# Determines if script is running under root.
	
	if os.getuid() != 0:
		exitStatus = 1
		print('FAIL: Execute this script as root.', file=sys.stderr)
		exit(exitStatus)

	# Copies configuration files and scripts to their respective directory.

	for file in files.keys():
		try:
			file_targetDirectory = files[file]
			os.chown(file, 0, 0)
			
			if '.sh' in file:
				os.chmod(file, 0o700)
			else:
				os.chmod(file, 0o600)
			
			shutil.copy(file, file_targetDirectory)
			print('OK: Copied "%s" to "%s".' % (file, file_targetDirectory))
		
		except Exception as why:
			if why.args[0] == 1:
				print('FAIL: Could not change owner of "%s" to root.' % (file), file=sys.stderr)
			else:
				print('FAIL: Could not copy "%s" to "%s": %s.' % (file, file_targetDirectory, why), file=sys.stderr)
			exitStatus = 1
			continue
			
	# Adds specific boot arguments to grub, which is required for proper suspending.
	
	try:
		for i in grub_arguments.keys():
			grub_arguments_value = grub_arguments[i]
			
			if i in open(grub_configFile).read():
				print('WARN: Did not append "%s" to "%s" with a value of %s: Already exists.' % (i, grub_configFile, grub_arguments_value))
			else:
				# Appends grub arguments.
			
				for line in fileinput.FileInput(grub_configFile, inplace = 1):
					line = line.replace(grub_parameter, '%s%s=%s ' % (grub_parameter, i, grub_arguments_value))
					sys.stdout.write(line)
				
				grub_appendStatus = 0
				print('OK: Appended "%s" to "%s" with a value of %s.' % (i, grub_configFile, grub_arguments_value))

	except Exception as why:
		exitStatus = 1
		print('FAIL: Could not append "%s" to "%s" with a value of %s: %s.' % (i, grub_configFile, grub_arguments_value, why), file=sys.stderr)

	if grub_appendStatus == 0:
		print('WARN: Inspect "%s" before invoking "grub2-mkconfig -o /boot/grub2/grub.cfg" to generate a grub2 configuration file.' % grub_configFile)

	if exitStatus == 0:
		print('\nProcess completed. Reboot for modifications to take into effect.')
	else:
		print('\nProcess completed with a non-zero exit status. Check output above for details.', file=sys.stderr)

	exit(exitStatus)

if __name__ == '__main__':
	main()
