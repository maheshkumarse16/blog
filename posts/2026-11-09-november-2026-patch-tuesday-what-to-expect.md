---
title: "November 2026 Patch Tuesday is tomorrow: what to expect and what to check first"
date: 2026-11-09
author: Mahesh
type: What's new
description: "The November 2026 security update lands on 10 November. It is the last one for Windows 11 23H2 Enterprise and Education, and it brings the October preview fixes, including the Always On VPN fix, to every device. A short note on what to expect and what to check before and after it lands."
tags: [Windows 11, Vulnerability Management, Intune]
---

A quick heads up before tomorrow. The November 2026 Patch Tuesday is on **10 November**, and this one matters more than most for three reasons. It is the last security update for Windows 11 23H2 Enterprise and Education, it carries the fixes from the October preview update to everyone, and it closes a run of known issues that many of us have been living with since September.

I will write up the full list of CVEs and what to patch first once the release is out. This post is about getting ready.

## The last update for 23H2 Enterprise and Education

After tomorrow, Windows 11 23H2 Enterprise and Education stop getting security updates. Any device still on 23H2 after this release will start showing up as unpatched in every vulnerability report from December onwards. Anything still on 22H2 is already out of support.

If you have not checked recently, today is a good day to run the device query again and see how many are left. I covered the full process in my guide on [finding the stragglers and upgrading them with an Intune feature update policy](/2026/10/26/windows-11-23h2-end-of-servicing-upgrade-with-intune/). The short version is this.

* Filter your Intune device list for OS versions starting `10.0.22631` for 23H2 and `10.0.22621` for 22H2.
* Check that update rings are not pausing or deferring feature updates for those devices.
* Make sure the devices are actually checking in. A device that has not synced for weeks is an asset problem, not an update problem.

## The Always On VPN fix reaches everyone

The Always On VPN problem from the September updates was fixed in the October preview update, KB5127936. Devices that did not take the preview will get the same fix tomorrow. If you followed my [Always On VPN workaround](/2026/10/28/always-on-vpn-stuck-on-connecting-workaround/) and set your profiles to a single protocol, plan when to test the fix on a pilot group before you put automatic protocol selection back. There is no rush to change the profile. A single protocol profile keeps working after the fix.

## Other fixes coming through from the preview

According to the release notes and the reports I checked, the October preview also fixed the following, so they arrive for everyone tomorrow.

* **Smart App Control toggle stuck greyed out** after the October security update.
* **No sound over HDMI or DisplayPort** on some AMD graphics configurations.

Microsoft's tracker also lists the Remote Desktop error `0xC000000D` for standard users with Administrator protection, and the black screen after sign in on AVD hosts with FSLogix, as resolved by updates from 13 October onwards. If you put workarounds in place for either of those, tomorrow's update is a good point to test removing them on a pilot group.

## Still open

The one issue still listed as open for 26H2 at the time of writing is the **USB Audio Class 1.0** problem, where some older USB headsets and audio devices show Code 10 in Device Manager or play no sound. Microsoft has said a fix is coming in a future update. Check the release notes tomorrow to see whether it is in this one.

## What I will check tomorrow

* **The known issues section of the release notes first.** That is where new problems appear before they show up in forums.
* **Exploited and publicly disclosed CVEs.** Those go to the top of the list, the same way they did in [the October triage](/2026/10/21/october-2026-patch-tuesday-what-to-patch-first/).
* **The VPN fix on a pilot group** with automatic protocol selection turned back on.
* **Any device still on 23H2** after the update, because from tomorrow that list only gets more expensive to ignore.

## Before you approve it

* Let your normal rings do their job. A pilot ring that gets the update first and reports back before the broad ring is worth more than a quick rollout.
* Make sure update ring deadlines and restart settings are set the way you expect, so users get a predictable restart rather than a surprise one.
* Keep an eye on helpdesk tickets for the first two days. New issues tend to show up there before they appear on the release health dashboard.

I will post the full breakdown once the release is out.

<div class="refs" markdown="1">

**References**

1. [Microsoft support article for KB5127936, the October 2026 preview update](https://support.microsoft.com/en-us/servicing/os/windows-11/2026/10/kb5127936-windows-11-25h2-26h2-update)
2. [BleepingComputer on Microsoft fixing the VPN issues caused by the September updates](https://bleepingcomputer.com/news/microsoft/microsoft-finally-fixes-vpn-issues-caused-by-september-updates)
3. [Help Desk Geek on Microsoft resolving most tracked Windows 11 26H2 issues](https://helpdeskgeek.com/microsoft-resolves-windows-11-26h2-bugs-recommends-upgrading-from-25h2/)
4. [BleepingComputer on Microsoft fixing Smart App Control after the October update](https://www.bleepingcomputer.com/news/microsoft/microsoft-fixes-smart-app-control-broken-by-october-windows-update/)
5. [IT Connect on the October update and the 23H2 end of updates](https://www.it-connect.tech/windows-11-kb5127648-what-you-need-to-know-about-the-october-2026-update/)

</div>
