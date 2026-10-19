---
title: "Remote Desktop fails with 0xC000000D when Administrator protection is on"
date: 2026-10-20
author: Mahesh
type: Workaround
description: "Standard users can no longer RDP into Windows 11 devices that have Administrator protection enabled. Here is who is affected, why it is spreading, and what to do until Microsoft fixes it."
tags: [Windows 11, Intune]
---

This one is going to land on a lot of service desks over the next few weeks, so it is worth getting ahead of it.

## The symptom

A user without admin rights tries to connect to a Windows 11 device over Remote Desktop and the connection fails with error `0xC000000D`. The message says the token that was passed to the function is invalid.

Admins can still connect. Standard users cannot.

## What is affected

* **Windows versions.** Windows 11 24H2, 25H2, 26H1 and 26H2.
* **Updates.** It started with `KB5124010`, the September 2026 optional preview update, and carries on in everything after it, including the October security update `KB5127648`.
* **Devices.** Remote Desktop hosts that have Administrator protection turned on. Microsoft says it happens however the feature was enabled.

In practice that means jump boxes, shared engineering machines, lab devices and any desktop that people connect into rather than sit in front of.

## Why more people are hitting it now

Administrator protection keeps signed in admins at standard user rights and asks for Windows Hello before anything that needs elevation, such as installing an app or changing the registry. It started rolling out in October 2025.

The reason this is suddenly widespread is the security baselines. Administrator protection is turned on in the Windows 11 24H2, 25H2 and 26H2 baselines from the Microsoft Security Compliance Toolkit. If your organisation applies those baselines and has not set the policy differently, it became active with the October update. A lot of teams will not realise they turned it on.

## Is there a fix?

Not yet. Microsoft says it is working on it and has not given a date. Until then, the only option it offers is to switch Administrator protection off on the affected devices.

## What to do until Microsoft ships a fix

Switching off a security feature across the whole estate to fix Remote Desktop on a handful of machines is the wrong trade. Here is how I would handle it.

### 1. Find the devices that actually need it

Work out which devices standard users genuinely RDP into. That is usually a short list. Put them in a dedicated Entra ID group, something like `Devices RDP Hosts AdminProtection Exception`.

### 2. Create a targeted policy in Intune

In the Intune admin center, create a new Settings catalog profile for Windows 10 and later.

<span class="path">Devices > Configuration > Create > New policy > Windows 10 and later > Settings catalog</span>

Search the settings picker for **Local Policies Security Options** and find **User Account Control Type Of Admin Approval Mode**. It has two options.

* Admin Approval Mode is running in legacy mode
* Admin Approval Mode is running with Administrator protection

Set it to the legacy mode option and assign the profile to your exception group only. The change needs a restart before it takes effect.

If you set this through Group Policy instead, the same setting sits under the security options in the local policies. Reset it on the affected hosts only.

### 3. Watch for conflicts

If your baseline or another profile also sets this value, the device will report a conflict and you may not get the result you expect. Check where the baseline is assigned and exclude the exception group from it, or adjust the baseline for that group.

### 4. Record the exception and set a reminder

Write down which devices are in the group and why. When Microsoft releases the fix, take the devices out of the group so Administrator protection comes back on. Exceptions like this have a habit of becoming permanent if nobody owns them.

### 5. Tell the service desk

Give them the error code, the short list of affected hosts and the expected fix. It saves a lot of time on calls that would otherwise go round in circles checking network rules and RDP permissions.

## How to check if a device is affected

On the remote host, check the build. If it is 24H2, 25H2, 26H1 or 26H2 and has `KB5124010` or later installed, and a standard user gets `0xC000000D`, you are looking at this issue. If an admin account connects fine to the same device, that pretty much confirms it.

I will update this post once Microsoft releases the fix.

<div class="refs" markdown="1">

**References**

1. [BleepingComputer on recent Windows updates causing Remote Desktop failures](https://bleepingcomputer.com/news/security/microsoft-recent-windows-updates-may-trigger-remote-desktop-failures)
2. [Windows Report on the KB5127648 known issues](https://windowsreport.com/?p=1512407)
3. [Cloudinfra on configuring UAC settings with Intune](https://cloudinfra.net/configure-uac-user-account-control-using-intune/)

</div>
