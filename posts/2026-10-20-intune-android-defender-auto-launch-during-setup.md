---
title: "Intune can now open Defender for Endpoint during Android setup on corporate devices"
date: 2026-10-20
author: Mahesh
type: What's new
description: "A new connector toggle makes Defender for Endpoint open automatically during out of box setup on fully managed and work profile Android devices. What it needs, how to switch it on and the assignment detail that decides whether it works."
tags: [Intune, Android, Defender]
---

One of the quieter items in the Intune September service release fixes a real annoyance for anyone rolling out Defender for Endpoint on corporate Android phones. Intune can now open the Defender app automatically during out of box setup, so the user finishes the Defender onboarding as part of enrolment instead of being chased for it a week later.

It applies to corporate owned fully managed devices (COBO) and corporate owned devices with a work profile (COPE). Personally owned work profile devices are not included.

## Why this matters

On Android, Defender onboarding is driven by the app. The app installs, but until the user opens it, signs in and accepts the permissions, the device does not report to Defender and does not send a risk level to Intune. If your compliance policy requires a machine risk score, those devices sit in a non compliant or unknown state and Conditional Access starts blocking mail on day one. Getting the user to open Defender during setup closes that gap.

If the user skips or abandons the Defender step, the Intune setup step stays available so they can open Defender again from there.

## What you need first

* Intune and Defender for Endpoint licences for the users.
* The **Endpoint Security Manager** role, or a custom role with **Read** and **Modify** on **Mobile Threat Defense**.
* Managed Google Play connected to the tenant.
* The Intune connection enabled from the Defender side, so the Defender for Endpoint connector in Intune can be configured.
* The **Microsoft Defender: Antivirus** app (package `com.microsoft.scmx`) approved in Managed Google Play.

Only one Mobile Threat Defense partner in a tenant can hold the MTD role permissions on Android. If you have another MTD vendor connected with that toggle on, you have to choose.

## Turn it on

1. Open the Defender for Endpoint connector.

    <span class="path">Endpoint security > Defender for Endpoint</span>

2. Under the Android settings, turn on **Grant MTD role permissions to Microsoft Defender for Endpoint on enrolled Android COBO and COPE devices**. The auto launch option depends on this toggle and does nothing without it.
3. Turn on **Automatically launch Defender for Endpoint during setup on Android COBO and COPE devices**.
4. Select **Save**.
5. Go to the Defender app in the app list.

    <span class="path">Apps > All apps > Microsoft Defender: Antivirus > Properties > Assignments</span>

6. Under **Required**, add the user groups that enrol corporate Android devices, or **All devices**. The reason for this choice is in the next section.
7. Save the assignment and check it shows under **Required** on the app's overview page.

## The assignment detail that decides whether it works

Microsoft is clear that Defender has to be assigned to user groups or to all devices before the device enrols. A device group assignment depends on the device object existing in Entra and being added to the group, and that processing often finishes after setup has already moved on. If Defender is not installed by the time Intune reaches the launch step, there is nothing to open.

So if you normally target apps at a dynamic device group based on enrolment profile, keep doing that for everything else, but give Defender a user group or **All devices** assignment. You can narrow it with an assignment filter for corporate ownership if you do not want it on personal devices.

## What users see

During setup, Intune opens Defender on its own. The user signs in if asked and accepts the permission prompts. Microsoft recommends **Allow all the time** for location, which some users will refuse unless you tell them in advance, so put one line about it in your enrolment instructions.

When they finish, setup carries on. If they back out, the Intune setup step for Defender stays in the list so they can return to it.

## How to check it worked

1. Enrol a test COBO or COPE device from factory reset and watch Defender open during setup.
2. In the Defender portal, confirm the device appears in the device inventory after onboarding.
3. In Intune, open the device and look at the compliance status for any policy that uses the machine risk score. It should move from not evaluated to compliant once Defender reports.

If the device never shows in Defender, the usual reasons are that the app did not install in time, the user did not complete onboarding, the Intune to Defender connection is not active, or there was a sign in or permission error inside the app.

## Things to watch

This only affects devices that enrol after you turn it on. Existing devices are not prompted again, so you still need your usual chase for phones that never onboarded.

The release name in the What's new list is shorter than the toggle text in the portal. When you write it up for your service desk, use the toggle label, because that is what they will see on screen.

In my experience the thing that breaks this is the app assignment, not the toggle. Most teams target Defender at the same device group as every other app, see the launch step fail on the first few phones, and conclude the feature does not work. Change the assignment first and test again before you open a case.

<div class="refs" markdown="1">

**References**

1. [Microsoft Learn on what is new in Intune, service release 2609](https://learn.microsoft.com/en-us/intune/whats-new/)
2. [Microsoft Learn on enabling a Mobile Threat Defense connector and its Android toggles](https://learn.microsoft.com/en-us/intune/device-security/mobile-threat-defense/enable-connector)
3. [Microsoft Learn on deploying Defender for Endpoint on Android with Intune](https://learn.microsoft.com/en-us/intune/device-security/microsoft-defender/deploy-android)
4. [Microsoft Learn on configuring the Defender for Endpoint integration with Intune](https://learn.microsoft.com/en-us/intune/device-security/microsoft-defender/configure-integration)

</div>
