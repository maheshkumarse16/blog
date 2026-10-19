---
title: "Intune's new device page, bulk eSIM actions for Android and Teams calls on Managed Home Screen"
date: 2026-10-20
author: Mahesh
type: What's new
description: "A round up of the smaller Intune changes from the September service release that make day to day device support easier, especially for Android Enterprise."
tags: [Intune, Android]
---

Phased deployments got most of the attention in the latest Intune release, but a few smaller changes will make a bigger difference to people who support devices every day.

## The redesigned device page

The default device view in the Intune admin center has been rebuilt. Device details, recent activity, reports, troubleshooting tools and the remote actions now sit together on one page.

Before, checking a single device meant jumping between hardware, compliance, configuration and app blades. Now most of what a second line engineer needs on a call is in one place, and you can run remote actions such as sync or restart from the same screen.

If your support guides include screenshots of the old device blade, they will need updating.

## Bulk eSIM management for Android Enterprise

Admins can now manage eSIMs on up to 100 corporate owned Android Enterprise devices at a time. For anyone running a fleet of company phones, that is a big time saver compared with doing it one device at a time.

There is also a change in how eSIMs are treated when you delete a device record. Intune now keeps the eSIM by default instead of removing it along with the record. That is the safer default, because deleting a stale record should not cut off someone's mobile data plan. If your offboarding process relied on the old behaviour to remove the eSIM, update it to remove the eSIM as a separate step.

## Teams calls on Managed Home Screen

Frontline workers using devices locked to Managed Home Screen can now answer urgent Microsoft Teams calls before they authenticate. Security controls for protected apps still apply after the call.

This is useful for shared devices in warehouses, stores and hospitals, where a missed call because someone had to sign in first is a real problem.

## More features in government clouds

Enterprise App Management, Microsoft Cloud PKI and Remote Help are now available in more government cloud environments, including GCC. Enterprise App Management is also now available to Department of Defense customers.

## A licensing note

From 1 July 2026, Endpoint Privilege Management and Enterprise App Management are included in Microsoft 365 E5. If you are on E5 and still paying separately for these, or for the Intune Suite mainly to get them, check your next renewal carefully.

## What I would do this week

* Open a few devices in the new view and update your support guides and screenshots.
* Review your Android offboarding steps now that eSIMs are kept when a device record is deleted.
* If you run shared Android devices, test Teams call handling on Managed Home Screen with your frontline team.
* Check whether your E5 licences now cover EPM and Enterprise App Management.

<div class="refs" markdown="1">

**References**

1. [Windows Report on what Microsoft added to Intune in September 2026](https://windowsreport.com/?p=1511069)
2. [Petri on Intune phased deployments and Android changes](https://petri.com/?p=780379)
3. [IT Connect on the June 2026 Intune features and the E5 licensing change](https://www.it-connect.tech/intune-vulnerability-management-and-app-updates-june-2026s-new-features/)

</div>
