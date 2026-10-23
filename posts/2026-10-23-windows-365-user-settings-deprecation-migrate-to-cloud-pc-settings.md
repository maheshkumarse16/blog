---
title: "Windows 365 User settings are going away: what changes, when, and how to migrate before January 2027"
date: 2026-10-23
author: Mahesh
type: How to
description: "Microsoft is retiring Windows 365 User settings in Intune. Existing policies will not migrate on their own, and from January 2027 they stop applying, which takes local admin and point in time restore with them. A step by step guide to inventory, recreate and validate everything in the new Cloud PC settings."
tags: [Cloud PC, Intune]
---

We have been working through this change in our own environment over the last couple of weeks, and it is one of those Microsoft retirements that looks small in the Message Center but can quietly break things if nobody owns it. So I wanted to write up what we found and the order we did it in, in case it saves someone else the head scratching.

## What is changing

Windows 365 **User settings** is being retired. It is the policy type in Intune that most of us have used for years to do three things on Cloud PCs.

* Make users local administrators on their Cloud PC
* Set how often restore points are taken and let users restore their own Cloud PC
* Control disaster recovery options

Microsoft is replacing it with a single **Cloud PC Settings** framework in Intune. The old capabilities are split across two new profile types, **Cloud PC Configuration** and **Windows App settings**.

The important part is in Message Center post MC1418556. **Existing User settings policies will not be migrated automatically.** You have to recreate them yourself.

## Why Microsoft is doing it

Microsoft's reason is consolidation. Windows 365 settings were spread across several separate experiences, and the new framework brings them into one place so they are managed the same way and scale better. In practice it also lines Cloud PC settings up with how the rest of Intune works, rather than being a special case.

## When

The timeline was revised on 3 September 2026. The current dates are:

| When | What happens |
|---|---|
| October 2026 | You can no longer create new User settings policies. The tab shows as **User settings (legacy)** and is greyed out. You can still edit existing ones. |
| November 2026 | Existing User settings policies become read only. |
| January 2027 | User settings are fully retired. Existing policies stop applying to anyone. |

If you are reading this in late October, the first stage has already happened. From November you will not even be able to tweak an old policy, so the sensible window to do this work is now.

## What breaks if you do nothing

After January 2027, any Cloud PC that relied on a User settings policy will lose what it gave them.

* Users who were local admins on their Cloud PC through User settings lose those rights.
* Point in time restore stops behaving the way you configured it, and users lose the ability to restore their own Cloud PC.
* Disaster recovery settings defined there no longer apply.

Microsoft lists it as a breaking change. The admin impact is high, even though most users will not notice until something they rely on is missing.

## Before you start

* **Role.** You need an Intune role that can manage Windows 365, such as Intune Administrator or Windows 365 Administrator.
* **Access to Microsoft Graph PowerShell** if you want to export the old policies rather than copying them by hand. The read only scope `CloudPC.Read.All` is enough.
* **A list of the groups** each policy is assigned to. These are user groups.
* **A test user with a Cloud PC** in a group you can assign on its own.
* **Know the conflict rule.** If a user is in more than one User settings policy, Intune uses the **most recently created** policy and ignores the rest. The last modified date does not count. Keep this in mind when you compare old and new behaviour.
* **Windows 365 Flex Cloud PCs in Shared mode** never used User settings, so they are not part of this work.

## Step 1. Inventory every User settings policy

1. In the Intune admin center, open the existing policies.

<span class="path">Devices > Cloud PC Settings</span>

2. Open each policy on the **User settings (legacy)** tab and write down its name, its assigned groups and these three values.
   * **Enable local admin**
   * **Allow user to initiate restore service**
   * `Frequency of restore-point service`
3. If you have more than a handful, export them with Graph instead. This lists every policy with its assignments.

```powershell
Connect-MgGraph -Scopes "CloudPC.Read.All"

$uri = "https://graph.microsoft.com/v1.0/deviceManagement/virtualEndpoint/userSettings?`$expand=assignments"
$settings = (Invoke-MgGraphRequest -Method GET -Uri $uri).value

$settings | ForEach-Object {
    [pscustomobject]@{
        Name          = $_.displayName
        Created       = $_.createdDateTime
        LocalAdmin    = $_.localAdminEnabled
        UserReset     = $_.resetEnabled
        RestorePoints = ($_.restorePointSetting | ConvertTo-Json -Compress)
        Groups        = ($_.assignments.target.groupId -join ", ")
    }
} | Export-Csv .\W365UserSettings.csv -NoTypeInformation
```

   A good result is a CSV with one row per policy. `LocalAdmin` and `UserReset` show `True` or `False`, and `RestorePoints` shows the frequency and whether user restore is allowed. If the file is empty, check that you signed in with an account that can read Windows 365 settings.

4. Sort the list by the **Created** column. Where a user is in more than one policy, the newest one is the one actually in effect today. That is the behaviour you need to reproduce, not the older policies.

## Step 2. Decide what each setting becomes

Before you build anything, map each value to its new home. We found it easiest to agree this with the team first so nobody recreated things twice.

5. **User self service actions go to Windows App settings.** This profile has the options **Enable Users to Reset their Cloud PC** and **Allow Users to Initiate a Restore**. When they are off, only IT can reset or restore.
6. **Cloud PC level settings go to Cloud PC Configuration.** That covers local admin, restore point frequency and disaster recovery, which Microsoft lists as moving into Cloud PC Settings.
7. Take the opportunity to tidy up. If you have several old policies that only differ slightly, this is a good moment to cut them down to two or three clear profiles with no overlapping groups.

## Step 3. Create the new profiles

8. Open the new settings area.

<span class="path">Devices > Windows 365 > Settings > Create</span>

9. Choose **Cloud PC Configuration** and recreate the local admin, restore point frequency and disaster recovery values from your inventory. Both new profile types are marked preview at the time of writing, so the field names may not match the old ones word for word. Match on meaning, not on label.
10. Assign it to the same groups as the old policy it replaces. Check on the assignment page whether the profile targets users or devices, and pick the matching groups. Do not assume it works the same way as the old user based policy.
11. Go back to **Create**, choose **Windows App settings**, and set **Enable Users to Reset their Cloud PC** and **Allow Users to Initiate a Restore** to match the old values.
12. Assign it the same way.

## Step 4. Pilot before you touch the old policies

13. Assign the new profiles to your test group first, not to production groups.
14. Ask the test user to **sign out and sign back in** to the Cloud PC. Local admin rights in particular only change at sign in.
15. Run the checks in the next section. Only when the pilot looks right, add the production groups to the new profiles.
16. Leave the old User settings policies in place until you have confirmed the new ones on real users. They become read only in November, but they keep applying until January, so they are a safety net for now.

## Verify it worked

* **Local admin.** On the test Cloud PC, open PowerShell and check the local Administrators group.

```powershell
Get-LocalGroupMember -Group "Administrators" | Select-Object Name, PrincipalSource
```

   If local admin is meant to be on, the user's account should appear in the list. If it is meant to be off, it should not.

* **Restore points.** In the Intune admin center, open the Cloud PC and check that restore points are being created at the interval you set. Remember there is a limit of 10 restore points, so a shorter interval gives you a shorter history.
* **User restore and reset.** In Windows App, the test user should see the restore and reset options only if you enabled them.
* **No surprises for other users.** Pick one user from each production group and repeat the local admin check after they have signed in again.

## Retire the old policies

17. Once every group is covered by the new profiles and verified, remove the assignments from the old User settings policies, then delete them.

<span class="path">Devices > Cloud PC Settings</span>

   Select the menu on the policy row, choose **Delete**, then **Yes**.

18. Update your build documentation, runbooks and service desk articles that mention User settings.
19. Brief the service desk that local admin and restore now come from different profiles, so they look in the right place when a ticket comes in.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| User lost local admin after you changed profiles | User has not signed out since the change, or is in a group the new profile does not cover | Ask them to sign out and in, then check group membership against the profile assignment |
| User has local admin you did not expect | They are still in an old User settings policy, and the newest created one wins | Check every old policy they are in and remove the assignment |
| Restore option missing in Windows App | **Allow Users to Initiate a Restore** is off in the Windows App settings profile, or the user is not in its assigned group | Check the profile value and assignment |
| Restore history shorter than expected | Restore point interval is short and only 10 points are kept | Increase the interval |
| Graph export returns nothing | Account lacks permission to read Windows 365 settings | Sign in with a Windows 365 or Intune administrator and consent to `CloudPC.Read.All` |
| Custom script that adds users to Administrators stops working | Turning local admin off in a profile removes those rights | Move the script's logic into the profile, or exclude those users |

The part that caught us out was the conflict rule. A few users were in two old policies, and the one in effect was not the one anyone expected, because it was simply the newest. Sorting the export by created date before rebuilding anything saved us from copying the wrong values into the new profiles.

<div class="refs" markdown="1">

**References**

1. [Message Center MC1418556 on Windows 365 User settings moving to the new settings framework](https://www.itelio.com/en/microsoft-message-center/mc1418556)
2. [Summary of MC1418556 with the admin actions](https://pupuweb.com/mc1418556-windows-365-user-settings-transition-to-the-new-settings-framework/)
3. [Microsoft Learn on making users local admins on Cloud PCs](https://learn.microsoft.com/en-us/windows-365/enterprise/assign-users-as-local-admin)
4. [Microsoft Learn on configuring point in time restore](https://learn.microsoft.com/en-us/windows-365/enterprise/restore-configure)
5. [Microsoft Graph reference for cloudPcUserSetting](https://learn.microsoft.com/en-us/graph/api/resources/cloudpcusersetting)
6. [Anoop C Nair on the new Cloud PC Configuration and Windows App settings](https://www.anoopcnair.com/cloud-pc-configurations-and-windows-app-intune/)

</div>
