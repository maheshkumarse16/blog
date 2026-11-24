<#
    Author      : Mahesh Kumar S.E
    Version     : 1.0
    Description : Single-file version. Checks whether hotpatch KB5132043 is present and
                  uninstalls it. Works as an Intune Platform script (run as SYSTEM, 64-bit)
                  or a manual run in an elevated PowerShell.
                  No restart is forced. No LCU install or scan is triggered.
                  Exit 0 = nothing to do, or removed (restart pending). Exit 1 = uninstall failed.
    Website     : https://maheshkumarse.com
#>

$ErrorActionPreference = 'Continue'
$kb = 'KB5132043'

$cv    = Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion'
$build = $cv.CurrentBuildNumber
$ubr   = [int]$cv.UBR
$pendingReboot = Test-Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired'

# 1. Is the hotpatch present?
$hotfix  = Get-HotFix -Id $kb -ErrorAction SilentlyContinue
$present = ($ubr -eq 9911) -or [bool]$hotfix

if (-not $present) {
    Write-Output "$env:COMPUTERNAME : $kb not present (build $build.$ubr). Nothing to do."
    exit 0
}

if ($pendingReboot) {
    Write-Output "$env:COMPUTERNAME : $kb present but a restart is already pending (build $build.$ubr). Skipping."
    exit 0
}

# 2. Uninstall (no restart)
Write-Output "$env:COMPUTERNAME : $kb present (build $build.$ubr). Uninstalling..."
$p = Start-Process -FilePath wusa.exe `
        -ArgumentList '/uninstall', "/kb:$($kb.Substring(2))", '/quiet', '/norestart' `
        -Wait -PassThru

Write-Output "wusa exit code: $($p.ExitCode)"   # 0 = removed, 3010 = removed, restart needed

if ($p.ExitCode -in 0, 3010) {
    Write-Output "$env:COMPUTERNAME : $kb uninstalled. Restart required to complete."
    exit 0
}

Write-Output "$env:COMPUTERNAME : uninstall failed. Fallback: dism /online /get-packages, then dism /online /remove-package /packagename:<name>"
exit 1
