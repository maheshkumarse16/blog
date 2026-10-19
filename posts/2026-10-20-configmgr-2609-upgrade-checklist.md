---
title: "ConfigMgr 2609 is here: what changed and how to upgrade safely"
date: 2026-10-20
author: Mahesh
type: How to
description: "2609 is the first ConfigMgr release under the new once a year cadence. It drops some old platforms, fixes a comanagement problem and needs a bit of preparation before you click install."
tags: [ConfigMgr, Windows 11]
---

Configuration Manager 2609 is out, and it marks a real change in how the product ships. Here is what is different and the checks I would run before upgrading.

## One release a year from now on

ConfigMgr used to get two current branch releases a year. Starting with 2609, it moves to one. The next planned release is 2709 in September 2027. Between now and then, expect only hotfix rollups and critical security fixes.

Each release still gets 18 months of support, so 2609 is supported until around March 2028.

Microsoft has been open about the direction. ConfigMgr stays focused on managing on premises devices with an emphasis on security and stability, and new features go into Intune. If you have been waiting for a new ConfigMgr feature, it is probably not coming.

## What changed in 2609

### Support removed

* **Windows Server 2012 and 2012 R2** are no longer supported for site systems.
* **SQL Server 2016** is no longer supported. You need SQL Server 2017 CU2 or later. A site running an unsupported SQL version will not upgrade until SQL is moved forward.

### Fixes worth knowing about

* **Comanagement and Defender settings.** On devices managed by both ConfigMgr and Intune, ConfigMgr could override the cloud block level and timeout values set in Intune. That is fixed. If you have seen Defender settings flip back on comanaged devices, this is likely why.
* **SQLCLR.** ConfigMgr no longer uses the SQL `TRUSTWORTHY` database property for its SQLCLR assemblies and relies on Microsoft signed assemblies instead. A good security improvement.
* **Console disk space.** The console could show 0 bytes free after certain restarts. Fixed.
* Earlier hotfixes are rolled into this release.

### Windows 11 26H2

Both 2603 and 2609 support deploying Windows 11 26H2.

## Before you upgrade

Run through this list first. It takes an hour and saves a long evening.

1. **Check your current version.** You must be on 2503 or later to install 2609 as an in console update.
2. **Check SQL.** Confirm the site database is on SQL Server 2017 CU2 or later.
3. **Check site server operating systems.** No site system roles on Server 2012 or 2012 R2.
4. **Take a backup.** Make sure the Backup Site Server maintenance task has run successfully and you know where the backup is.
5. **Save customisations.** If you or a third party product changed any ConfigMgr configuration files, copy them somewhere safe. The upgrade can overwrite them.
6. **Pause anything that writes heavily to the database.** Large deployments and software update syncs can wait until the upgrade is done.
7. **Upgrade a test hierarchy first** if you have one.

## Running the upgrade

In the console, go to the updates node.

<span class="path">Administration > Overview > Updates and Servicing</span>

1. Wait for 2609 to show as **Ready to install**. If it is stuck downloading, check `dmpdownloader.log` on the site server.
2. Right click the update and choose **Run prerequisite check**. Do not skip this.
3. Watch `C:\ConfigMgrPrereq.log` on the site server and the status under **Monitoring > Overview > Updates and Servicing Status**.
4. Fix every error. Read every warning too, because warnings are often what bites you later.
5. When the check passes, right click again and choose **Install Update Pack**.
6. Follow progress in `CMUpdate.log` in the Logs folder of your ConfigMgr install directory.
7. After the site updates, open the console again. It will prompt you to update the console itself.

## After the upgrade

* Confirm the site version in **Administration > Site Configuration > Sites**.
* Update the client package and plan a client upgrade. Automatic client upgrade is the easiest route if you already use it.
* Check that comanaged devices keep the Defender cloud protection values you set in Intune.
* Recreate any configuration file customisations you saved earlier.

## What I would do this week

* Check SQL and server OS versions on every site system.
* Read Microsoft's 2609 release notes for anything specific to your setup.
* Book the upgrade in a change window and upgrade a test site first.
* Start planning which ConfigMgr workloads you can move to Intune, since that is where new features will land.

<div class="refs" markdown="1">

**References**

1. [Microsoft Tech Community on the annual release cadence for Configuration Manager](https://techcommunity.microsoft.com/blog/configurationmanagerblog/announcing-the-annual-release-cadence-for-microsoft-configuration-manager/4464794)
2. [Windows Report on Windows 11 26H2 support in ConfigMgr 2603 and 2609](https://windowsreport.com/?p=1511156)
3. [Prajwal Desai on the Configuration Manager 2609 upgrade](https://www.prajwaldesai.com/?p=341736)
4. [Microsoft Learn on supported Configuration Manager current branch versions](https://learn.microsoft.com/en-au/mem/configmgr/core/servers/manage/current-branch-versions-supported)

</div>
