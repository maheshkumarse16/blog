---
title: "Windows 11 23H2 Enterprise support ends on 10 November: find the stragglers and upgrade them with Intune"
date: 2026-10-26
author: Mahesh
type: How to
description: "The November 2026 Patch Tuesday is the last security update for Windows 11 23H2 Enterprise and Education. A step by step guide to finding every remaining 22H2 and 23H2 device, moving them to a supported version with an Intune feature update policy, and clearing the usual blockers."
tags: [Windows 11, Intune, Vulnerability Management]
---

Every estate has them. The handful of laptops that missed the last feature update because they were in a drawer, on a long leave, stuck on a safeguard hold or simply never in the right group. For Windows 11 23H2 Enterprise and Education, that tail now has a hard deadline.

**The 10 November 2026 security update is the last one for 23H2 Enterprise and Education.** From December, any 23H2 device stops getting security fixes, and it will start lighting up in every vulnerability report you run. 22H2 Enterprise and Education already reached end of servicing in October 2025, so anything still on 22H2 is already unpatched.

That leaves about two weeks. Here is how I would use them.

## Before you start

* **Licences and roles.** Feature update policies need Microsoft Intune Plan 1 and a Windows licence that includes the Windows Autopatch entitlement. To create policies you need the Policy and Profile manager role, or a custom role with the Device configurations permissions. To view reports, Read Only Operator or Help Desk Operator is enough.
* **Device requirements.** Devices must be Intune managed and Entra joined or hybrid joined, running Pro, Pro Education, Enterprise or Education. Enterprise LTSC is not supported by feature update policies.
* **Diagnostic data** must be set to at least **Required**.
* **The Microsoft Account Sign In Assistant service** (`wlidsvc`) must be enabled and running. This one is disabled by hardening scripts more often than you would think.
* **Pick your target version.** Windows 11 25H2 is the obvious choice for most estates, or 26H2 if you have already tested it. 24H2 Enterprise is supported until October 2027, but there is little point upgrading to something that old.
* **A pilot group** of a few 23H2 devices whose users will tell you quickly if something breaks.

## Step 1. Find every device still on 22H2 or 23H2

Windows 11 23H2 reports an OS version starting `10.0.22631`, and 22H2 reports `10.0.22621`.

1. In the Intune admin center, open the device list.

<span class="path">Devices > All devices</span>

2. Add a filter on **OS** for Windows, then sort or filter on the **OS version** column and look for versions starting `10.0.22631` and `10.0.22621`.
3. Export the list. For more than a few hundred devices, Graph is quicker and easier to repeat.

```powershell
Connect-MgGraph -Scopes "DeviceManagementManagedDevices.Read.All"

$uri = "https://graph.microsoft.com/v1.0/deviceManagement/managedDevices?`$filter=operatingSystem eq 'Windows'&`$select=deviceName,osVersion,userPrincipalName,lastSyncDateTime,complianceState"
$devices = @()
do {
    $page = Invoke-MgGraphRequest -Method GET -Uri $uri
    $devices += $page.value
    $uri = $page.'@odata.nextLink'
} while ($uri)

$devices |
    Where-Object { $_.osVersion -like '10.0.22631*' -or $_.osVersion -like '10.0.22621*' } |
    Select-Object deviceName, osVersion, userPrincipalName, lastSyncDateTime, complianceState |
    Sort-Object lastSyncDateTime |
    Export-Csv .\Win11-23H2-and-22H2.csv -NoTypeInformation
```

   A good result is a CSV of the devices you need to move. Sorting by `lastSyncDateTime` puts the ones that have not checked in for weeks at the top. Those are rarely an upgrade problem. They are an asset problem, so hand that list to whoever owns hardware.

4. Put the devices that synced in the last 14 days into an Entra device group, for example `Win11 FU 23H2 Remediation`. Those are the ones a feature update policy can actually reach before the deadline.

## Step 2. Check nothing is holding them back

Most stragglers are not broken. Something in policy is quietly stopping them.

5. Check the update rings assigned to these devices. If a device is targeted by both a feature update policy and an update ring, set **Feature update deferral period (days)** to **0** in the ring. Otherwise the ring deferral delays the feature update.
6. Make sure feature updates are **not paused** in that ring.
7. Check that diagnostic data is set to **Required** or higher and that `wlidsvc` is not disabled by a script or baseline. On a sample device you can confirm the service like this.

```powershell
Get-Service wlidsvc | Select-Object Name, Status, StartType
```

   `StartType` should be `Manual` or `Automatic`, not `Disabled`. The service starts on demand, so a `Stopped` status on its own is fine.

8. Check free disk space on a few of the oldest devices. A full feature update needs plenty of room, and small SSDs full of OneDrive files are one of the most common reasons an upgrade sits at "pending" for weeks.

## Step 3. Create the feature update policy

9. Open the feature updates area.

<span class="path">Devices > Windows > Windows updates > Feature updates</span>

10. Select **Create profile**.
11. On **Deployment settings**, enter a **Name** such as `Windows 11 25H2 for 23H2 remediation` and a short description.
12. In **Feature update to deploy**, select your target version, for example Windows 11, version 25H2. Only versions that are still supported appear in the list.
13. Choose **Make available to users as a required update**. With only two weeks left, an optional update is not going to get you there. The optional choice also needs a Windows Autopatch licence.
14. Under **Rollout options**, decide how fast to go. If the group is small, make it available straight away. If it is a few thousand devices, spread it over several days so you are not pulling the whole payload over the network in one morning.
15. Select **Next**, assign the policy to your pilot group first, then select **Next** again.
16. On **Review + create**, check the settings and select **Create**.

## Step 4. Pilot, then widen

17. Give the pilot a day or two. Ask those users to leave their devices on and connected overnight.
18. Once the pilot devices report the new version, edit the policy and add your full remediation group.
19. Remind users about restarts. The restart experience, deadlines and active hours still come from your update rings, so if those are relaxed, consider a tighter deadline ring just for this group until the deadline passes.

## Verify it worked

* **In Intune.** Open **Devices > Windows > Windows updates > Feature updates** to see your profile's assignment and support status. For per device progress, go to **Reports > Windows Updates**, open the **Reports** tab and run the **Feature Updates report** for your policy.
* **Readiness.** In the Windows feature updates organisational report, a device in the `OfferReady` state has finished policy processing and will be offered the update at its next scan.
* **On the device.** After the upgrade, confirm the version.

```powershell
(Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion').DisplayVersion
```

   A device moved to 25H2 returns `25H2`. If it still returns `23H2` after a few days, check the troubleshooting table below.

* **Rerun the Graph export from step 1** every couple of days. The list should shrink towards zero, or towards just the devices that are not syncing at all.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| Device never shows as offered | Diagnostic data below Required, or `wlidsvc` disabled | Fix the policy or script that sets them, then sync the device |
| Report shows the device is held | A Microsoft safeguard hold applies to that hardware or driver | Check the hold details in the report, update the driver or firmware, or target a different version |
| Upgrade stuck downloading or pending for days | Low disk space or a slow or metered connection | Free up space, check OneDrive usage, and make sure the device is on a decent network overnight |
| Device installed a quality update but not the feature update | Update ring defers or pauses feature updates | Set **Feature update deferral period (days)** to 0 and unpause feature updates |
| Upgrade rolls back after restart | Driver or app compatibility, often older security or VPN agents | Read `setuperr.log` and `setupact.log` under `C:\$WINDOWS.~BT\Sources\Panther`, or run Microsoft's SetupDiag tool, then update the driver or agent |
| Device removed from the group never gets the update | Devices that drop out of a feature update policy are not offered a feature update until they are assigned a new one | Keep devices in the group until they have upgraded |
| Enterprise LTSC devices ignored | LTSC is not supported by feature update policies | Leave LTSC alone, it has its own lifecycle |

In most estates I have seen, the real work here is step 2, not step 3. Creating the policy takes five minutes. Finding out that one old update ring was pausing feature updates for a whole department is what eats the day, so check the rings before you blame the devices.

<div class="refs" markdown="1">

**References**

1. [IT Connect on the October 2026 update and the end of updates for 23H2 Enterprise and Education](https://www.it-connect.tech/windows-11-kb5127648-what-you-need-to-know-about-the-october-2026-update/)
2. [Neoteo on the November 2026 end of updates for 23H2 Enterprise and Education](https://www.neoteo.com/en/microsoft-adds-a-remote-desktop-issue-to-its-october-windows-11-update)
3. [Microsoft Learn on Windows feature update prerequisites and update ring interaction in Intune](https://learn.microsoft.com/lt-LT/mem/intune/protect/windows-10-feature-updates)
4. [Microsoft Learn on creating a Windows feature update policy and its reports](https://learn.microsoft.com/lt-lt/intune/device-updates/windows/configure-feature-update-policy)
5. [Anoop C Nair on upgrading with the Intune feature update deployment policy](https://www.anoopcnair.com/windows-11-feature-update-deployment-policy/)

</div>
