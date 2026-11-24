<#
    Author      : Mahesh Kumar S.E
    Version     : 1.2
    Description : Single-file version. Checks whether the hotpatch package
                  Package_for_HotpatchFix_9911 (KB5132043) is present and removes it with DISM
                  (Remove-WindowsPackage). Works as an Intune Platform script (run as SYSTEM,
                  64-bit) or a manual run in an elevated PowerShell.
                  Only removes when exactly ONE matching package is found; otherwise it lists
                  the candidates and exits 1 without changing anything.
                  No restart is forced. No LCU install or scan is triggered.
                  Exit 0 = nothing to do, or removed (restart pending). Exit 1 = failed / unsure.
    Website     : https://maheshkumarse.com
#>

$ErrorActionPreference = 'Continue'

$cv    = Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion'
$build = $cv.CurrentBuildNumber
$ubr   = [int]$cv.UBR
$pendingReboot = Test-Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired'

# 1. Is the hotpatch package present?
$candidates = @(Get-WindowsPackage -Online -ErrorAction Stop | Where-Object {
    $_.PackageState -eq 'Installed' -and $_.PackageName -match 'HotpatchFix_9911|KB5132043'
})

if ($candidates.Count -eq 0) {
    Write-Output "$env:COMPUTERNAME : hotpatch package not present (build $build.$ubr). Nothing to do."
    exit 0
}

if ($pendingReboot) {
    Write-Output "$env:COMPUTERNAME : hotpatch present but a restart is already pending (build $build.$ubr). Skipping."
    exit 0
}

if ($candidates.Count -ne 1) {
    Write-Output "Expected 1 matching package but found $($candidates.Count). Not removing anything."
    $candidates | ForEach-Object { Write-Output ("  {0} | {1} | {2}" -f $_.PackageName, $_.PackageState, $_.ReleaseType) }
    exit 1
}

# 2. Remove it (no restart)
$name = $candidates[0].PackageName
Write-Output "$env:COMPUTERNAME : build $build.$ubr. Removing package: $name"

try {
    $r = Remove-WindowsPackage -Online -PackageName $name -NoRestart -ErrorAction Stop
    Write-Output "$env:COMPUTERNAME : removed. RestartNeeded = $($r.RestartNeeded). Restart required to complete."
    exit 0
}
catch {
    Write-Output "$env:COMPUTERNAME : Remove-WindowsPackage failed: $($_.Exception.Message)"
    exit 1
}
