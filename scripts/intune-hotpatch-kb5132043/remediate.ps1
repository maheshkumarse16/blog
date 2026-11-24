<#
    Author      : Mahesh Kumar S.E
    Version     : 1.0
    Description : Intune Remediation - REMEDIATION. Uninstalls hotpatch KB5132043 only.
                  No restart is forced and no update scan is triggered.
                  Pilot on a few devices first.
    Website     : https://maheshkumarse.com
#>

$p = Start-Process -FilePath wusa.exe `
        -ArgumentList '/uninstall', '/kb:5132043', '/quiet', '/norestart' `
        -Wait -PassThru

Write-Output "wusa exit code: $($p.ExitCode)"   # 0 = removed, 3010 = removed, restart needed

if ($p.ExitCode -in 0, 3010) { exit 0 }

Write-Output "Uninstall failed. Try DISM: dism /online /get-packages, then /remove-package /packagename:<name>"
exit 1
