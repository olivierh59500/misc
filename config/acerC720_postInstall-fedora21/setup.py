#!/usr/bin/python3

# Ensure to run this particular script as root.

def main():
	import os
	import shutil
	import sys
	
	files = {
		'50-cros-touchpad.conf'        : '/etc/X11/xorg.conf.d',
		'cros-acpi-wakeup.conf'        : '/etc/tmpfiles.d',
		'cros-sound-suspend.sh'        : '/usr/lib/systemd/system-sleep',
		'disable-touchpad-wakeup.conf' : '/etc/tmpfiles.d'
	}
	
	grub_configFile     = "/etc/default/grub"
	grub_bootParameters = 'GRUB_CMDLINE_LINUX_DEFAULT="quiet splash tpm_tis.force=1"'

	# Copies configuration files and scripts to their respective directory.

	for file in files.keys():
		try:
			print('Processing %s...' % file)
			os.chown(file, 0, 0)
			
			if ".sh" in file:
				os.chmod(file, 0o700)
			else:
				os.chmod(file, 0o600)
			
			shutil.copy(file, files[file])
		
		except OSError as why:
			if why.args[0] == 1:
				print('ERROR: Could not change owner of "%s" to root.' % (file), file=sys.stderr)
			else:
				print('ERROR: Could not copy "%s". Details: %s.' % (file, why), file=sys.stderr)
			continue
			
	# Adds a specific boot parameter to GRUB, which is required for proper suspending.
	
	try:
		print('Adding a specific boot parameter to %s...' % grub_configFile)
		
		with open(grub_configFile, 'a') as myfile:
			myfile.write('\n%s' % grub_bootParameters)
			print('WARN: Inspect "%s" before generating a grub2 configuration file.' % grub_configFile)
	except OSError as why:
		print('ERROR: Could not edit "%s". Details: %s.' % (grub_configFile, why), file=sys.stderr)
		print('\nProcess completed with a non-zero exit status.', file=sys.stderr)
		exit(1)

	print('\nProcess complete. Reboot for modifications to take into effect.')
	exit(0)

if __name__ == '__main__':
	main()
