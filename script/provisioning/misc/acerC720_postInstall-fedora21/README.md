## Acer C720 Chromebook - Fedora 21 Post-Install Script

For those who seek to install Fedora 21 on a Acer C720 Chromebook, you may have noticed that documentation on the configurations required for such an installation exists on only very few sites and is sparse. Well, from searching the web for adequate documentation, I've successfully gathered the necessary information to ensure the Acer C720 Chromebook operates normally upon the install of Fedora 21. For your convenience, I developed a Python script to automatically configure your system appropriately.

However, just in case you are wondering, suspending functionality is covered here, as well. Once you complete the instructions below, WiFi and audio output should work upon a suspended state.

To begin the automatic configuration of your system:

- **Create a backup of `/etc/default/grub`:**
```
su -c "cp /etc/default/grub /etc/default/grub.bak"
```

- **Clone this repository with git and navigate over to this particular subdirectory or download only said subdirectory with subversion:**
```
git clone https://github.com/misterpeguero/misc.git
cd misc/script/provisioning/misc/acerC720_postInstall-fedora21/
```
```
svn checkout https://github.com/misterpeguero/misc/trunk/script/provisioning/misc/acerC720_postInstall-fedora21
cd acerC720_postInstall-fedora21/
```

- **Mark `setup.py` as an executable file:**
```
chmod +x setup.py
```

- **Execute `setup.py` as root:**
```
su -c ./setup.py
```

- **Inspect `/etc/default/grub` for any unusual modifications:**
```
vi /etc/default/grub
```

- **Update your grub2 configuration:**
```
grub2-mkconfig -o /boot/grub2/grub.cfg
```

- **Then reboot, and that's it!**

If you encounter any potential issues with this particular subdirectory, please do not hesitate to report an issue under this repository. In the meantime, I will be developing an automatic way to create a backup of `/etc/default/grub` and update your grub2 configuration, in order to render a couple of the steps mentioned above as unnecessary.
