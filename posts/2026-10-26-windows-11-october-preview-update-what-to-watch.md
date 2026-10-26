---
title: "Coming up this week: the Windows 11 October preview update and what to watch for"
date: 2026-10-26
author: Mahesh
type: What's new
description: "Microsoft's optional preview update for Windows 11 usually lands in the fourth week of the month. A short note on what I am hoping it fixes, what it will not change, and how to handle it safely before the November Patch Tuesday."
tags: [Windows 11, Vulnerability Management]
---

A quick heads up for this week. Microsoft normally releases the optional non security preview update for Windows 11 in the fourth week of the month, so the October preview should appear in the next few days. I will write it up properly once it is out and the release notes are published, but here is what I will be looking for and how I plan to handle it.

## What a preview update is, and is not

The preview update is optional. It carries the non security fixes and changes that will roll into the next Patch Tuesday, which this time is **10 November 2026**. It contains no new security fixes, so there is no security reason to rush it onto the fleet.

What it does give you is an early look. If something you are fighting today is fixed in the preview, you can test it on a few devices now, and then you know what to expect when the same fix arrives in the November security update.

## What I am hoping to see fixed

There are two open known issues on the October update, `KB5127648`, that a lot of us are living with.

* **Remote Desktop error `0xC000000D` for standard users.** Standard users cannot connect over RDP to Windows 11 devices with Administrator protection turned on. Microsoft has said a fix is coming in a future update. If it lands in the preview, that is the moment to plan removing any Administrator protection exceptions you put in place on your RDP hosts. I covered the workaround in an earlier post.
* **Some USB Audio Class 1.0 devices showing Code 10 or playing no sound.** Microsoft has limited this to that device class. If you have users with older USB headsets or DACs, this is the one they will be asking about.

When the release notes come out, these are the first two things I will check for.

## What the preview will not change

**The enterprise WiFi and VPN sign in change is not a bug, so do not expect a fix for it.** Since the October update, Windows blocks NTLMv1 derived credentials for single sign on by default on devices without Credential Guard. That breaks automatic sign in on networks that use PEAP or EAP with MSCHAPv2. Microsoft describes this as a planned hardening change. The temporary workaround is the `BlockNtlmv1SSO` registry value, and the real fix is moving to certificate based authentication. I wrote up the full Intune remediation for it last week. A preview update will not undo it.

## How I handle preview updates

* **Do not push it to everyone.** Previews are optional for a reason. The same fixes arrive in the November Patch Tuesday along with the security fixes, so most devices should simply wait for that.
* **Install it by hand on a few test devices.** Pick devices that represent your real problems, such as an RDP host with Administrator protection, a laptop with one of the affected USB audio devices, and a standard build. Install the preview from Windows Update on those devices only.
* **Check the release notes for anything that touches your stack.** Preview notes are often long. Search them for the things you care about, such as Remote Desktop, Windows Hello, BitLocker, VPN, Secure Boot and printing.
* **Watch the known issues section.** A preview can introduce new problems too, and the known issues section is the first place they appear.

## A forum report I am keeping an eye on

On 22 October someone posted on Microsoft Q&A that, after the October updates, BitLocker encrypted data drives opened with the right key but then showed up as RAW instead of NTFS. It is a single report from one machine, the cause has not been identified and Microsoft has not commented. I am not treating it as a known issue. I mention it only so that if you see something similar, you know you are not the first, and you report it through Feedback Hub with as much detail as you can.

## The dates to keep in mind

| Date | What |
|---|---|
| This week | Windows 11 October optional preview update expected |
| 10 November 2026 | November Patch Tuesday, and the last security update for Windows 11 23H2 Enterprise and Education |
| November 2026 | Windows 365 User settings policies become read only |

If you still have 23H2 devices, that 10 November date is the one to worry about, not the preview. I have written a separate guide on finding them and upgrading them with an Intune feature update policy.

I will update this post with the actual KB number and the confirmed fixes once Microsoft publishes the preview.

<div class="refs" markdown="1">

**References**

1. [Windows Report on the KB5127648 Remote Desktop and USB audio known issues](https://windowsreport.com/?p=1512407)
2. [BleepingComputer on the Remote Desktop failures with Administrator protection](https://bleepingcomputer.com/news/security/microsoft-recent-windows-updates-may-trigger-remote-desktop-failures)
3. [Message Center MC1508562 on the NTLMv1 hardening change](https://mc.merill.net/message/MC1508562)
4. [Microsoft Q&A report of BitLocker drives showing as RAW after the October updates](https://learn.microsoft.com/en-us/answers/questions/6046419/windows-11-october-2026-updates-bitlocker-drives-b)
5. [IT Connect on the October update and the 23H2 end of updates](https://www.it-connect.tech/windows-11-kb5127648-what-you-need-to-know-about-the-october-2026-update/)

</div>
