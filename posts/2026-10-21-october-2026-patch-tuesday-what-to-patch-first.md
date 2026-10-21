---
title: "October 2026 Patch Tuesday: the five CVEs I am patching first"
date: 2026-10-21
author: Mahesh
type: How to
description: "1,411 CVEs landed in one month. These are the five that stood out on my vulnerability dashboard, why they matter on endpoints and servers, and the exact checks I use to confirm each one is closed."
tags: [Vulnerability Management, Windows 11, ConfigMgr, Intune]
---

When the October data refreshed in my vulnerability dashboard, the list was longer than I have ever seen it. Microsoft fixed 1,411 CVEs this month, a record, with around 70 rated Critical. Nobody patches 1,411 things in order of CVE number, so the first job is to sort the noise from the handful that actually need to move today.

These were the five that rose to the top for me, and the reasoning behind each one.

| CVE | Component | Why it is near the top |
|---|---|---|
| `CVE-2026-96951` | Windows Shell | Exploited in the wild, on the CISA Known Exploited Vulnerabilities list |
| `CVE-2026-108398` | .NET Framework | Publicly disclosed, bypasses Windows Defender Application Control |
| `CVE-2026-70229` | Active Directory Domain Services | Remote code execution, no privileges needed, CVSS 8.1 |
| `CVE-2026-88075` | Configuration Manager | SQL injection leading to elevation of privilege over the network, CVSS 8.8 |
| `CVE-2026-70049` | Configuration Manager | SQL injection leading to elevation of privilege over an adjacent network, CVSS 8.0 |

A sixth one, `CVE-2026-92707`, a denial of service in the MessagePack library used by .NET apps, was also publicly disclosed. It is rated Moderate. If you have in house .NET applications that use MessagePack, pass it to the developers. It did not change my patching order.

## Why these five

**The Shell bypass is the only one being exploited.** `CVE-2026-96951` lets an attacker get round Mark of the Web, the tag Windows puts on files that came from the internet. That tag is what triggers SmartScreen warnings and Protected View in Office. Take it away and a phishing attachment opens with no warning at all. That is exactly the kind of flaw attackers use first, which is why it is already in the CISA catalogue.

**The .NET flaw goes after application control.** `CVE-2026-108398` lets a signed in attacker place a crafted .NET assembly and get a protected process to load it, which can bypass Windows Defender Application Control. It was found by James Forshaw of Google Project Zero and the details are public. If you rely on WDAC or App Control for Business to stop unapproved code, this one undermines the control you are counting on.

**The Active Directory flaw needs no credentials.** `CVE-2026-70229` is an incorrect authorisation issue in Active Directory Domain Services that allows remote code execution over the network without privileges or user interaction. Attack complexity is rated High, which helps, but a domain controller is the last place you want unauthenticated code running. The CVE record lists Windows 10, Windows 11 and every supported Windows Server version as affected, so it comes in with the normal cumulative update everywhere. The domain controllers are what make it urgent.

**The two ConfigMgr flaws are SQL injection.** Both let a low privileged user on the network escalate privileges through the site. In most estates the ConfigMgr site server and its database can push software to every device, so elevation there means control of the fleet.

## Before you start

* **Access.** You need rights to view device update status in Intune, and Full Administrator or an equivalent role in Configuration Manager for the site update.
* **Know your build numbers.** After the October update, Windows 11 should report build 26100.9711 (24H2), 26200.9711 (25H2), 26300.9711 (26H2), 28000.3231 (26H1) or 22621.7652 (23H2). Anything lower is missing the Shell fix.
* **Know your ConfigMgr version.** The CVE records list fixed builds for 2503, 2509 and 2603. Version 2609 is not listed as affected.
* **Expedited updates in Intune have prerequisites.** Intune Plan 1, a Windows licence that includes the Windows Autopatch entitlement, Pro, Enterprise or Education editions (not LTSC), devices that are Entra joined or hybrid joined, diagnostic data set to at least Required, and the Microsoft Account Sign In Assistant service (`wlidsvc`) running.
* **Read the known issues.** The October update stops standard users connecting over Remote Desktop to hosts with Administrator protection turned on (error `0xC000000D`), and some USB Audio Class 1.0 devices show Code 10. Neither is a reason to hold the update, but warn the service desk first.

## Step 1. Close the Shell bypass on endpoints

1. Confirm which devices are still below the October build. On a single device, this returns the build and the update revision.

```powershell
$cv = Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion'
"{0}.{1}" -f $cv.CurrentBuildNumber, $cv.UBR
```

   A patched 25H2 device returns `26200.9711` or higher. A result such as `26200.9650` means the October update is missing.

2. Check that `KB5127648` (or `KB5127646` on 26H1, `KB5126653` on 23H2) shows as installed.

```powershell
Get-HotFix | Where-Object HotFixID -in 'KB5127648','KB5127646','KB5126653'
```

   A good result lists the KB with an `InstalledOn` date. No output means it is not there.

3. Across the fleet, use the Windows quality update reporting in Intune to list devices that have not reached the October build, and export the list.
4. For the devices that are behind, create an expedited quality update profile in Intune and target the October 2026 security release. This tells eligible devices to install it straight away and skip any deferral set in your update rings.
5. Leave the restart behaviour to your existing update rings, which is where Intune takes it from. If your rings allow long restart deadlines, shorten them for this release.
6. Keep the Remote Desktop exception scoped. If you already turned off Administrator protection on a few RDP hosts for the `0xC000000D` issue, do not widen that group as part of this push.

## Step 2. Make sure the .NET fix is actually installed

7. The .NET Framework fixes ship as their own cumulative update for .NET Framework, separate from the Windows cumulative update. A device can be fully up to date on Windows and still be missing the .NET part, so check it on its own.
8. Look at the installed updates on a sample device.

```powershell
Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 10 HotFixID, Description, InstalledOn
```

   You should see two October entries, the Windows cumulative update and a separate .NET Framework update. If you only see one, the .NET update has not arrived.

9. If you use WDAC or App Control for Business on high value machines, such as privileged access workstations, jump hosts and build servers, put those first in the queue for the .NET update.

## Step 3. Patch the domain controllers

10. Patch domain controllers in your normal server window, but bring this month's window forward if you can. Do one domain controller per site first, confirm replication, then the rest.
11. After each one restarts, confirm it took the October cumulative update and that replication is healthy.

```powershell
repadmin /replsummary
```

   A good result shows `0` in the fails column for every domain controller. Any failures should be fixed before you patch the next one.

## Step 4. Patch Configuration Manager

12. In the console, check for the October security update for your version.

<span class="path">Administration > Overview > Updates and Servicing</span>

13. Install it the same way as any in console update, then confirm the new site version.

<span class="path">Administration > Site Configuration > Sites</span>

14. Compare the version against the fixed builds from the CVE records. For `CVE-2026-88075` they are 5.00.9135.1040 or later on 2503, 5.00.9141.1039 or later on 2509, and 5.00.9146.1026 or later on 2603. For `CVE-2026-70049` they are 5.00.9135.1042, 5.00.9141.1041 and 5.00.9146.1027, so the second set is the one to aim for.
15. If you are planning the move to 2609 anyway, this is a good reason to bring it forward, since 2609 is not listed as affected.
16. Until the site is patched, limit who can reach the site server and SQL from the network. Both flaws need an authenticated low privileged user, so anyone with an account and a network path is a candidate.

## Verify it worked

* **Shell fix.** Rerun the build check from step 1 on a sample of devices from each ring. Every one should report the October build or higher.
* **.NET fix.** Check the same sample for the separate .NET Framework update from step 2.
* **Domain controllers.** Every domain controller shows the October cumulative update and `repadmin /replsummary` shows no failures.
* **ConfigMgr.** The site version in **Sites** matches or exceeds the fixed build for your branch.
* **Dashboard.** Give your vulnerability tool a full scan cycle, then confirm the five CVEs have dropped off the exposure list. If a CVE stays open on a device that reports the right build, rescan that device before assuming the patch failed.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| Device never picks up the expedited update | A prerequisite is missing, often diagnostic data below Required or `wlidsvc` disabled | Check the service and the diagnostic data policy on the device, then sync |
| Device shows the October Windows build but the dashboard still flags the .NET CVE | The separate .NET Framework update is not installed | Check installed updates for the .NET entry and deploy it |
| LTSC devices ignore the expedite profile | LTSC is not supported for expedited updates | Use an update ring with zero deferral for those devices |
| Standard users cannot RDP after the update, error `0xC000000D` | Known issue with Administrator protection on the target host | Apply the scoped workaround to the affected hosts only |
| USB headset shows Code 10 | Known issue with some USB Audio Class 1.0 devices | Microsoft is directing business customers to Support for Business |
| ConfigMgr update not showing in the console | Service connection point offline or still downloading | Check `dmpdownloader.log` on the site server |
| Replication failures after patching a domain controller | Restart left a service or link unhealthy | Fix replication before you move on to the next domain controller |

The part that usually catches people out this month is .NET. Teams see a compliant Windows build in their reporting, tick the box, and the WDAC bypass stays open for weeks because nobody looked at the second update. If you only change one thing in your checks, add the .NET Framework update to the list.

<div class="refs" markdown="1">

**References**

1. [BleepingComputer on the October 2026 Patch Tuesday fixes and zero days](https://www.bleepingcomputer.com/news/microsoft/microsoft-october-2026-patch-tuesday-fixes-1-411-flaws-3-zero-days/)
2. [Fortra analysis of the October 2026 Patch Tuesday](https://www.fortra.com/blog/october-2026-patch-tuesday-analysis)
3. [CVE record for CVE-2026-70229, Active Directory Domain Services](https://app.opencve.io/cve/CVE-2026-70229)
4. [CVE record for CVE-2026-88075, Configuration Manager](https://app.opencve.io/cve/CVE-2026-88075)
5. [CVE record for CVE-2026-70049, Configuration Manager](https://app.opencve.io/cve/CVE-2026-70049)
6. [Microsoft Learn on expedited Windows quality updates in Intune](https://learn.microsoft.com/en-us/intune/intune-service/protect/windows-10-expedite-updates)
7. [Windows Report on the KB5127648 known issues](https://windowsreport.com/?p=1512407)
8. [IT Connect on the October 2026 Windows 11 builds](https://www.it-connect.tech/windows-11-kb5127648-what-you-need-to-know-about-the-october-2026-update/)

</div>
