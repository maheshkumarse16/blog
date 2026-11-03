---
title: "Always On VPN stuck on Connecting after the September 2026 updates: now fixed in KB5127936, plus the workaround until you install it"
date: 2026-10-28
author: Mahesh
type: Workaround
description: "Always On VPN connections hang on Connecting or report that the port is already in use after the September 2026 security updates. Microsoft has now fixed it in the October preview update KB5127936, and the fix will reach everyone with the November security update. This guide covers how to confirm the problem and get the fix, and the workaround of switching the VPN profile away from automatic protocol selection until you can install it."
tags: [Windows 11, Intune]
---

> **Update, 4 November 2026.** Microsoft has now fixed this. The October optional preview update, KB5127936, released on 28 October 2026 for Windows 11 25H2 and 26H2, includes the fix. Microsoft's note says the update "fixes an issue that affects Always On VPN connections after installing September security update", where connections using automatic protocol selection or protocol fallback could stay stuck in Connecting or fail after a first failed attempt. If you do not deploy preview updates, the fix comes with the November security update on 10 November 2026. If you run another Windows 11 version, check the notes for its October preview update. Until the fix is on your devices, the workaround below still applies, and you can remove it once the fix is installed and tested.

A few friends asked me about this one this week, so I thought it was worth writing up for everyone. The symptom is simple to describe and frustrating to live with. An Always On VPN connection hangs on Connecting. The first attempt fails, and every attempt after that either hangs again or reports that the specified port is already in use. The user can see the network, but the tunnel never comes up, so internal sites and file shares stop working.

This is not a one off. The issue affects Windows 11 24H2 and later after the September 2026 security updates. Microsoft first marked it as resolved in the October security update, KB5127648, then confirmed that update had not fixed it. The real fix arrived in the October preview update, KB5127936, as described in the update above.

Until you install the fix, you can avoid the problem. The workaround is to stop the VPN profile from choosing its protocol automatically, and to set it to one protocol that your VPN gateway supports. This post covers how to confirm the problem, make the change, check it and roll it out safely.

## What is happening

An Always On VPN profile can be set to choose between IKEv2 and SSTP automatically. The bug affects profiles that use automatic protocol selection or fallback. After one failed attempt, later attempts can hang in the Connecting state, or fail with the port already in use message.

The workaround Microsoft describes is to change the affected profiles from automatic protocol selection to a single protocol, either SSTP only or IKEv2 only. Microsoft says organisations should select the protocol based on their environment, security and deployment requirements. This is a configuration change, not a registry hack, so it can be reversed cleanly.

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
* **Install the fix if you can.** KB5127936, or the November security update once it ships, contains the fix. If you can install it on the affected devices, do that first and test. Use the workaround steps below only for devices that cannot take the update yet.

## The steps, in order

1. **Confirm the symptom.** On the test device, try to connect. Look for a connection that stays on Connecting, or for the message "The specified port is already in use" after a failed attempt. If the first attempt connects and later ones fail, that matches the pattern in the reports.

2. **Confirm the update level.** Run the following command on the test device and note the installed updates.

```powershell
Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 5
```

   You should see the September 2026 security update in the list, and ideally KB5127648 or later after you install it.

3. **Check whether the fix is installed.** Look for KB5127936, or the November security update, in the list from step 2. If it is there, test the connection before you change the profile, because you may not need the workaround at all. If it is not there, continue with the steps below.

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

Once KB5127936 or the November security update is installed, test the fix on a pilot device with the profile still set to a single protocol. If the connection stays reliable, you can change the profile back to Automatic, but keep the test record so you know why it was changed.

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
5. [Microsoft support article for KB5127936, the October 2026 preview update](https://support.microsoft.com/en-us/servicing/os/windows-11/2026/10/kb5127936-windows-11-25h2-26h2-update)
6. [BleepingComputer on Microsoft fixing the VPN issues caused by the September updates](https://bleepingcomputer.com/news/microsoft/microsoft-finally-fixes-vpn-issues-caused-by-september-updates)

</div>
