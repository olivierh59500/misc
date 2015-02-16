## Acer C720 Chromebook - Fedora 21 Post-Install Script

For those who seek to install Fedora 21 on a Acer C720 Chromebook, you may have noticed that documentation on the configurations required for such an installation exists on only very few sites and is sparse. Well, from searching the web for adequate documentation, I've successfully gathered the necessary information to ensure the Acer C720 Chromebook operates normally upon the install of Fedora 21. For your convenience, I developed a Python script to automatically configure your system appropriately.

However, just in case you are wondering, suspending functionality is covered here, as well. Once you complete the instructions below, WiFi and audio output should work upon a suspended state.

To begin the automatic configuration of your system:

- **From within a shell, login as root:**
```
/usr/bin/su -l
```

- **Create a backup of `/etc/default/grub`:**
```
cp /etc/default/grub /etc/default/grub.bak
```

- **Clone this repository with git and navigate over to this particular subdirectory or download only said subdirectory with subversion:**
```
yum install git -y
git clone https://github.com/misterpeguero/misc.git
cd misc/script/provisioning/misc/acerC720_postInstall-fedora21/
```
```
yum install subversion -y
svn checkout https://github.com/misterpeguero/misc/trunk/script/provisioning/misc/acerC720_postInstall-fedora21
cd acerC720_postInstall-fedora21/
```

- **Mark `setup.py` as an executable file:**
```
chmod +x setup.py
```

- **Execute `setup.py`:**
```
./setup.py
```

- **You should expect this very output from `setup.py`:**
```
OK: Copied "cros-acpi-wakeup.conf" to "/etc/tmpfiles.d".
OK: Copied "disable-touchpad-wakeup.conf" to "/etc/tmpfiles.d".
OK: Copied "50-cros-touchpad.conf" to "/etc/X11/xorg.conf.d".
OK: Copied "cros-sound-suspend.sh" to "/usr/lib/systemd/system-sleep".
OK: Appended "tpm_tis.force" to "/etc/default/grub" with a value of 1.
OK: Appended "tpm_tis.interrupts" to "/etc/default/grub" with a value of 0.
WARN: Inspect "/etc/default/grub" before invoking "grub2-mkconfig -o /boot/grub2/grub.cfg" to generate a grub2 
configuration file.

Process completed. Reboot for modifications to take into effect.
```

- **Update your grub2 configuration:**
```
grub2-mkconfig -o /boot/grub2/grub.cfg
```

- **Then, reboot:**
```
systemctl reboot
```

- **And that's it!**

If you encounter any potential issues with this particular subdirectory, please do not hesitate to report an issue under this repository. In the meantime, I will be developing an automatic way to create a backup of `/etc/default/grub` and update your grub2 configuration, in order to render a couple of the steps mentioned above as unnecessary.
