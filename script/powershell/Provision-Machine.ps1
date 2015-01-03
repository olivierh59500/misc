<#
	.NOTES
	Provision-Machine Script
	Last Modification: 2015-01-03
	Author: Steven Peguero
	
	.SYNOPSIS
	Provisions a machine by installing applicable drivers and binding it to a domain.

	.PARAMETER DomainName
	A specific domain to bind to.
	
	.PARAMETER DomainAdmin
	The specific username of a domain administrator with the permission to bind machines to a specified domain. You will be prompted for a password during the execution of this script.
	
	.PARAMETER DomainAdminPassword
	The specific password of a domain administrator with the permission to bind machines to a specified domain. This will allow for automatic domain binding, but this particular method is unsecure and is NOT recommended, as it will leave a specified password exposed as plain text prior to invocation.
	
	.PARAMETER DriverDirectory
	A root directory that contains a hierarchy of directories specific to machine model, operating system build, and operating system architecture containing driver software.
	
	.PARAMETER SecondsToDisplayBindingStatus
	A number of seconds to pause the script upon domain binding, before it is automatically terminated. The default value is 15.
	
	.EXAMPLE
	.\Provision-Machine.ps1 -DomainName "domain.com" -DomainAdmin "DOMAIN\username" -DriverDirectory "C:\Drivers" -SecondsToDisplayBindingStatus 10
#>

[CmdletBinding()]

Param (
	[Parameter(Mandatory=$True)]
	[alias("n")]
	[String]
	$DomainName,
	
	[Parameter(Mandatory=$True)]
	[alias("u")]
	[String]
	$DomainAdminUserName,
	
	[Parameter(Mandatory=$False)]
	[alias("p")]
	[String]
	$DomainAdminPassword,
	
	[Parameter(Mandatory=$False)]
	[alias("d")]
	[String]
	$DriverDirectory,
	
	[Parameter(Mandatory=$False)]
	[alias("s")]
	[Int64]
	$SecondsToDisplayBindingStatus = 15
)

Begin {
	
	# ---- VARIABLES ----
	
	$Log_FileName = "provisioning_" + $DomainName + "_" + (Get-Date -Format "yyyy-MM-dd_HH-mm-ss") + ".log"
	$Log_FilePath = $env:Temp + "\" + $Log_FileName

	# ---- FUNCTIONS ----
	
	function AddRegistryKey ([String]$DirectoryPath, [String]$KeyName, $KeyValue, [Switch]$CreateSubdirectory) {

		# Provides easy manipulation of registry.

		if ($DirectoryPath -gt 0 -and $KeyName -gt 0 -and $KeyValue -ne $Null) {
			try {
				if ($CreateSubdirectory) {
					New-Item -Path $DirectoryPath -ItemType Directory -Force > $Null
				}

				New-ItemProperty -Path $DirectoryPath -Name $KeyName -Value $KeyValue -Force > $Null
				return "Successfully manipulated registry."
			}

			catch {
				Write-Host -ForegroundColor Red "ERROR: Could not manipulate registry due to specific error. Details:" + $Error[0]
			}
		}

		else {
			Write-Host -ForegroundColor Red "ERROR: Could not manipulate registry due to insufficient parameter input."
		}
	}

	function ReportStatus ([String]$Type, [String]$Message, [Switch]$NoWhitespace) {

		switch ($Type) {
			Step {
				$Output = @{
					"Object" = $Message + "..."
					"BackgroundColor" = "Yellow"
					"ForegroundColor" = "Black"
				}
			}
			
			Error {
				$Output = @{
					"Object" = "ERROR: " + $Message
					"BackgroundColor" = "Black"
					"ForegroundColor" = "Red"
				}
			}

			Default {
				$Output = @{
					"Object" = $Message
					"BackgroundColor" = $Host.UI.RawUi.BackgroundColor
					"ForegroundColor" = $Host.UI.RawUi.ForegroundColor
				}
			}
		}
		
		if ($Host.Name -eq "Windows PowerShell ISE Host") {
			$output.Remove("BackgroundColor")
			$output.Remove("ForegroundColor")
		}

		if (!($NoWhitespace)) {
			$Output.Set_Item("Object", "`n" + ($Output['Object']) + "`n") # Leaves whitespace before and after output.
		}
		
		Write-Host @Output
	}
	
	function GenerateSpecificDriverSubdirectories ([String]$RootDirectory) {
	
		try {
			$CurrentMachine_ModelNumber = @(Get-WmiObject -Class Win32_ComputerSystem)[0].Model -Replace ' ',''
			$CurrentMachine_OSVersion = (Get-WmiObject -Class Win32_OperatingSystem).Version
			$CurrentMachine_OSArchitecture = (Get-WmiObject -Class Win32_OperatingSystem).OSArchitecture
			
			$FullPath = $RootDirectory + "\"
			$FullPath += $CurrentMachine_ModelNumber + "\"
			$FullPath += $CurrentMachine_OSVersion + "\"
			$FullPath += $CurrentMachine_OSArchitecture
			
			$GeneratedDriverSubdirectories = @{
				"RootDirectory" = $RootDirectory
				"ModelNumber" = $CurrentMachine_ModelNumber
				"OSVersion" = $CurrentMachine_OSVersion
				"OSArchitecture" = $CurrentMachine_OSArchitecture
				"FullPath" = $FullPath
			}
			
			return $GeneratedDriverSubdirectories
		}
		
		catch [Exception] {
			Write-Host -ForegroundColor Red "ERROR: An error occurred when generating driver subdirectories. Details: " + $Error[0]
		}
	}
	
	# ---- PASSWORD ENCRYPTION ----
	
	if ($DomainAdminPassword -match "^$") {
		$DomainAdminCredentials = $DomainAdminUserName
	}
	
	else {
		$DomainAdminEncryptedPassword = (ConvertTo-SecureString -String $DomainAdminPassword -AsPlainText -Force)
		$DomainAdminCredentials = (New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $DomainAdminUserName, $DomainAdminEncryptedPassword)
	}
}

Process {

	# ---- START OF DIAGNOSTIC LOGGING ----

	ReportStatus -Type Step -Message "Initializing Diagnostic Logging"

	try {
		Start-Transcript -Path $Log_FilePath -Force
	}

	catch [Exception] {
		ReportStatus -NoWhiteSpace -Type Error -Message ("Could not begin writing log of buffer to '" + $Log_FilePath + "'. Details: " + $Error[0])
	}

	# ---- START OF RDP SERVICE ----

	ReportStatus -Type Step -Message "Enabling RDP Server"
	
	AddRegistryKey `
	-DirectoryPath "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server" `
	-KeyName "fDenyTSConnections" `
	-KeyValue 0

	# ---- DRIVER INSTALLATIONS ----

	if ($DriverDirectory) {
		ReportStatus -Type Step -Message "Disabling Driver Verification"
		
		AddRegistryKey `
		-DirectoryPath "HKCU:\Software\Policies\Microsoft\Windows NT\Driver Signing" `
		-KeyName "BehaviorOnFailedVerify" `
		-KeyValue 0 `
		-CreateSubdirectory

		ReportStatus -Type Step -Message "Installing Drivers"
		
		try {
			$MachineSpecificDriverSubdirectories = (GenerateSpecificDriverSubdirectories -RootDirectory $DriverDirectory)
			
			if (!(Test-Path $MachineSpecificDriverSubdirectories.FullPath)) {
				ReportStatus -NoWhitespace -Type Error -Message ( `
					"Could not locate the generated driver directory path, '" `
					+ $MachineSpecificDriverSubdirectories.FullPath `
					+ "', on the local filesystem." `
				)
			}

			else {
				ReportStatus -NoWhitespace -Message ( `
					"Installing applicable drivers from " `
					+ $MachineSpecificDriverSubdirectories.FullPath `
					+ ":"
				)
				
				AddRegistryKey `
				-DirectoryPath "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\UnattendSettings\PnPUnattend\DriverPaths\1" `
				-KeyName "Path" `
				-KeyValue $MachineSpecificDriverSubdirectories.FullPath `
				-CreateSubdirectory `
				| Out-Null
				
				& "$($env:SystemRoot)\System32\PnpUnattend.exe" AuditSystem /L 2>&1 | Out-Default
			}
		}

		catch [Exception] {
			ReportStatus -Type Error -Message ( `
				"Could not successfully perform the process of installing drivers onto this specific machine (" `
				+ $MachineSpecificDriverSubdirectories.ModelNumber `
				+ "). Details: " `
				+ $Error[0] `
			)
		}
	}

	else {
		ReportStatus -Type Step -Message "Skipping Installation of Drivers"
	}

	# ---- DOMAIN BINDING ----

	ReportStatus -Type Step -Message "Binding Machine to Domain"

	try {
		if (Test-Connection $DomainName -Quiet -Count 1) {
			if ($env:UserDNSDomain -eq $Null) {
				Add-Computer -DomainName $DomainName -Credential $DomainAdminCredentials
			}
			
			else {
				throw "Machine is already bound to a domain (" + $env:UserDNSDomain.ToLower() + ")."
			}
		}

		else {
			throw "Unable to resolve. Ensure an appropriate network driver has been installed and static network information has not been configured. This script will continue."
		}
	}

	catch [Exception] {
		ReportStatus -NoWhitespace -Type Error -Message ("Could not bind machine to '" + $DomainName + "'. Details: " + $Error[0])
	}

	# ---- END OF DIAGNOSTIC LOGGING ----

	try {
		Stop-Transcript | Out-Null
	}

	catch [Exception] {}

	finally {
		ReportStatus -Message ("Terminating script in " + $SecondsToDisplayBindingStatus + " seconds...")
		Start-Sleep -Seconds $SecondsToDisplayBindingStatus
	}
}
