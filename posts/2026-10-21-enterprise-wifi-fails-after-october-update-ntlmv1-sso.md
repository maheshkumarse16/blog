---
title: "Enterprise WiFi stopped connecting after the October update? Here is the cause and the Intune fix"
date: 2026-10-21
author: Mahesh
type: Workaround
description: "After KB5127648, WiFi, wired 802.1X and VPN connections that use PEAP with MSCHAPv2 stop signing in automatically on Windows 11. Why it happens, how to confirm it, and how to roll out Microsoft's temporary workaround with an Intune remediation."
tags: [Windows 11, Intune, Entra ID]
---

Over the last few days my LinkedIn feed has filled up with EUC engineers saying the same thing. The October update went out, and the next morning laptops would not join the corporate WiFi. Home networks were fine. The office WPA2 Enterprise network was not. A few people said uninstalling `KB5127648` brought WiFi back, which is the last thing you want to do this month with an exploited zero day in that update.

So I spent some time digging into it. The short version is that this is not a random bug. It is a planned security change that Microsoft announced over a year ago, and it finally switched on by default with the October update. Once you know that, the fix is straightforward, and you can push it to the right devices with Intune in about fifteen minutes.

## What is actually happening

Windows 11 24H2 and later removed the NTLMv1 protocol, but NTLMv1 derived cryptography is still used inside MSCHAPv2. That matters because a lot of enterprise WiFi, wired 802.1X and VPN setups still use `PEAP-MSCHAPv2` or `EAP-MSCHAPv2` with single sign on, where Windows reuses the signed in user's credentials to connect.

Microsoft has been phasing this out through a registry value called `BlockNtlmv1SSO`.

* **0 means Audit mode.** Single sign on still works and Windows logs a warning.
* **1 means Enforce mode.** Windows blocks the NTLMv1 derived credentials and logs an error.

Since late August 2025, Windows 11 24H2 and later has been running in Audit mode. With updates released on or after 13 October 2026, the default changed. **If the value is not set, Windows now behaves as if it is 1.** The update does not create the value, it just changes what happens when it is missing.

Microsoft's Message Center post MC1508562 describes this as a planned hardening change, not a known issue. That is why you will not find it on the release health page for `KB5127648`.

## Who is affected

* Windows 11 24H2, 25H2 and 26H2, and Windows Server 2025
* Devices where **Credential Guard is turned off**
* Networks and VPNs that use MSCHAPv2 based authentication with single sign on, typically domain joined or hybrid joined machines

Devices with Credential Guard turned on are not affected by this change, because Credential Guard was already blocking this behaviour. If your MSCHAPv2 WiFi worked on those machines, it was not using single sign on.

## Who does not need to worry

A lot of people read "PEAP" in the reports and assume every PEAP network is broken. That is not quite right. The problem is MSCHAPv2, the password based method that usually runs inside PEAP. PEAP is only the tunnel around it. You can stop worrying if any of these describe your setup.

* **Your WiFi uses certificates.** `EAP-TLS` and `PEAP-TLS` authenticate the device or user with a certificate, not a password, so this change does not touch them. If you already push WiFi profiles with SCEP, PKCS or Cloud PKI certificates from Intune, you are fine.
* **Your devices have Credential Guard running.** Credential Guard was already blocking this kind of single sign on, so the October update changes nothing for those devices.
* **Users type their password every time.** The block only applies to single sign on, where Windows reuses the signed in credentials. Manual entry still works, although Windows will no longer save the credentials.
* **You use WPA2 or WPA3 Personal.** A shared passphrase does not use MSCHAPv2.
* **The device is not on Windows 11 24H2 or later.** Microsoft lists Windows 11 24H2, 25H2 and 26H2 and Windows Server 2025. Macs, iPhones and Android devices are not affected either, because this is a Windows change.
* **Someone already set the value.** If `BlockNtlmv1SSO` was already configured on your devices before the update, the October default does not apply to them.

If you are not sure which method your network uses, open the WiFi profile in Intune and check the EAP type and the authentication method, or ask your network team what the RADIUS server accepts. "MSCHAPv2" or "secured password" anywhere in that answer means you are in scope.

## Symptoms

* The device does not connect to the corporate WiFi or wired 802.1X network automatically after the October update.
* Users can still connect if they type their credentials in manually, but Windows will not save them for next time.
* MSCHAPv2 based VPN profiles that relied on single sign on behave the same way.
* WPA2 Personal and certificate based networks such as EAP TLS keep working.

## Before you start

* **Confirm the device is affected before you change anything.** Use the event check in step 1. This is a security control, so you only want to relax it where you have to.
* **Licences for Remediations.** Users need Windows Enterprise E3 or E5 (included in Microsoft 365 F3, E3 or E5), Windows Education A3 or A5, or Windows VDA per user. Devices must be Entra joined or hybrid joined and enrolled in Intune, or comanaged.
* **Role.** You need rights to create and assign script packages in Intune.
* **A device group** containing only the machines that need the exception, for example `Devices NTLMv1 SSO Exception`.
* **No restart is needed.** Microsoft states the registry change takes effect without one.
* **Do not uninstall KB5127648.** It fixes `CVE-2026-96951`, which is being exploited. Removing the whole update to fix WiFi is the wrong trade.

## Step 1. Confirm the cause on an affected device

1. On a laptop that will not connect, open PowerShell as administrator.
2. Look for NTLM events 4024 and 4025 in the NTLM operational log.

```powershell
Get-WinEvent -LogName 'Microsoft-Windows-NTLM/Operational' -FilterXPath "*[System[(EventID=4024 or EventID=4025)]]" -MaxEvents 20 |
    Format-Table TimeCreated, Id, LevelDisplayName -AutoSize
```

3. Read the result.
   * **Event 4025, Error.** The message says an attempt to use NTLMv1 derived credentials for single sign on was blocked by policy. This is the issue.
   * **Event 4024, Warning.** The device is in Audit mode and single sign on is still allowed. Something else is wrong with the WiFi.
   * **No events.** The connection is not using MSCHAPv2 single sign on, so look elsewhere, starting with the `Microsoft-Windows-WLAN-AutoConfig/Operational` log.

4. Check the current registry value and Credential Guard status.

```powershell
Get-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Lsa\MSV1_0' -Name BlockNtlmv1SSO -ErrorAction SilentlyContinue
(Get-CimInstance -ClassName Win32_DeviceGuard -Namespace root\Microsoft\Windows\DeviceGuard).SecurityServicesRunning
```

   No output from the first command means the value is not set, so the device is in Enforce mode after the October update. If the second command does not include `1`, Credential Guard is not running, which matches the affected profile.

## Step 2. Build the Intune remediation

Save these two scripts as `.ps1` files with `UTF-8` encoding.

**Detection script** (`Detect-BlockNtlmv1SSO.ps1`)

```powershell
$path  = 'HKLM:\SYSTEM\CurrentControlSet\Control\Lsa\MSV1_0'
$value = (Get-ItemProperty -Path $path -Name 'BlockNtlmv1SSO' -ErrorAction SilentlyContinue).BlockNtlmv1SSO

if ($value -eq 0) {
    Write-Output "BlockNtlmv1SSO is 0 (Audit mode)"
    exit 0
}

Write-Output "BlockNtlmv1SSO is '$value' (Enforce mode or not set)"
exit 1
```

**Remediation script** (`Remediate-BlockNtlmv1SSO.ps1`)

```powershell
$path = 'HKLM:\SYSTEM\CurrentControlSet\Control\Lsa\MSV1_0'

if (-not (Test-Path $path)) {
    New-Item -Path $path -Force | Out-Null
}

New-ItemProperty -Path $path -Name 'BlockNtlmv1SSO' -PropertyType DWord -Value 0 -Force | Out-Null
Write-Output "BlockNtlmv1SSO set to 0 (Audit mode)"
exit 0
```

An exit code of 1 from the detection script tells Intune the issue is present, so it runs the remediation. Any other exit code means no action.

5. In the Intune admin center, open the remediations area.

<span class="path">Devices > Manage devices > Scripts and remediations</span>

6. Select **Create script package**.
7. On **Basics**, set **Name** to something clear like `WiFi NTLMv1 SSO Audit mode exception` and add a description that links to your change record.
8. On **Settings**, upload the detection script as the **Detection script file** and the remediation script as the **Remediation script file**.
9. Set `Run this script using the logged-on credentials` to **No**. The script writes to `HKLM`, so it must run as SYSTEM.
10. Set **Enforce script signature check** to **No** unless you sign your scripts, and leave `Run script in 64-bit PowerShell` at **No**. The `HKLM\SYSTEM` hive is not redirected for 32 bit processes, so it makes no difference here.
11. Select **Next**, add scope tags if you use them, then on **Assignments** add your exception device group.
12. Set the schedule to **Hourly** with a value of 1 for the first day so devices pick it up quickly, then change it to **Daily** once the affected devices are back online.
13. Review and create.

## Step 3. Keep the exception scoped

14. Only add devices you have confirmed in step 1, or whole groups that you know connect to an MSCHAPv2 network. Do not assign this to All devices.
15. Record the exception with an end date. Microsoft describes Audit mode as "a scoped, temporary security exception" because it lowers the protection that Enforce mode gives.

## Verify it worked

* In Intune, go back to **Devices > Manage devices > Scripts and remediations**, open the package and select **Device status**. Affected devices should show that the issue was found and fixed, and the output column shows `BlockNtlmv1SSO set to 0`.
* On a device, rerun the registry check from step 1. It should now return `BlockNtlmv1SSO : 0`.
* Ask the user to disconnect and reconnect to the corporate network. It should join without asking for credentials.
* Rerun the event check. New entries should be **4024** warnings, not 4025 errors. That confirms single sign on is working in Audit mode.

## Roll back

When you are ready to go back to the secure default, which should be once your WiFi and VPN use certificates:

1. Edit the remediation script to set the value to `1` instead of `0`, and update the detection script to check for `1`, or
2. Remove the assignment and deploy a one off script that deletes the value, since a missing value now means Enforce mode.

```powershell
Remove-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Lsa\MSV1_0' -Name 'BlockNtlmv1SSO' -ErrorAction SilentlyContinue
```

After the change, event 4025 should reappear on any device that still tries MSCHAPv2 single sign on. That gives you a list of what is left to migrate.

## The real fix

The registry value buys time. The long term answer from Microsoft is to move WiFi and VPN from MSCHAPv2 to certificate based authentication, `EAP-TLS` or `PEAP-TLS`, and to turn on Credential Guard where the hardware supports it. In Intune, Credential Guard is a Settings catalog policy under the **Device Guard** category, setting **Credential Guard**, with the options **Enabled with UEFI lock** or **Enabled without lock**. Pick the second one if you want to be able to switch it off remotely.

Be aware that turning on Credential Guard also stops MSCHAPv2 single sign on, so do it together with the certificate migration, not before.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| Remediation shows as run but WiFi still fails | The device logs no 4024 or 4025 events, so it is a different problem | Check the WLAN AutoConfig operational log and the RADIUS server logs |
| Detection keeps reporting the issue after remediation | Another policy or script sets the value back to 1 | Search your scripts and baselines for `BlockNtlmv1SSO` and remove the conflict |
| Script package never runs on a device | Licence or join state does not meet the Remediations prerequisites | Confirm the user licence and that the device is Entra joined or hybrid joined |
| Users connect manually but credentials are not saved | Device is still in Enforce mode | Confirm the device is in the exception group and has synced |
| VPN still prompts after WiFi is fixed | VPN profile uses a different authentication method | Check the VPN profile's EAP settings, the same registry value covers MSCHAPv2 based VPN too |
| Devices with Credential Guard on still cannot use MSCHAPv2 single sign on | Credential Guard blocks it regardless of this value | Move those devices to certificate based authentication |

What surprised me most when reading through this is how long the warning has been there. Event 4024 has been logging on Windows 11 24H2 devices since late August 2025, telling anyone who looked exactly which connections would break. If you collect that event centrally, it is worth adding to your dashboards now, because the next round of NTLM hardening will not be the last.

<div class="refs" markdown="1">

**References**

1. [Microsoft Support KB5066470 on the NTLMv1 changes in Windows 11 24H2 and Windows Server 2025](https://support.microsoft.com/help/5066470)
2. [Message Center MC1508562 on NTLMv1 hardening and network connections](https://mc.merill.net/message/MC1508562)
3. [Windows Report on KB5127648 and WPA2 Enterprise PEAP authentication](https://windowsreport.com/?p=1512387)
4. [Borncity on Microsoft confirming 802.1X failures in company networks](https://borncity.com/news/windows-updates-microsoft-bestaetigt-wpa-802-1x-ausfaelle-in-firmennetzen/)
5. [Microsoft Learn on Remediations in Intune](https://learn.microsoft.com/en-us/intune/intune-service/fundamentals/remediations)
6. [Microsoft Learn on configuring Credential Guard](https://learn.microsoft.com/en-us/windows/security/identity-protection/credential-guard/configure)

</div>
