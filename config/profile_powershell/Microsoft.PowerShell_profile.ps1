
$ErrorActionPreference = "Stop"

function Initiate-Session {

	$SessionDirectoryPath = $PSScriptRoot
#	$ConfigDirectoryPath  = $SessionDirectoryPath + "\config" <-- Remaining for future implementation.
	$ModuleDirectoryPath  = $SessionDirectoryPath + "\module"

	# ---- FUNCTIONS ----

	function ReportStatus {

		Param (
			[String]
			$Message,

			[String]
			$Type
		)

		if ($Type -eq "Okay") {
			Write-Host -NoNewLine -ForegroundColor Black -BackgroundColor Green -Object " + "
		}

		if ($Type -eq "Fail") {
			Write-Host -NoNewLine -ForegroundColor White -BackgroundColor Red -Object " - "
		}

		Write-Output $Message
	}

	# ---- SHELL CONFIGURATION ----

	$Host.UI.RawUI.BackgroundColor = "Black"
	$Host.UI.RawUI.ForegroundColor = "Green"

	Clear-Host

	function Global:Prompt {

		[ArrayList]$Prompt = [Ordered]@{
			"`nPS "                                                   = "Cyan"
			"["                                                       = "White"
			($env:UserName + '@' + $env:ComputerName.ToLower() + " ") = "Cyan"
			(Get-Location).ProviderPath                               = "Red"
			"]"                                                       = "White"
		}

		Write-Output "`n> "

		foreach ($Item in $Prompt.Keys) {
			Write-Host -NoNewLine -ForegroundColor $Prompt[$Item] -Object $Item
			[String]$HostTitleBar += $Item
		}

		$Host.UI.RawUI.WindowTitle = $HostTitleBar
	}

	# ---- MODULE IMPORTATION ----

	Write-Host -Object "" # Leaves space between name of first imported module and title bar.

	if (!(Test-Path -Path $ModuleDirectoryPath)) {
		try {
			New-Item -Name "module" -Path $SessionDirectoryPath -ItemType Directory -Force | Out-Null
			ReportStatus -Type "Okay" -Message (" Created module directory at '" + $ModuleDirectoryPath + "'.")
		}

		catch {
			ReportStatus -Type "Fail" -Message (" An error occurred when attempting to create module directory at '" + $ModuleDirectoryPath + "' :`n`n" + $_.Exception.Message)
		}
	}

	else {
		Get-Module | ? {$_.ModuleBase -like "$SessionDirectoryPath*" -and $_.Name -ne $Session_ProfileName} | Remove-Module
		$ModuleList = (Get-ChildItem -Path $ModuleDirectoryPath -Filter "*.psm1" -Recurse)

		if ($ModuleList) {
			foreach ($Module in $ModuleList) {
				try {
					Import-Module -Name $Module.FullName -DisableNameChecking -Force
					ReportStatus -Type "Okay" -Message (" " + $Module.BaseName)
				}

				catch {
					ReportStatus -Type "Fail" -Message (" " + $Module.BaseName + " :`n`n" + $_.Exception.Message + "`n")
				}
			}
		}

		else {
			ReportStatus -Type "Fail" -Message (" No modules available for importation.")
		}
	}
}

Initiate-Session
