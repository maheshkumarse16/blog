---
title: "Old Windows Update group policies still fighting your Intune update rings? How to make Windows ignore them"
date: 2026-11-09
author: Mahesh
type: How to
description: "Windows 11 now has a policy that tells Windows Update to skip the Group Policy source completely, so old WSUS and deferral GPOs stop overriding Intune. This step by step guide covers what IgnoreWindowsUpdateGroupPolicies does, how to deploy it from Intune, how to prove it is working and how to back it out."
tags: [Intune, Windows 11]
---

If you run a hybrid estate, you have almost certainly seen this. Intune update rings are assigned, the policy shows as succeeded, and yet the device still behaves as if it is pointed at WSUS, or it keeps a deferral that nobody remembers setting. Somewhere in the domain there is an old Windows Update GPO, and Windows is still reading it.

The usual answer used to be the **MDM wins over GP** setting. The problem is that it never worked for Windows Update. Microsoft documents that `ControlPolicyConflict`, the policy behind MDM wins over GP, does not apply to the Update Policy CSP. So for update settings there was no clean way to tell Windows to listen to Intune and ignore the GPO, short of unlinking the GPO or cleaning up the registry with scripts.

That has changed. Windows 11 now has a policy called `IgnoreWindowsUpdateGroupPolicies`. Instead of picking a winner when Intune and Group Policy disagree, it tells Windows Update to skip the Group Policy source completely. This post covers how it works, how to deploy it safely and how to prove it is doing what you expect.

## What the setting does

The policy lives in the Update Policy CSP.

| Item | Value |
|---|---|
| OMA URI | `./Device/Vendor/MSFT/Policy/Config/Update/IgnoreWindowsUpdateGroupPolicies` |
| Data type | Integer |
| Scope | Device |
| Values | `1` turns the bypass on. `0`, or no value at all, leaves normal Group Policy reading in place |

When the value is `1`, Windows Update stops reading the Group Policy locations, which are `HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate` and its `AU` subkey, along with the Group Policy cache. Only the settings delivered through MDM count.

There are a few things it does **not** do, and they matter.

* It does not unlink or delete the GPO, remove the registry keys or stop `gpupdate`. The GPO still applies to the device. Windows Update simply stops listening to it.
* It does not fall back to the Group Policy value when Intune does not set something. If your GPO set a value that Intune does not, that value is no longer in effect once the bypass is on.
* It does not move a device to any particular update source by itself. It only removes Group Policy from consideration.
* A script that writes to the same Windows Update policy keys is treated the same as a real GPO, so it is ignored too.

## Before you start

* **Supported builds.** Support starts with Windows 11 24H2 with KB5101684, build 26100.8973, released in July 2026. Check the Update Policy CSP page for the full list of supported versions before you target anything older.
* **Know what your GPOs set today.** Run `gpresult /h gp.html` on a typical device, or open the GPOs in Group Policy Management, and write down every Windows Update setting they configure. Pay particular attention to WSUS server settings, deferral periods, active hours and restart behaviour.
* **Make sure Intune covers the same ground.** Every setting from the GPO that you still need must exist in an Intune update ring or Settings catalog policy, because the GPO value stops counting once the bypass is on.
* **ConfigMgr co management.** If ConfigMgr still owns the Windows Update workload on some devices, leave those devices out of scope until the workload has moved to Intune.
* **A pilot group.** A handful of devices from different sites and builds, with users who will tell you quickly if updates stop arriving.

## The steps, in order

1. **Record the current state on a pilot device.** Before you change anything, capture the Windows Update policy keys so you have something to compare against later.

```powershell
Get-ItemProperty 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate' -ErrorAction SilentlyContinue
Get-ItemProperty 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU' -ErrorAction SilentlyContinue
```

   If you see values such as `WUServer`, `WUStatusServer` or `UseWUServer`, the device is being pointed at WSUS by Group Policy.

2. **Check which update service the device uses today.** Run this to see the update services registered on the device and which one is the default.

```powershell
(New-Object -ComObject Microsoft.Update.ServiceManager).Services |
    Select-Object Name, IsDefaultAUService
```

   Keep the output. You will run the same check after the change.

3. **Confirm the Intune update ring is complete.** Open the update ring assigned to the pilot group and check that it covers everything you recorded in the Before you start section. Add anything missing now, not after the bypass is on.

<span class="path">Devices > Windows > Windows updates > Update rings</span>

4. **Look for the setting in the Settings catalog.** Create a new Settings catalog profile for Windows and search for **Ignore Windows Update Group Policies**. If the catalog shows it, add it, set it to enabled and move on to step 6.

<span class="path">Devices > Windows > Configuration > Create > New policy > Settings catalog</span>

5. **Use a custom profile if the setting is not in the catalog yet.** Create a new Windows configuration profile using the **Custom** template and add one OMA URI row with the values from the table above, data type Integer and value `1`.

6. **Name and describe the profile clearly.** Something like `WU Ignore legacy GPO` with a description that says what it does and links to your change record. Six months from now someone will wonder why updates ignore the domain.

7. **Assign it to the pilot group only.** Do not assign it to all devices. Leave the GPO linked for now, because it still protects devices that are not in the pilot.

8. **Sync the pilot devices.** Trigger a sync from the Intune admin center or from **Settings > Accounts > Access work or school** on the device, then give it a few minutes.

9. **Check the policy has been delivered.** On a pilot device, read the value that Intune wrote.

```powershell
$path = 'HKLM:\SOFTWARE\Microsoft\PolicyManager\current\device\Update'
(Get-ItemProperty -Path $path -Name IgnoreWindowsUpdateGroupPolicies -ErrorAction SilentlyContinue).IgnoreWindowsUpdateGroupPolicies
```

   A result of `1` means the policy arrived. You can also look in Event Viewer under **Applications and Services Logs > Microsoft > Windows > DeviceManagement Enterprise Diagnostics Provider > Admin** for the event that records the setting.

10. **Run a controlled update scan.** Delivery is not the same as behaviour. Open **Settings > Windows Update**, select **Check for updates**, and confirm the device scans and offers what your Intune ring says it should. Then repeat the service check from step 2 and compare.

11. **Watch the pilot for a full cycle.** Leave the pilot running through at least one monthly security update. Check the Windows update reports in Intune and make sure the pilot devices install the update within the deadline set in the ring.

12. **Widen the assignment.** Once the pilot is clean, add the next ring of devices, then the rest of the estate in stages.

13. **Clean up the old GPOs.** This setting is meant as a migration tool, not a permanent home for a forgotten GPO. Once every device in a GPO's scope is covered by the bypass and behaving correctly, unlink the Windows Update GPO and remove it.

## Verify it worked

* **Delivery.** The PolicyManager value from step 9 is `1` on every device in scope.
* **Behaviour.** A manual scan offers the updates your Intune ring allows, and devices install the monthly security update within the ring's deadline.
* **Reports.** The Windows update reports in Intune show the pilot devices as current, with no growing list of devices stuck on old builds.
* **No surprises.** Users are not seeing restart prompts at odd times, which would point to an active hours or restart setting that the GPO used to set and Intune does not.

Treat delivery, stored state and real update behaviour as three separate checks. The registry value only proves the policy arrived.

## Roll back

If something goes wrong, remove the device from the assignment or set the value to `0`. Windows Update starts reading the Group Policy locations again, and the legacy values count once more. Because the bypass never deletes the GPO or its registry values, nothing needs to be rebuilt. Sync the device and run a scan to confirm it is back on its old behaviour.

Do not unlink the GPO until you are sure you will not need this rollback path.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| The PolicyManager value is missing | The profile has not synced, or the device is not in the assigned group | Check the assignment and the profile status in Intune, then sync |
| The device stops getting updates after the change | The GPO pointed at WSUS or set a value that Intune does not cover | Compare the GPO settings from step 1 with the Intune ring and add the missing settings |
| Restart behaviour changes | Active hours or restart settings came from the GPO | Add those settings to the Intune update ring |
| The setting has no effect | The device build is older than the supported build | Check the build against the Update Policy CSP and update the device first |
| A script keeps writing WSUS values | The script writes to the Group Policy keys | Those values are ignored while the bypass is on, but remove the script so it does not confuse the next person |

The setting itself is a single value. The real work is making sure Intune already covers everything the old GPO was doing, so spend most of your time on the before and after checks.

<div class="refs" markdown="1">

**References**

1. [Microsoft Learn Update Policy CSP](https://learn.microsoft.com/en-us/windows/client-management/mdm/policy-csp-update)
2. [Patch My PC on how Intune bypasses Windows Update Group Policy](https://patchmypc.com/blog/ignore-windows-update-group-policy-intune/)
3. [Admin365 Blog on IgnoreWindowsUpdateGroupPolicies](https://admin365.blog/2026/10/04/ignorewindowsupdategrouppolicies-make-intune-override-update-gpo/)
4. [Call4Cloud on Intune bypassing Windows Update Group Policy](https://call4cloud.nl/intune-can-now-bypass-windows-update-group-policy/)
5. [Andrew Taylor Intune newsletter, 6 November 2026](https://andrewstaylor.com/2026/11/06/intune-newsletter-6th-november-2026/)

</div>
