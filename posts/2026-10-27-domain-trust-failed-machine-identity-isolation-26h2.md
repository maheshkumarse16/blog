---
title: "Domain trust relationship failed after the September 2026 updates: Machine Identity Isolation and how to fix it"
date: 2026-10-27
author: Mahesh
type: Fix
description: "Domain joined Windows 11 devices lost their secure trust relationship with the domain after the September 2026 updates. Users could not sign in with valid domain credentials. The cause is the Machine Identity Isolation feature, and this guide covers how to confirm it, check your domain functional level, disable the feature and repair the secure channel."
tags: [Windows 11, Entra ID]
---

A few friends in the industry ran into the same problem this month, and I helped them work through it. The symptom is easy to recognise once you have seen it. A user types their correct domain password on a domain joined Windows 11 laptop and gets a message saying the trust relationship between the device and the domain failed. Their password is right and the account is fine. The machine itself has lost its secure channel to the domain. Offline sign in with cached credentials may still work, which is why it can look like a random fault.

The cause is a feature called **Machine Identity Isolation**, which the September 2026 updates turned on. Microsoft has a release health entry for it, and this post follows that entry closely. I have added the checks I used with my friends, including how to check your domain before you change anything.

## What is happening

Microsoft's description is that some Credential Guard protected machine accounts might be unable to sign in interactively with valid domain credentials. Users then receive a message that the trust relationship between the device and the domain failed.

The updates enable Machine Identity Isolation. Microsoft documents the feature as supported only in environments connected to domain controllers at a **Windows Server 2025 domain functional level (DFL) or above**. Devices that have the feature enabled but are not connected to Windows Server 2025 domain controllers will hit this issue, and Microsoft's guidance is to disable the feature on those devices.

The timeline from Microsoft's entry:

| Date | What happened |
|---|---|
| 8 September 2026 | KB5124008 introduced the change on Windows 11 24H2, 25H2 and 26H2 |
| 14 September 2026 | The out of band update KB5129195 carried the same change |
| 16 September 2026 | The issue was opened on the release health dashboard |
| 22 September 2026 | KB5124010 resolved it by disabling Machine Identity Isolation enforcement completely |

The affected client versions are 24H2, 25H2, 26H1 and 26H2. Microsoft lists no server platforms.

## Who is affected

You are in scope if all of the following are true.

* The device is Windows 11 client on 24H2, 25H2, 26H1 or 26H2.
* The device is domain joined and uses Credential Guard protected machine accounts.
* The device has Machine Identity Isolation enabled, either by the September update or by a policy or registry value.
* The domain controllers the device talks to are not all at a Windows Server 2025 domain functional level.

If your domain is already at Windows Server 2025 DFL, the feature can stay on and you should not see this issue. Check before you make changes, because the right fix depends on your domain.

## Before you start

* **Admin access.** You need local admin on the affected device, and rights to reset a computer account in the domain.
* **Active Directory module.** Install the RSAT Active Directory tools on a management machine so you can read the domain level.
* **Management access.** Make sure you can change Group Policy or Intune, because whichever method turned the feature on is the one you need to change.
* **Network path.** The device must reach a domain controller, either on the corporate network or through VPN.
* **Confirm the symptom.** Ask the user for the exact message. The one you are looking for is the trust relationship failure, not a wrong password message. Also ask whether they can sign in with cached credentials while offline. If they can, the local session is intact and the secure channel is the problem.

Do not reset the user's password first. A password reset will not fix a broken secure channel.

## The fix, step by step

1. **Check the build and the KB.** Open PowerShell on the affected device and confirm the version.

```powershell
(Get-ComputerInfo).OsDisplayVersion
(Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion').UBR
```

   Compare the result with the builds in Microsoft's entry. Devices on the September updates before KB5124010 are the ones that can hit this. Devices on KB5124010 or a later cumulative update have enforcement prevented, so the problem should not recur there. If you are on a newer build and still see the symptom, continue with the steps below, because an older setting may still be present.

2. **Check the domain functional level.** From a machine with the Active Directory PowerShell module, check the domain mode and the domain controller operating systems.

```powershell
Import-Module ActiveDirectory
Get-ADDomain | Select-Object Name, DomainMode
Get-ADDomainController -Filter * | Select-Object Name, OperatingSystem
```

   `DomainMode` must be `Windows2025Domain` for Machine Identity Isolation to be supported. If it is lower, or any domain controller the device can reach runs an older operating system, treat the feature as unsupported in that location. A single older domain controller in a site can be enough to cause the problem for devices that authenticate there.

3. **Check the Machine Identity Isolation values.** The feature can be controlled from two registry locations. Check both.

```powershell
Get-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Lsa' -Name MachineIdentityIsolation -ErrorAction SilentlyContinue
Get-ItemProperty -Path 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\DeviceGuard\MachineIdentityIsolation' -ErrorAction SilentlyContinue
```

   Microsoft's workaround says that when `MachineIdentityIsolation` equals `2`, you should set it to `0`. A value of `2` means the feature is set to enforce. If both locations are missing, check for a Known Issue Rollback setting or a policy in Intune and Group Policy that you have not found yet.

4. **Pick your method.** Microsoft gives two supported options, and both are reversible.
   * **Known Issue Rollback Group Policy.** This is the cleaner option for a fleet. Microsoft's entry names the policy **KB5124008 260915_17123 Known Issue Rollback**, under Computer Configuration, Administrative Templates, for Windows 11 versions 24H2 and 25H2. Set it to **Disabled**, as Microsoft describes, and restart the device.
   * **Registry value.** Set `MachineIdentityIsolation` to `0` in both locations from step 3, then restart. Use this for a single device, or when you cannot deploy the policy yet.

   Use the same management method that enabled the feature. If it was set through Intune, change it in Intune, otherwise the next sync will set it back.

5. **Apply the change and restart.** Make the change from a local admin session or through your management tool. Do not change it through a remote session that depends on the broken trust, because you may lock yourself out. After the restart, rerun the registry check from step 3. It should show `0`, or the value should be absent if your policy removes it.

6. **Repair the secure channel.** Disabling the feature alone does not repair a trust that has already broken. Sign in with cached credentials on the device, open PowerShell as administrator and run the following.

```powershell
Test-ComputerSecureChannel -Repair -Credential (Get-Credential)
```

   Enter an account with rights to reset a computer account in the domain. The command returns `True` when the repair works. If it returns `False`, the device is not reaching a domain controller, so check VPN, DNS and the network path, then run it again.

7. **Check the trust from the device.** Replace `<yourdomain>` with the domain's DNS name and run both commands.

```powershell
nltest /sc_query:<yourdomain>
nltest /sc_verify:<yourdomain>
```

   Both should report success. If `sc_verify` fails, repeat step 6 and check the time on the device, because a large time difference can break Kerberos and trust checks.

8. **Test an interactive sign in.** Lock the device, then sign in with the user's domain credentials while connected to the corporate network or VPN, so the sign in goes through a domain controller and not the cache. Repeat this on a few devices from different sites, because each site may use different domain controllers.

9. **Roll out in stages.** Apply the Known Issue Rollback or the registry change to a pilot group first. Check those devices over one or two days, then widen the scope.

10. **Track the helpdesk tickets.** Count the devices that show the trust message. After the fix, the count should drop to zero, and any new ticket should be checked against the steps above before anyone resets a password.

11. **Decide the long term setting.** Machine Identity Isolation is a valid security feature, and it should be used once it is properly supported in your environment. The key requirement is the Windows Server 2025 domain functional level. Do not turn it on again until every domain controller in the path is at that level, and test it on a pilot group first.

## Verify it worked

* **Registry.** Both locations from step 3 show `0`, or the value is absent.
* **Secure channel.** `Test-ComputerSecureChannel` returns `True`, and `nltest /sc_verify` reports success.
* **Sign in.** A user can sign in interactively with valid domain credentials, on the corporate network and over VPN.
* **Fleet.** The helpdesk ticket count for the trust message falls to zero, and no new devices show the message after the next sync cycle.

## Roll back

Keep the Known Issue Rollback policy or the registry change in place until every device is on a build where enforcement is prevented. Only then decide whether to remove them.

If you later enable Machine Identity Isolation on purpose, do it only after every domain controller the device can reach is at Windows Server 2025 DFL. To go back, use the same method you used to disable it and restart the device. If the trust breaks again, repeat step 6 from cached credentials.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| Trust message after the fix | The secure channel was not repaired | Run `Test-ComputerSecureChannel -Repair` again from cached credentials |
| `Test-ComputerSecureChannel` returns False | The device cannot reach a domain controller | Check VPN, DNS and network path, then retry |
| Registry value keeps returning to `2` | An Intune or Group Policy assignment is setting it | Find and change the policy, otherwise the value is set again at the next sync |
| Problem persists on a current build | Older domain controllers in the site | Check every domain controller the device can reach, not only the nearest one |
| `nltest` reports a failure | Clock skew or a stale machine password | Check time sync, then repair the secure channel |

## What I took from helping the others

The first instinct for most people was a password problem, and a password reset does nothing for a broken secure channel. Once the domain functional level and the registry value were checked, the cause was clear.

If you see this in your estate, check the domain first. The Windows side is quick to fix. Finding out why the feature was enabled in a domain that does not support it takes longer, so start there.

<div class="refs" markdown="1">

**References**

1. [Microsoft release health: Domain-joined devices might lose their secure trust relationship with the domain (Windows 11, version 25H2)](https://learn.microsoft.com/en-us/windows/release-health/status-windows-11-25h2)
2. [Microsoft release health: Windows 11, version 26H2 known issues and notifications](https://learn.microsoft.com/en-us/windows/release-health/status-windows-11-26h2)
3. [Microsoft release health: Resolved issues in Windows 11, version 26H2](https://learn.microsoft.com/en-us/windows/release-health/resolved-issues-windows-11-26h2)
4. [KB5124010 quick reference from Admin365 Blog](https://admin365.blog/2026/09/23/kb5124010-quick-reference-whats-new-whats-fixed-and-known-issues/)
5. [Microsoft support article for KB5124010](https://support.microsoft.com/help/5124010)

</div>
