---
title: "How to audit and block FTP and SFTP uploads with Endpoint DLP"
date: 2026-10-20
author: Mahesh
type: How to
description: "Endpoint DLP can now see and stop sensitive files leaving Windows devices over FTP and SFTP. This covers device readiness, the policy settings, evidence collection, testing in Activity explorer and moving from audit to block."
tags: [Purview, Windows 11, Defender]
---

FTP and SFTP have always been the hole in an Endpoint DLP design. You could block USB, printing, browser uploads and network shares, and a user with WinSCP open could still push a spreadsheet of customer data to any server they liked. That gap is now closed. Endpoint DLP support for FTP and SFTP transfers on managed Windows devices is generally available, with the roadmap item marked as rolling out on 5 October 2026 and the Learn how to page published on 16 October 2026.

It is not on by default. Existing policies do nothing about FTP until you tick the new activity in a rule. Below is how I would put it in, starting in audit and only blocking once the data in Activity explorer says it is safe.

## Before you start

**Licensing.** Endpoint DLP licensing has not changed for this feature. Check the Purview service description for the plan you hold, the Learn pages for the feature do not name a separate SKU.

**Roles.** To create and deploy the policy you need to be in one of the Compliance administrator, Compliance data administrator, Information Protection, Information Protection Admin or Security administrator role groups. To read Activity explorer you need Information Protection Admin, Analyst or Investigator, or the Compliance Administrator, Security Administrator or Security Reader role groups. Device onboarding settings only honour Entra roles, so use Security admin or Compliance admin there.

**Devices.** Windows 10 22H2 or Windows 11 21H2 through 24H2 on x64, or Windows 11 on ARM64. Devices must be Entra joined, hybrid joined or registered and onboarded to Purview. If they are already in Defender for Endpoint and device monitoring is on in Purview, they are onboarded.

**Antimalware client.** Version 4.18.2110 or later, with real time protection and behaviour monitoring on. Versions older than N minus 2 are not supported. `MpDlpService.exe` must be allowed through any firewall, third party antivirus or application control you run.

**A test server.** You need an FTP or SFTP server you control, and a test file containing data that matches a sensitive information type, such as a few dummy credit card numbers.

## Confirm the devices are ready

1. In the Purview portal open device onboarding.
<span class="path">Settings > Device onboarding > Devices</span>
2. Select a pilot device and read **Configuration status** and **Policy sync status** in the details pane. Both should say **Updated**. **Not updated** means the device has settings it has not applied yet. **Not available** means the OS is too old, it was only just onboarded, or no Endpoint DLP policy exists yet.
3. On the device itself, confirm the antimalware client version in PowerShell.

```powershell
Get-MpComputerStatus | Select-Object AMProductVersion, RealTimeProtectionEnabled, BehaviorMonitorEnabled
```

A good result shows a version of 4.18.2110 or higher and `True` for both protection values. If behaviour monitoring is off, Endpoint DLP will not enforce anything.

4. For a fleet view, run this in advanced hunting in the Defender portal.

```kql
DeviceInfo
| where DlpInfo != ""
| project Timestamp, DeviceName, DlpInfo
```

Devices that return rows are reporting DLP state. A pilot device missing from the output has a problem to fix before you go any further.

## Turn on evidence collection (optional)

FTP and SFTP transfers support full file evidence, which is useful when the business asks to see what was actually sent.

5. Open the endpoint DLP settings.
<span class="path">Settings > Data Loss Prevention > Endpoint DLP settings</span>
6. Expand **Setup evidence collection for file activities on devices** and set the toggle to **On**.
7. Set **Set evidence cache on device** to **7**, **30** or **60** days. This is how long the device holds a copy if it cannot upload straight away.
8. Under **Select a storage type** choose **Microsoft managed store**, or choose **Customer managed store**, select **+ Add storage** and enter a name and a URL in the form `https://storageAccountName.blob.core.windows.net/containerName`. A customer storage account must allow public network access from all networks, because private endpoints and IP restrictions are not supported.

Evidence is capped at 500 MB per file and is not collected for files on network shares.

## Create the policy in audit mode

9. Start a new policy.
<span class="path">Data loss prevention > Policies > Create policy</span>
10. Choose the **Custom** category and the **Custom policy** template, give it a clear name such as `Endpoint FTP SFTP audit`, and select **Next** until you reach the locations page.
11. On **Locations** select **Devices** only. Select **Edit** next to it and scope to your pilot users or device group. Leave every other location off so the rule stays easy to read.
12. On the policy settings page choose **Create or customize advanced DLP rules** and select **Create rule**.
13. Under **Conditions** add **Content contains** and pick the sensitive information types or sensitivity labels you want to protect. For the test, a single type such as **Credit Card Number** is enough.
14. Under **Actions** select **Add an action** and choose **Audit or restrict activities on devices**.
15. In **File activities for all apps** choose **Apply restrictions to specific activity**, tick **FTP and SFTP transfers** and set it to **Audit only**.
16. If you collect evidence, also tick **Collect original file as evidence for all selected file activities on Endpoint**.
17. Leave user notifications off for now, save the rule, then on the policy mode page choose to turn the policy on and select **Submit**. The policy appears in the policy list, and the devices pick it up on their next policy sync.

## Verify it worked

18. On a pilot device, check that **Policy sync status** for the device shows **Updated** again on the device onboarding page. Allow up to two hours for the status to refresh.
19. Upload the test file to your FTP or SFTP server with the client your users actually use. The transfer succeeds, since the rule only audits.
20. Open Activity explorer directly at `https://purview.microsoft.com/informationprotection/dataclassification/activityexplorer`. Set the **Activity** filter to **File transfer by FTP/SFTP**. You should see an event with the user, the device, the file name, the policy that matched and the action, which will be audit. If you turned on evidence, the event links to the stored file.

Activity explorer holds 30 days of data, so run the pilot in audit for at least two weeks and look at who is genuinely using FTP. Expect developers, finance teams sending files to banks, and a few line of business apps you did not know about.

## Move to block

21. Edit the rule and change **FTP and SFTP transfers** from **Audit only** to **Block with override** for the pilot. This lets a user continue with a business justification, which gives you a record of legitimate use without stopping work.
22. Under **User notifications** turn on policy tips so blocked users see a Windows notification explaining why the transfer was stopped.
23. Repeat the test upload. The client should fail the transfer and a DLP notification should appear on the device. In Activity explorer the event now shows the restrictive action.
24. Once you have reviewed overrides for a few weeks, change the action to **Block** for groups that have no business reason to use FTP, and widen the scope in stages.

If you prefer to stay in audit, you can leave the setting there indefinitely and use the data for alerting.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| No FTP events in Activity explorer | Policy not synced, or the rule does not tick FTP and SFTP transfers | Check **Policy sync status** for the device and open the rule to confirm the activity is selected |
| Device shows **Not available** | Old OS, new onboarding or no Endpoint DLP policy | Wait for onboarding to finish and confirm a device scoped policy exists |
| Device shows **Not updated** for hours | Device offline or policy failed to apply | Bring it online, wait two hours, then run the Defender client analyzer and raise a case with Microsoft |
| Nothing enforces at all | Behaviour monitoring or real time protection off | Turn both on in your antivirus policy and confirm with `Get-MpComputerStatus` |
| Transfer allowed even though set to block | Content did not match the condition | Check the file really matches the sensitive information type and confidence level you chose |
| Evidence missing for some events | File on a network share, over 500 MB, or a less restrictive rule matched | Expected behaviour, evidence is only kept by the most restrictive rule that collects it |
| `MpDlpService.exe` blocked | Application control or third party antivirus | Add an allow rule for the service |

One thing people get wrong is testing with a file that only just matches a sensitive information type. A single fake card number often falls below the confidence level the rule asks for, so the test passes silently and someone decides the feature does not work. Put a handful of realistic test values in the file and the event shows up first time.

<div class="refs" markdown="1">

**References**

1. [Protect FTP and SFTP transfers with Endpoint DLP](https://learn.microsoft.com/en-us/purview/endpoint-dlp-ftp-sftp-short)
2. [What's new in Microsoft Purview](https://learn.microsoft.com/en-us/purview/whats-new)
3. [Message Center MC1404319 on Endpoint DLP support for FTP and SFTP](https://mc.merill.net/message/MC1404319)
4. [Get started with device onboarding in Purview](https://learn.microsoft.com/en-us/purview/device-onboarding-overview)
5. [Create and deploy a DLP policy](https://learn.microsoft.com/en-us/purview/dlp-create-deploy-policy)
6. [Collect files that match DLP policies from devices](https://learn.microsoft.com/en-us/purview/dlp-copy-matched-items-get-started)
7. [Get started with Activity explorer](https://learn.microsoft.com/en-us/purview/data-classification-activity-explorer)
8. [Troubleshoot Endpoint DLP policy sync](https://learn.microsoft.com/en-us/purview/dlp-edlp-tshoot-sync)

</div>
