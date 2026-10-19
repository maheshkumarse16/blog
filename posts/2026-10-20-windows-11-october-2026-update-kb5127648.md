---
title: "Windows 11 October 2026 update: builds, fixes and what to patch first"
date: 2026-10-20
author: Mahesh
type: What's new
description: "KB5127648 is a big one. A record number of CVEs, an exploited zero day, real fixes for AVD and VPN users, and the last update for 24H2 Home and Pro."
tags: [Windows 11, Vulnerability Management]
---

Microsoft released the October cumulative updates for Windows 11 on 13 October 2026. If you manage a Windows fleet, this is one to move through your rings quickly.

## Which update and build you should see

| Windows 11 version | Update | Build after install |
|---|---|---|
| 26H2 | `KB5127648` | 26300.9711 |
| 25H2 | `KB5127648` | 26200.9711 |
| 24H2 | `KB5127648` | 26100.9711 |
| 26H1 | `KB5127646` | 28000.3231 |
| 23H2 | `KB5126653` | 22621.7652 |

If you report on compliance in Intune or ConfigMgr, the build number is the quickest way to confirm a device has it. Anything on 25H2 below 26200.9711 has not taken the October update yet.

## Why you should not sit on this one

This release covers more than 1,400 CVEs, which is the largest Patch Tuesday Microsoft has shipped. Around 70 are rated Critical, and most of those are remote code execution.

One of them, `CVE-2026-96951`, is a Windows Shell security feature bypass that was already being exploited before the patch came out. It is in the CISA Known Exploited Vulnerabilities catalog. Two other vulnerabilities were publicly disclosed before the fix.

In my experience the usual approach of letting a quality update sit in pilot for a week or two is fine for most months. With an exploited zero day in the mix, I would shorten that window this time.

## What it fixes

The update also clears several problems that have been around for a while.

* **Explorer on multi user hosts.** Explorer could fail to start or crash after sign in on Azure Virtual Desktop and other FSLogix setups, leaving users with a black screen. This is fixed, so any workaround you put in place for it can come out after testing.
* **Always On VPN.** Connection problems with Always On VPN are resolved.
* **AC3 audio.** Playback of AC3 audio failed in some apps. Fixed.
* **Windows Hello fingerprint.** Fingerprint sign in could fail after a cold boot. Fixed.
* **File History.** Backups and restores to an external drive or network location could fail. Fixed.

The update also continues the rollout of the new Secure Boot certificates, with Windows Update using updated targeting data to decide which devices are ready.

## Known issues still open

Two problems are still listed against `KB5127648`.

1. Remote Desktop connections can fail for standard users when the target device has Administrator protection turned on. I have written this one up separately with what to do until Microsoft ships a fix.
2. Some USB Audio Class 1.0 devices may not start, may play no sound, or may show Code 10 in Device Manager. Microsoft says it only affects that device class and is asking business customers who need a quick workaround to contact Support for Business.

## Lifecycle dates to note

* **24H2 Home and Pro** reached end of updates with this release. October 2026 was their last update.
* **24H2 Enterprise and Education** continue to get updates until 12 October 2027.
* **23H2 Enterprise and Education** get their final update on 10 November 2026.

If you still have 23H2 devices in the estate, now is the time to target a feature update at them. After November they stop getting security fixes.

## What I would do this week

* Approve `KB5127648` for your pilot ring now and shorten the gap before broad deployment.
* Build a quick report of devices below build 26200.9711 on 25H2 and 26100.9711 on 24H2.
* If you run AVD with FSLogix, test this update on a host pool first, since it fixes the Explorer black screen.
* Warn your service desk about the Remote Desktop error `0xC000000D` and the USB audio Code 10 issue.
* List every remaining 23H2 device and get them upgraded before 10 November.

<div class="refs" markdown="1">

**References**

1. [Windows Report on the October 2026 Patch Tuesday updates](https://windowsreport.com/windows-11-kb5126653-kb5127648-kb5127646-october-2026-patch-tuesday-released/)
2. [BleepingComputer on the October 2026 Patch Tuesday CVEs and zero days](https://www.bleepingcomputer.com/news/microsoft/microsoft-october-2026-patch-tuesday-fixes-1-411-flaws-3-zero-days/)
3. [IT Connect on what KB5127648 fixes and the lifecycle dates](https://www.it-connect.tech/windows-11-kb5127648-what-you-need-to-know-about-the-october-2026-update/)
4. [Neoteo on the build numbers and known issues](https://www.neoteo.com/en/microsoft-adds-a-remote-desktop-issue-to-its-october-windows-11-update)

</div>
