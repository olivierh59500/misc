function Repeat-Command {

	<#
		.SYNOPSIS
		A PowerShell variant of the 'watch' Unix command, used for continuously invoking commands every specified amount of seconds.

		.EXAMPLE
		Repeat-Command 'ls'
		Invokes the specified command, ls, every second.

		.EXAMPLE
		Repeat-Command 'ls' 2
		Invokes the specified command, ls, every two seconds.

		.EXAMPLE
		Repeat-Command 'ls' 2 -WithoutClearingBuffer
		Repeat-Command 'ls' 2 -w
		Invokes the specified command, ls, every two seconds, without clearing a console's buffer.

		.EXAMPLE
		Repeat-Command 'ls' 2 -TerminateIfError
		Repeat-Command 'ls' 2 -t
		Invokes the specified command, ls, every two seconds, but is prone to automatic termination, if said command throws an exception. Only supports PowerShell cmdlets.
	#>

	[CmdletBinding()]

	Param (
		[Parameter(Mandatory=$True)]
		[String]
		$Command,

		[Parameter(Mandatory=$False)]
		[Int64]
		$Seconds = 1,

		[Parameter(Mandatory=$False)]
		[Alias("w")]
		[Switch]
		$WithoutClearingBuffer,

		[Parameter(Mandatory=$False)]
		[Alias("t")]
		[Switch]
		$TerminateIfError
	)

	Begin {
		$HeadsUpDisplay_Text       = "Repeat-Command: '" + $Command + "' every " + $Seconds + " second(s)"
		$HeadsUpDisplay_Separator  = "-" * $HeadsUpDisplay_Text.Length + "`n"
		$HeadsUpDisplay            = @($HeadsUpDisplay_Text, $HeadsUpDisplay_Separator)

		$Host.UI.RawUI.WindowTitle = $Host.UI.RawUI.WindowTitle + " (Repeat-Command)"
	}

	Process {
		do {
			if ($WithoutClearingBuffer -eq $False) {
				Clear-Host
				Write-Output $HeadsUpDisplay
			}

			try {
				Invoke-Expression $Command | Out-Default
			}

			catch [Exception] {
				Write-Host -ForegroundColor Red ("ERROR: " + $_.Exception.Message)

				if ($TerminateIfError -eq $True) {
					break
				}
			}

			Start-Sleep -Seconds $Seconds
		}

		until (
			$Null
		)
	}
}
