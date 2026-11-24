<#
    Author      : Mahesh Kumar S.E
    Version     : 1.0
    Description : Intune Remediation - DETECTION. Flags any device that has hotpatch
                  KB5132043 installed (build revision 9911).
                  Exit 1 = patch present (runs remediation)
                  Exit 0 = not present, or a restart is already pending
    Website     : https://maheshkumarse.com
#>

$cv    = Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion'
$build = $cv.CurrentBuildNumber
$ubr   = [int]$cv.UBR

$spooler = (Get-Service -Name Spooler -ErrorAction SilentlyContinue).Status
$pendingReboot = Test-Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired'

# Present if the OS revision matches the hotpatch, or Get-HotFix lists it
$hotfix = Get-HotFix -Id KB5132043 -ErrorAction SilentlyContinue
$present = ($ubr -eq 9911) -or [bool]$hotfix

if ($pendingReboot) {
    Write-Output "Restart pending already. Build $build.$ubr, Spooler=$spooler"
    exit 0
}

if ($present) {
    Write-Output "KB5132043 PRESENT: build $build.$ubr, Spooler=$spooler"
    exit 1
}

Write-Output "OK: KB5132043 not present. Build $build.$ubr, Spooler=$spooler"
exit 0
