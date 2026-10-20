---
title: "How to move your Intune Windows security baseline to version 26H2 without a big bang"
date: 2026-10-20
author: Mahesh
type: How to
description: "The Windows 11 26H2 security baseline is in Intune, but existing profiles do not update themselves. A step by step way to create the new version, pilot it, swap assignments and retire the old profile safely."
tags: [Intune, Windows 11]
---

The Windows security baseline for Windows 11 version 26H2 arrived in Intune in the week of 5 October 2026. It brings new settings, some changed defaults and updated guidance, and it is now the latest Windows baseline in the admin center.

What catches people out is that nothing happens to your existing profiles. Once a newer version exists, the settings in your current profile become read only. You can still change its name, description and assignments, but to get the 26H2 settings you have to create a new version of the profile and move devices onto it.

This guide is the way I do that move so devices never sit without a baseline and you can back out in minutes.

## Before you start

* **Licence.** Security baselines need Microsoft Intune Plan 1.
* **Permissions.** Your role needs **Organization** Read and **Security baselines** Assign, Create, Delete, Read and Update. The least privileged built in role that has these is **Policy and Profile Manager**.
* **Comanaged devices.** If ConfigMgr also manages these devices, the **Device configuration** workload must be switched to Intune or the baseline will not apply.
* **Profile age.** The in place **Update Version** option works for baseline profiles created from May 2023 onwards. Older profiles have to be rebuilt, which is covered in the troubleshooting table.
* **A pilot group.** Have an Entra ID device group with a handful of real machines from different hardware models and teams. Include at least one device used for Remote Desktop and one used by a developer, because those are the people who complain first.
* **A list of your customisations.** Write down every setting you changed from the Microsoft default in the current profile and the reason. You will need it when you review the new version.
* **One known gap.** The **Configure NetBIOS settings** policy is not part of the 26H2 baseline in Intune. Microsoft says it will be added later. If you need it now, set it with a separate profile.

## Step 1. Look at what you have

1. Sign in to the Microsoft Intune admin center and open the baselines list.

    <span class="path">Endpoint security > Security baselines</span>

    The list shows each baseline type with the number of profiles using it and the **Last Published** date.

2. Select the Windows security baseline type. The **Profiles** pane opens with every profile created from that baseline.
3. Select **Versions** to see which baseline versions your profiles use. If more than one version is in use, deal with the oldest first so you do not end up with three versions fighting over the same devices.
4. Open your current profile, select **Properties** and note the **Scope tags** and **Assignments**, including every excluded group. The new version will not copy them.

## Step 2. Create the 26H2 version

1. Back on the **Profiles** pane, tick the check box next to the profile you want to move. Tick only one.
2. Select **Update Version** in the toolbar.
3. In the **Update Version** pane choose one of the two options.

    * **Accept baseline changes but keep my existing setting customizations** keeps the values you changed and applies Microsoft's new defaults everywhere else. This is what most people want.
    * **Accept baseline changes and discard existing setting customizations** throws away your changes and gives you the plain 26H2 defaults.

    The choice applies to the whole profile. You cannot keep some customisations and drop others at this point, so pick keep and fix individual settings afterwards.

4. Select **Create**. The **Upgrade Policy** workflow opens on the **Basics** tab.
5. Give it a **Name** that includes the version, for example `Windows baseline 26H2 pilot`. The name is required. The **Description** is filled in for you.
6. On **Configuration settings**, expand each group and check the values against your list of customisations. New settings arrive with their default value. Settings that are not in 26H2 are gone and will no longer be enforced.
7. On **Scope tags**, add the same tags as the original profile. The field starts empty.
8. On **Assignments**, under **Select groups to include**, add only your pilot group. Leave everything else for now.
9. On **Review + create**, select **Create**.

The new profile appears in the **Profiles** list next to the old one. The old profile is untouched. It keeps its settings, name, scope tags and assignments and carries on applying to devices.

## Step 3. Stop the two versions overlapping on the pilot

Two baseline profiles that set the same setting to different values on one device produce a conflict, and a conflicted setting is not applied.

1. Open the original profile, select **Properties**, then **Edit** next to **Assignments**.
2. Under **Select groups to exclude**, add the pilot group.
3. Select **Review + save**.

Now the pilot devices get only the 26H2 profile and everyone else stays on the old one.

## Step 4. Check the settings that changed for real devices

Before you leave the pilot alone for a week, look at the settings that usually bite.

* Anything under **Administrative Templates** for **Remote Assistance** and **Remote Desktop Services**.
* Device control settings, such as preventing installation of devices that match certain setup classes, and BitLocker write protection for removable drives, which is enabled in the 26H2 defaults.
* **Credential Guard** and virtualisation based security settings on older hardware.
* Local security options such as **Enumerate administrator accounts on elevation**.

If your organisation also uses Administrator protection, read my post on the Remote Desktop 0xC000000D problem from earlier today before the pilot goes wide.

## Verify it worked

1. Open the new profile from the **Profiles** pane. The overview shows **Device and user check in status**, plus the **Device assignment status** and **Per setting status** tiles.
2. Select **View report**. The first time, select **Generate report** to build it. Filter on **Assignment status** and select **Generate again** after a change.
3. Open **Per setting status**. Each setting shows a count of **Success**, **Error** and **Conflict**. You want zero in the last two.
4. To find the cause of a problem, go to the **Monitor** section of the profile and open `Per-setting status`, then select the number in the **Error** or **Conflict** column to see the affected devices.
5. For a single device, go to the device page and look at the profile there.

    <span class="path">Devices > All devices > select the device > Device configuration</span>

6. On the device itself, collect a diagnostic report and check the policy area.

    ```powershell
    mdmdiagnosticstool.exe -area "DeviceEnrollment;DeviceProvisioning;Autopilot" -zip "c:\users\public\documents\MDMDiagReport.zip"
    ```

    Open `MDMDiagHtmlReport.html` from the zip. The baseline policies appear in the managed policies list with their current values. A setting that shows the old value usually means the device has not checked in since you moved it.

Give it time. The report can take up to 24 hours after the first assignment and up to six hours after later changes. Do not chase a missing device after one hour.

## Step 5. Move everyone across

When the pilot has been clean for a week or so, move the rest of the estate in a couple of batches.

1. Edit the new profile's **Assignments** and add the next group under **Select groups to include**. Add the exclusions you noted in Step 1.
2. Edit the old profile's **Assignments** and add the same group under **Select groups to exclude**.
3. Repeat for each batch. On the last one, remove all include groups from the old profile.
4. Once the old profile has no groups assigned and the new one reports healthy for a few days, delete the old profile from the **Profiles** list.

If you want a quick rehearsal first, use **Duplicate** from the profile's menu to make a test copy. The copy keeps settings and scope tags but has no assignments, so it is safe to play with.

## Roll back

If the pilot breaks something, remove the pilot group from the exclusions on the old profile and from the includes on the new one. The devices go back to the old version at their next check in.

Be aware that Intune does not undo settings it stops managing. When a setting leaves a baseline, the device keeps its last value until something else sets it. Each setting comes from a CSP and each CSP handles removal its own way. If a 26H2 setting caused the problem, fix it by setting the value you want in the old profile or a separate profile, rather than by simply unassigning.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| **Update Version** is not offered for the profile | The profile was created before May 2023 in the old format | Use **Change Version**, select **Export Profile Settings** to save the old values, then create a fresh 26H2 profile and copy your customisations across by hand |
| New profile shows no devices | Scope tags and assignments are not carried over | Add the include groups and scope tags on the new profile |
| Settings show **Conflict** on pilot devices | Old and new baseline, or another profile, set the same setting | Exclude the pilot group from the old baseline and check device configuration profiles that set the same value |
| Settings show **Error** on some models | The setting is not supported on that hardware or edition | Open the device's setting details to see the error, then set that value differently for the affected group |
| You cannot edit settings in the old profile | Settings become read only once a newer version exists | Change settings in the 26H2 profile instead |
| A setting stayed after you removed the baseline | CSPs do not always revert when no longer managed | Set the desired value explicitly with another profile |
| NetBIOS policy missing from the 26H2 baseline | It is not in this baseline yet | Configure it with a separate profile until Microsoft adds it |

The step people skip is the exclusion on the old profile. Without it the pilot devices get both versions, the reports fill with conflicts and someone decides the new baseline is broken when it is really just overlapping.

<div class="refs" markdown="1">

**References**

1. [Microsoft Learn on what is new in Intune, including the 26H2 baseline](https://learn.microsoft.com/en-us/intune/whats-new/)
2. [Microsoft Learn on managing security baseline profiles and updating to a new version](https://learn.microsoft.com/en-us/intune/device-security/security-baselines/configure-baselines)
3. [Microsoft Learn on monitoring security baselines](https://learn.microsoft.com/en-us/intune/device-security/security-baselines/monitor-baselines)
4. [Microsoft Learn on the default settings in the Windows 26H2 baseline](https://learn.microsoft.com/en-us/intune/device-security/security-baselines/ref-windows-mdm-settings?pivots=mdm-26h2)
5. [Microsoft Security Baselines blog on the Windows 11 version 26H2 baseline](https://techcommunity.microsoft.com/blog/microsoft-security-baselines/windows-11-version-26h2-security-baseline/4560382)
6. [Microsoft Learn on collecting MDM diagnostic logs](https://learn.microsoft.com/en-us/windows/client-management/mdm-collect-logs)

</div>
