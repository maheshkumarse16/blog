<#
    Author      : Mahesh Kumar S.E
    Version     : 1.1
    Description : Intune Remediation - DETECTION. Flags any device that has the hotpatch
                  package Package_for_HotpatchFix_9911 (KB5132043) installed.
                  Exit 1 = hotpatch package present (runs remediation)
                  Exit 0 = not present, or a restart is already pending
    Website     : https://maheshkumarse.com
#>

$cv    = Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion'
$build = $cv.CurrentBuildNumber
$ubr   = [int]$cv.UBR

$spooler = (Get-Service -Name Spooler -ErrorAction SilentlyContinue).Status
$pendingReboot = Test-Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired'

$pkg = @(Get-WindowsPackage -Online -ErrorAction SilentlyContinue | Where-Object {
    $_.PackageState -eq 'Installed' -and $_.PackageName -match 'HotpatchFix_9911|KB5132043'
})

if ($pendingReboot) {
    Write-Output "Restart pending already. Build $build.$ubr, Spooler=$spooler"
    exit 0
}

if ($pkg.Count -gt 0) {
    Write-Output "HOTPATCH PRESENT: $($pkg[0].PackageName). Build $build.$ubr, Spooler=$spooler"
    exit 1
}

Write-Output "OK: hotpatch package not present. Build $build.$ubr, Spooler=$spooler"
exit 0
