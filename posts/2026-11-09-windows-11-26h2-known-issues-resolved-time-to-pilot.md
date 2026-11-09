---
title: "Windows 11 26H2: all but one known issue is now resolved. Is it time to start your pilot?"
date: 2026-11-09
author: Mahesh
type: What's new
description: "Microsoft's tracker now shows every Windows 11 26H2 known issue resolved except the USB Audio Class 1.0 problem. A look at what was fixed, what is still open, and how I would plan an enterprise pilot of 26H2 from here."
tags: [Windows 11, Intune]
---

When Windows 11 26H2 reached general availability on 29 September 2026, the list of known issues was long enough that most of us parked it. Domain joined devices losing their trust, Remote Desktop failing for standard users, black screens on AVD hosts and a handful of audio problems. Nobody wanted to be first.

Six weeks later the picture is very different. According to Microsoft's update history, as reported on 4 November, every tracked 26H2 known issue is now resolved except one. That makes this a good moment to decide when your 26H2 pilot starts, rather than whether it should.

## What has been fixed

| Issue | Fixed by |
|---|---|
| Domain joined devices losing their secure trust relationship, caused by Machine Identity Isolation | KB5124010, 22 September 2026 |
| File History failures | KB5124010, 22 September 2026 |
| Remote Desktop error `0xC000000D` for standard users with Administrator protection | Updates from 13 October 2026, including KB5127648 and KB5127936 |
| Black screen after sign in, mostly on AVD hosts with FSLogix | Updates from 13 October 2026 |
| Smart App Control toggle stuck greyed out | KB5127936, late October 2026 |
| No sound over HDMI or DisplayPort on some AMD graphics configurations | KB5127936, late October 2026 |

A few of these hit enterprise estates hard. The trust relationship problem in particular locked users out of domain joined laptops, and I wrote up [how to confirm it and repair the secure channel](/2026/10/27/domain-trust-failed-machine-identity-isolation-26h2/) at the time. If you held 26H2 back because of that one, it has been fixed since September.

## What is still open

One issue remains open. Some **USB Audio Class 1.0** devices, typically older USB headsets and audio adapters, can show a Code 10 error in Device Manager or stop playing sound. Microsoft says a fix is coming in a future update. Some reports say a later update mitigates it for some users, but Microsoft's tracker had not marked it resolved at the time of writing.

For most enterprise fleets this is a manageable risk. Check whether your standard headsets are USB Audio Class 1.0 devices before you pick pilot users, and leave anyone who depends on an older audio device out of the first ring.

## What Microsoft is saying about 26H2

Microsoft's Windows Experience Blog on 3 November said that, in its lab testing, PCs with 8GB of memory were up to 20% more responsive on 26H2, with multitasking up to 40% faster. Coverage of the update has framed that as Microsoft recommending the move from 25H2, mainly for home and small office PCs. That is not the same as a recommendation for managed estates, and I would not treat it as one. Your own pilot is what decides it.

## Why plan the pilot now

* **The servicing clock is already running.** 26H2 is an H2 release, so Enterprise and Education editions get 36 months of servicing from general availability. Starting the pilot sooner gives you more of that window in production.
* **Fixes are rolling in.** Every issue except one is fixed, and the November security update on 10 November brings the October preview fixes to every device.
* **The tooling is ready.** The Intune Settings catalog has been updated for 26H2, and the Windows 11 26H2 security baseline is available. I covered [moving to the 26H2 baseline without a big bang](/2026/10/20/intune-windows-11-26h2-security-baseline-upgrade/) last month.
* **23H2 is ending.** If you still have 23H2 devices after 10 November, it may make sense to move some of them straight to the version you will run for the next few years. Microsoft only offers versions that are still supported in the feature update policy list.

## How I would run the pilot

* **Pick a small, mixed group.** Include laptops and desktops, devices from each hardware model you support, a few VPN users and anyone who uses Remote Desktop heavily.
* **Use a feature update policy.** Target the pilot group with a Windows 11 26H2 feature update policy in Intune, and keep it separate from the policies that move devices off 23H2.
* **Update first, then upgrade.** Make sure the pilot devices take the November security update straight after the upgrade, so they have every fix listed above.
* **Test the things that broke before.** Domain sign in, Remote Desktop for standard users, VPN connections, audio on your standard headsets, and any AVD session hosts if you run them.
* **Give it a full patch cycle.** Leave the pilot on 26H2 through at least one Patch Tuesday before you widen it, and watch helpdesk tickets for those users.

If the pilot is clean through December, a wider rollout in the new year looks reasonable. If something new shows up, you will have found it on a few devices, not a few thousand.

<div class="refs" markdown="1">

**References**

1. [Help Desk Geek on Microsoft resolving most tracked Windows 11 26H2 issues](https://helpdeskgeek.com/microsoft-resolves-windows-11-26h2-bugs-recommends-upgrading-from-25h2/)
2. [PCWorld on the Windows 11 26H2 known issues at launch](https://www.pcworld.com/article/3247667/windows-11-26h2-update-has-known-issues-you-might-want-to-wait.html)
3. [Microsoft Intune Settings catalog updated to support Windows 11 version 26H2](https://techcommunity.microsoft.com/blog/intunecustomersuccess/microsoft-intune-settings-catalog-updated-to-support-windows-11-version-26h2/4560815)
4. [Microsoft support article for KB5127936, the October 2026 preview update](https://support.microsoft.com/en-us/servicing/os/windows-11/2026/10/kb5127936-windows-11-25h2-26h2-update)

</div>
