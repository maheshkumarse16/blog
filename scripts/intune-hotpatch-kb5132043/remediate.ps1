<#
    Author      : Mahesh Kumar S.E
    Version     : 1.2
    Description : Intune Remediation - REMEDIATION. Uninstalls the hotpatch package
                  Package_for_HotpatchFix_9911 (KB5132043) using DISM (Remove-WindowsPackage).
                  Only removes when exactly ONE matching package is found; otherwise it
                  prints the candidates and exits 1 without changing anything.
                  No restart is forced and no update scan is triggered. Pilot first.
    Website     : https://maheshkumarse.com
#>

$candidates = @(Get-WindowsPackage -Online -ErrorAction Stop | Where-Object {
    $_.PackageState -eq 'Installed' -and $_.PackageName -match 'HotpatchFix_9911|KB5132043'
})

if ($candidates.Count -ne 1) {
    Write-Output "Expected 1 matching package but found $($candidates.Count). Not removing anything."
    $candidates | ForEach-Object { Write-Output ("  {0} | {1} | {2}" -f $_.PackageName, $_.PackageState, $_.ReleaseType) }
    exit 1
}

$name = $candidates[0].PackageName
Write-Output "Removing package: $name"

try {
    $r = Remove-WindowsPackage -Online -PackageName $name -NoRestart -ErrorAction Stop
    Write-Output "Removed. RestartNeeded = $($r.RestartNeeded)"
    exit 0
}
catch {
    Write-Output "Remove-WindowsPackage failed: $($_.Exception.Message)"
    exit 1
}
