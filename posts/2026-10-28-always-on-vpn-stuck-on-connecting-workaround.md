---
title: "Always On VPN stuck on Connecting after the September 2026 updates: the workaround while Microsoft works on the fix"
date: 2026-10-28
author: Mahesh
type: Workaround
description: "Always On VPN connections hang on Connecting or report that the port is already in use after the September 2026 security updates. Microsoft has not shipped a permanent fix yet. This guide covers how to confirm the problem, switch the VPN profile away from automatic protocol selection, verify the change and roll it out safely."
tags: [Windows 11, Intune]
---

A few friends asked me about this one this week, so I thought it was worth writing up for everyone. The symptom is simple to describe and frustrating to live with. An Always On VPN connection hangs on Connecting. The first attempt fails, and every attempt after that either hangs again or reports that the specified port is already in use. The user can see the network, but the tunnel never comes up, so internal sites and file shares stop working.

This is not a one off. The issue affects Windows 11 24H2 and later after the September 2026 security updates. Microsoft tracks it in its release health dashboard under the issue reference WI1482218. The reports I checked say Microsoft first marked it as resolved on 13 October 2026, then changed the status back to Mitigated. That means a permanent fix is still being worked on, and there is no confirmed date for it.

Until that fix ships, you can avoid the problem. The workaround is to stop the VPN profile from choosing its protocol automatically, and to set it to one protocol that your VPN gateway supports. This post covers how to confirm the problem, make the change, check it and roll it out safely.

## What is happening

An Always On VPN profile can be set to choose between IKEv2 and SSTP automatically. The bug affects profiles that use automatic protocol selection or fallback. After one failed attempt, later attempts can hang in the Connecting state, or fail with the port already in use message.

The workaround described in the report I checked is to disable automatic protocol selection in the affected profiles, and to use either SSTP or IKEv2 exclusively, based on your network and security requirements. This is a configuration change, not a registry hack, so it can be reversed cleanly.

## Who is affected

You are in scope if all of the following are true.

* The device runs Windows 11 24H2, 25H2, 26H1 or 26H2.
* The device has the September 2026 security updates installed.
* The Always On VPN profile is set to automatic protocol selection, or to a fallback that moves between IKEv2 and SSTP.

If your profile already uses one fixed protocol, you may not see this bug, but it is still worth checking, because the profile can be set to automatic by default.

## Before you start

* **Know your gateway.** Confirm with your network or firewall team whether the VPN gateway supports IKEv2, SSTP, or both. Choose the protocol your organisation already uses and has tested. Do not pick one at random, because a protocol the gateway does not support will fail in a different way.
* **Admin access.** You need the rights to edit the Always On VPN profile in Intune, or in your Group Policy or XML tooling, and local admin on a test device.
* **A test device.** Pick one device that shows the problem and is on a network where you can reach internal resources.
* **Install the latest update.** Reports say the October cumulative update, KB5127648, or a later one fixes other VPN related problems. It does not fix this bug, but install it first so you are testing on the newest base.

## The steps, in order

1. **Confirm the symptom.** On the test device, try to connect. Look for a connection that stays on Connecting, or for the message "The specified port is already in use" after a failed attempt. If the first attempt connects and later ones fail, that matches the pattern in the reports.

2. **Confirm the update level.** Run the following command on the test device and note the installed updates.

```powershell
Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 5
```

   You should see the September 2026 security update in the list, and ideally KB5127648 or later after you install it.

3. **Check the issue status.** Open Microsoft's release health dashboard and search for WI1482218. Note the current status, because it tells you whether the fix is still pending.

4. **Find where the profile is defined.** Work out whether your Always On VPN profile is set in an Intune configuration profile, in a Settings catalog policy, or in a ProfileXML file. Each one changes the setting in a different place, so start by finding the one that applies to your devices.

5. **Pilot the change on the test device first.** Do not change the production profile yet. Make a copy of the current profile, or note its settings, so you can put it back if needed.

6. **Change the connection type in Intune.** Open the VPN configuration profile and find the setting for the connection type. If it is set to Automatic, change it to the single protocol your gateway supports, either IKEv2 or SSTP. Save the profile and sync the test device.

7. **Change the ProfileXML if you use it.** Find the element `<NativeProtocolType>Automatic</NativeProtocolType>`. For IKEv2, change it to `<NativeProtocolType>IKEv2</NativeProtocolType>`. For SSTP on a User Tunnel, use `<NativeProtocolType>SSTP</NativeProtocolType>`. Test on the device before you deploy the XML more widely.

8. **Use PowerShell for a User Tunnel if you need to test quickly.** Run PowerShell as administrator on the test device, using the profile name as it appears on the device.

```powershell
Set-VpnConnection -Name "Your VPN Profile Name" -TunnelType Ikev2
```

   Use `-TunnelType Sstp` if your gateway uses SSTP. This command changes the local profile on the device only, so it is for testing, not for fleet wide use.

9. **Verify the protocol.** Run the following command and check the tunnel type.

```powershell
Get-VpnConnection -Name "Your VPN Profile Name"
```

   The output should show `TunnelType` as `Ikev2` or `Sstp`, not `Automatic`. If it still shows Automatic, the change did not apply, so check the sync or the profile assignment.

10. **Test the connection several times.** Disconnect and reconnect at least five times, then wait a few minutes and try again. The bug shows up after a failed attempt, so repeated attempts matter more than a single success. Check that internal sites and shares work after each connect.

11. **Roll out in rings.** Assign the changed profile to a pilot group of users first. Watch the helpdesk tickets for a few days, then widen the assignment to the full group. Keep the old profile available until the rollout is complete.

## Verify it worked

* **Protocol.** The VPN connection query shows the single protocol you chose, not Automatic.
* **Connection.** The VPN connects on the first attempt and on repeated attempts, and internal resources are reachable.
* **Error.** The message "The specified port is already in use" no longer appears after a failed attempt.
* **Fleet.** The number of VPN tickets for hanging connections falls, and new tickets are checked against the steps above before anyone reinstalls the client.

## Roll back

Keep the old profile ready. If the change causes problems, set the connection type back to Automatic on the profile and sync the devices. Only do this if the gateway needs the old behaviour, because the bug will return.

Once Microsoft ships the permanent fix and the release notes say it is resolved, test the fix on a pilot device with the profile still set to a single protocol. If the connection stays reliable, you can change the profile back to Automatic, but keep the test record so you know why it was changed.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| The VPN still hangs after the change | The profile has not synced, or another profile is still applying | Check the assignment and sync the device, then run the VPN connection query again |
| The VPN will not connect with the chosen protocol | The gateway does not support that protocol | Confirm the gateway protocol with your network team and switch to the other one |
| The port already in use message remains | A stale connection is still active | Disconnect, restart the device, then try again |
| The PowerShell change reverts after a sync | Intune is still setting the profile | Change the profile in Intune, not only on the device |
| The command shows a tunnel type that is not Automatic but still fails | The problem is elsewhere, such as DNS, certificates or the gateway | Check the gateway logs and client certificates before changing the profile again |

The bug is in the client, but the fix in the profile is simple. Most of the time is spent confirming which protocol your gateway uses, so start there.

<div class="refs" markdown="1">

**References**

1. [Windows report on Microsoft admitting KB5127648 did not fix the Always On VPN bug, with the workaround](https://windowsreport.com/microsoft-admits-windows-11-kb5127648-didnt-fix-vpn-bug-shares-workaround/)
2. [WinTips on Always On VPN stuck on Connecting after the KB5124008 update](https://www.wintips.org/always-on-vpn-stuck-on-connecting-after-kb5124008-update-how-to-fix/)
3. [Windows forum on KB5127648 fixing VPN, AVD and storage issues](https://windowsforum.com/news/windows-11-kb5127648-october-2026-update-fixes-vpn-avd-and-storage-issues.448177/)
4. [Microsoft Windows release health dashboard for Windows 11, version 25H2](https://learn.microsoft.com/en-us/windows/release-health/status-windows-11-25h2)

</div>
