---
title: "Defender Antivirus platform 4.18.26090.9 renames a PowerShell property your scripts may read"
date: 2026-10-20
author: Mahesh
type: What's new
description: "What changed in the 12 October 2026 Defender Antivirus platform and engine release, which scripts and reports can break, and how to stage the build through update channels and confirm it landed."
tags: [Defender, Intune]
---

Microsoft released Defender Antivirus platform 4.18.26090.9 and engine 1.1.26090.9 on 12 October 2026, together with security intelligence 1.461.1.0. The release notes file it under September 2026, which is why it is easy to miss when you skim the page. Most of the changes are quiet fixes. One of them is a rename that can break compliance scripts, and another fixes a bug that may explain odd ASR behaviour you have been chasing.

## What is in the release

The Learn release notes list these changes for 4.18.26090.9.

1. The protection engine now refreshes itself when the licence tier resolved on the device changes.
2. A stalled security intelligence update worker that could block every later update is fixed.
3. An update configuration issue that could leave `DisableBmNetworkSensor` set to 1 after a platform update is fixed.
4. The configuration protection property in PowerShell is renamed from `ControlledConfigurationState` to `ConfigurationProtection`.
5. The feature control cache is now kept through signature updates.
6. Path normalisation for attack surface reduction rules is improved.
7. ASR exclusions are no longer dropped when several policies target the same rule.

No known issues are listed against this build.

## Who should care

If you run a script, a proactive remediation or a compliance check that reads `ControlledConfigurationState` from `Get-MpComputerStatus`, that check needs attention. Configuration protection is still a preview feature, so most estates will not have it, but anyone piloting it probably wrote a detection script against the old property name. The Learn article on configuration protection still tells you to check `ControlledConfigurationState`, so the docs and the platform disagree for now. I would make detection scripts tolerate both names until the docs catch up.

The ASR fix matters to anyone with layered policies. If you assign one ASR profile to all devices and a second profile with extra exclusions to a smaller group, and those exclusions seemed to vanish on some machines, this is the likely cause.

## Stage the build before it reaches everyone

Platform and engine updates follow the gradual rollout channels. Beta gets builds first, Current Channel (Preview) next, then the broad population scales from 10% to 100%. To check this build on a pilot group before it lands everywhere, put those devices on the Preview channel.

**Intune.** Create or edit a Settings Catalog profile and add the Defender settings below.
<span class="path">Devices > Configuration > Create > New policy > Windows 10 and later > Settings catalog</span>
Search the picker for Defender and set **Platform Updates Channel** and **Engine Updates Channel** to **Current Channel (Preview)** for the pilot group. Leave **Security Intelligence Updates Channel** alone, since it only offers staged and broad options.

**Group Policy.** The settings sit in this location.
<span class="path">Computer Configuration > Administrative Templates > Windows Components > Microsoft Defender Antivirus</span>
Use **Select the channel for Microsoft Defender monthly platform updates** and **Select the channel for Microsoft Defender monthly engine updates**. They write `PlatformRing` and `EngineRing` under `HKLM\SOFTWARE\Policies\Microsoft\Windows Defender`.

**PowerShell on a test machine.**

```powershell
Set-MpPreference -PlatformUpdatesChannel Preview
Set-MpPreference -EngineUpdatesChannel Preview
Get-MpPreference | Select-Object PlatformUpdatesChannel, EngineUpdatesChannel, DefinitionUpdatesChannel, DisableGradualRelease
```

The last command should show `Preview` for the first two values.

## Confirm the build and fix your scripts

Check the versions on a device with this.

```powershell
Get-MpComputerStatus | Select-Object AMProductVersion, AMEngineVersion, AntivirusSignatureVersion
```

A device on the new build reports `4.18.26090.9` for `AMProductVersion` and `1.1.26090.9` for `AMEngineVersion`. Anything lower has not taken the update yet.

To see which configuration protection property a device exposes, list the property names rather than assuming one.

```powershell
$s = Get-MpComputerStatus
$s.PSObject.Properties.Name | Where-Object { $_ -match 'Config' }
```

On the new platform expect `ConfigurationProtection`. On older builds you will see `ControlledConfigurationState`. A detection script that reads whichever one exists will survive the mixed period while the rollout completes.

For the ASR side, check the exclusions the device actually holds after the update.

```powershell
(Get-MpPreference).AttackSurfaceReductionOnlyExclusions
```

Then watch the Defender operational log for blocks against paths you excluded. The log is at **Applications and Services Logs > Microsoft > Windows > Windows Defender > Operational**. Event ID 1121 is a block, 1122 is an audit hit and 5007 records a settings change. At fleet level this query shows whether ASR events drop on the pilot after the update.

```kql
DeviceEvents
| where Timestamp > ago(7d)
| where ActionType startswith "Asr"
| summarize EventCount = count() by ActionType, bin(Timestamp, 1d)
```

If you were seeing blocks for paths that one of your policies excludes, the daily count of ASR action types ending in `Blocked` for those devices should fall once they run 4.18.26090.9.

## A note on configuration protection

If you are piloting configuration protection, remember what it needs. Devices must be onboarded, managed by Intune or Defender security settings management, and running platform 4.18.26060.3004 or later. It is not supported on comanaged devices or in GCC High, and it is set in the Windows Security Experience profile under Endpoint security with the **Configuration protection (Device)** setting. Turning it on turns tamper protection off unless another policy sets it, which drops your tamper protection Secure Score item. That catches people out more than the property rename.

My take is that this is a routine platform build with one sharp edge. Find every script that names `ControlledConfigurationState` today, and you will save yourself a confusing compliance report next month.

<div class="refs" markdown="1">

**References**

1. [Defender for Endpoint release notes with platform 4.18.26090.9](https://learn.microsoft.com/en-us/defender-endpoint/microsoft-defender-endpoint-releases)
2. [Configuration protection for Defender Antivirus](https://learn.microsoft.com/en-us/defender-endpoint/secure-controlled-configuration)
3. [Manage how and where Defender Antivirus receives updates](https://learn.microsoft.com/en-us/defender-endpoint/configure-updates)
4. [Enable attack surface reduction rules and exclusions](https://learn.microsoft.com/en-us/defender-endpoint/attack-surface-reduction-rules-configure)
5. [ASR events in the Windows event log](https://learn.microsoft.com/en-us/defender-endpoint/attack-surface-reduction-windows-events)
6. [Monitor attack surface reduction rules with advanced hunting](https://learn.microsoft.com/en-us/defender-endpoint/attack-surface-reduction-rules-monitor)

</div>
