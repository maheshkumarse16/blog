---
title: "Microsoft 365 Apps October 2026 security update: the builds to check for and how to get there"
date: 2026-10-20
author: Mahesh
type: What's new
description: "The 13 October 2026 Office security release fixes 132 CVEs, including eight in Outlook. This lists the exact build for every channel and LTSC version, and shows how to push a device to it and confirm it."
tags: [Microsoft 365, Vulnerability Management]
---

The October Office security release shipped on 13 October 2026 alongside the Windows updates. By my count from the Learn security updates page it covers 132 CVEs. Excel takes the biggest share with 51, then the shared Office components with 36, Access and Word with 13 each, Outlook with 8, PowerPoint with 7, Visio with 3 and OneNote with 1.

The Outlook items are the ones I would chase first. All eight are remote code execution bugs, and community analysis of the advisories lists the Preview Pane as an attack vector for at least two of them, `CVE-2026-70242` and `CVE-2026-70291`. None was public or exploited at release. Also bear in mind the Windows side of Patch Tuesday fixed an actively exploited Mark of the Web bypass, `CVE-2026-96951`, which press reports say stops Office Protected View and macro blocking from kicking in on files from the internet. Patching Office without Windows leaves that door open.

## The builds that contain the fixes

Any device at or above the build for its channel has the October fixes.

| Product and channel | Version | Build |
|---|---|---|
| Current Channel | 2609 | 20430.20182 |
| Monthly Enterprise Channel | 2609 | 20430.20180 |
| Monthly Enterprise Channel | 2608 | 20326.20232 |
| Monthly Enterprise Channel | 2607 | 20228.20276 |
| Semi Annual Enterprise Channel | 2609 | 20430.20178 |
| Semi Annual Enterprise Channel | 2608 | 20326.20230 |
| Semi Annual Enterprise Channel | 2607 | 20228.20274 |
| Office 2024 Retail | 2609 | 20430.20182 |
| Office 2021 Retail | 2608 | 20326.20232 |
| Office LTSC 2024 Volume Licensed | 2408 | 17932.21056 |
| Office LTSC 2021 Volume Licensed | 2108 | 14334.20974 |
| Office 2019 Volume Licensed | 1808 | 10417.20228 |

The Current Channel build also fixes an Excel crash after coauthoring and an Outlook crash while searching for people. The previous Current Channel build, 20430.20146 from 6 October, does not have the security fixes.

Office LTSC 2021 and Office 2021 reached end of support on 13 October 2026, so these are the last builds those products will get.

## Why Semi Annual devices are on 2609

If you still think of Semi Annual Enterprise Channel as a slow channel, the table will look wrong. Since the Version 2606 release in July 2026 Microsoft has unified Semi Annual Enterprise Channel with Monthly Enterprise Channel. Semi Annual devices now get the same feature and security updates, with their own build numbers, and once on 2606 or later they show as Monthly Enterprise Channel under **File > Account**. Different build numbers between the two channels do not mean different security content. Any compliance script or report that looks for the literal text Semi Annual Enterprise Channel needs a look, because those devices will report differently.

## Check a device

1. Open Word, Excel or Outlook and go to **File > Account**.
2. Under **Product Information** read the version and build next to **About**, and compare the build with the table above.
3. Next to **Update Options** you should see **Updates are automatically downloaded and installed**. If you see something else, select **Update Options > Enable updates**.

## Push a device to the build now

Office updates arrive from the CDN gradually over several days, so a device that has not updated yet is not necessarily broken.

4. On a single device, select **File > Account > Update Options > Update Now**. Office downloads the update in the background and applies it when the apps close. The device needs at least 4 GB free on the system drive.

5. To move a group of devices to an exact build, use the Office Deployment Tool with `TargetVersion`. Build the version string from 16.0 plus the build in the table. For Current Channel that is 16.0.20430.20182.

```xml
<Configuration>
  <Updates Enabled="TRUE" TargetVersion="16.0.20430.20182" />
</Configuration>
```

Run it from an administrator command prompt in the folder that holds `setup.exe`.

```cmd
setup.exe /configure config.xml
```

When it finishes, **File > Account** should show the target build. If the apps were open, the update waits until they close unless you add `FORCEAPPSHUTDOWN` with a value of TRUE in a `Property` element, which closes them and can lose unsaved work.

6. For managed fleets, set a deadline so stragglers are forced through. In Group Policy the setting lives under the Office update policies.
<span class="path">Computer Configuration > Policies > Administrative Templates > Microsoft Office 2016 (Machine) > Updates</span>
Enable **Update deadline** and set the date and time the update must be installed by. Users get reminders, including one 30 minutes before the deadline, and Office closes the apps at the deadline. The same settings are available in Intune through the Settings Catalog. A Group Policy value wins over the same value set by the Office Deployment Tool.

7. If you use cloud update at config.office.com, check **Update progress** for each profile. Cloud update takes priority over every other management tool for devices signed in by your users, so do not fight it with Group Policy.

## Confirm across the fleet

8. In your software inventory, list devices below the build for their channel. Any device on a version older than the oldest supported Monthly Enterprise version, 2607, is out of support and will not get the October fixes at all. Move it to a supported channel before worrying about the build.

9. Pay particular attention to Outlook 2016 MSI installs. Community tracking of the release shows no October update for that product, so do not assume this release covers it.

I tend to find that the October problem devices are the ones nobody remembers. Shared machines, kiosk PCs and the old LTSC 2021 boxes in labs or production lines. With LTSC 2021 now out of support, this is a good month to get a real count of those, because there will be no November build for them.

<div class="refs" markdown="1">

**References**

1. [Release notes for Microsoft 365 Apps security updates](https://learn.microsoft.com/en-us/officeupdates/microsoft365-apps-security-updates)
2. [Current Channel release notes](https://learn.microsoft.com/en-us/officeupdates/current-channel)
3. [Monthly Enterprise Channel release notes](https://learn.microsoft.com/en-us/officeupdates/monthly-enterprise-channel)
4. [Unified update channels for Microsoft 365 Apps](https://learn.microsoft.com/en-us/microsoft-365-apps/updates/unified-update-channels/)
5. [Update basics for Microsoft 365 Apps](https://learn.microsoft.com/en-US/deployoffice/updates/update-basics)
6. [Configure update settings for Microsoft 365 Apps](https://learn.microsoft.com/deployoffice/configure-update-settings-microsoft-365-apps)
7. [Office Deployment Tool configuration options](https://learn.microsoft.com/en-us/microsoft-365-apps/deploy/office-deployment-tool-configuration-options)
8. [Cloud update for Microsoft 365 Apps](https://learn.microsoft.com/deployoffice/admincenter/cloud-update)
9. [BleepingComputer on October 2026 Patch Tuesday](https://www.bleepingcomputer.com/news/microsoft/microsoft-october-2026-patch-tuesday-fixes-1-411-flaws-3-zero-days/)
10. [Community summary of classic Outlook updates](https://robert365.com/news/latest-updates-for-classic-outlook)

</div>
