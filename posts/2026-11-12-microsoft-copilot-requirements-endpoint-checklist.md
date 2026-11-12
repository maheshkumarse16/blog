---
title: "Microsoft Copilot requirements explained: an endpoint and network checklist before you assign licences"
date: 2026-11-12
author: Mahesh
type: How to
description: "Microsoft has refreshed its Copilot requirements page, and Microsoft 365 Copilot is now simply Microsoft Copilot. A practical walk through of every requirement from the endpoint side, covering licences, mailboxes, Windows and Edge versions, the Office Feature Updates task, the cloud.microsoft domain, WebSockets, browser cookies and Safe Links, with the checks to run before users complain."
tags: [Copilot, Microsoft 365, Intune, Windows 11, Entra ID]
---

Most Copilot rollouts I hear about go the same way. Licences are assigned, an announcement goes out, and then the tickets start. Copilot is missing in Word on some laptops. The chat pane spins forever behind the proxy. Links in answers say "Unable to verify link". None of these are Copilot bugs. They are requirements that nobody checked on the endpoint or the network.

Microsoft refreshed its **Microsoft Copilot requirements** page on 5 November 2026, and it is worth reading closely, because it is the clearest list so far of what has to be in place. This post walks through it from the endpoint engineer's side, with the checks I would run before a single licence is assigned.

## First, the new names

Microsoft has renamed the products. **Microsoft 365 Copilot is now Microsoft Copilot**, and **Microsoft 365 Copilot Chat is now Microsoft Copilot Chat**. The main address is moving to `copilot.cloud.microsoft`. You will still see the old names in older documentation and in some admin center screens for a while, so expect both.

The difference between the two still matters.

| Requirement | Microsoft Copilot | Microsoft Copilot Chat |
|---|---|---|
| Eligible Microsoft 365 subscription | Required | Required |
| Microsoft Copilot licence | Required for licensed features | Not required for eligible users |
| Entra ID work or school account | Required | Required |
| Exchange Online mailbox | Required for mailbox based features | Only for features that use mailbox data |
| Supported OS, apps, browser and network | Required | Required |
| Secure and governed foundation | Recommended | Recommended |

## Before you start

* **Roles.** The **AI Administrator** role gives access to Copilot and AI administration without Global Administrator. Use it for the people running the rollout.
* **Intune reporting.** You need to be able to report on OS versions and run scripts or remediations on Windows devices.
* **Network contacts.** You will need whoever owns the proxy, firewall and TLS inspection rules. Most of the hard problems are on the network, not the device.
* **A pilot group.** Pick users on different device models, sites and connection types, including some who work over VPN.

## The checks, in order

1. **Check licensing for the pilot users.** Every user needs an eligible Microsoft 365 subscription, and licensed Copilot needs the Copilot licence on top. Run the **Copilot License Details** diagnostic at `aka.ms/CopilotLicenseDetails` against a few pilot users to confirm. One catch to note: Copilot is **not available with device based licensing for Microsoft 365 Apps for enterprise**, so shared device and kiosk style setups using device licences are out.

2. **Confirm identity and mailboxes.** Users must have a work or school account in Entra ID. For anything that uses mail, calendar or meetings, the **primary mailbox must be in Exchange Online**. Copilot can also use archive, shared and delegate mailboxes the user can access, but it **is not available in group mailboxes**. If you still have on premises mailboxes in a hybrid setup, those users will get a reduced experience.

3. **Check operating system versions in Intune.** The minimums are Windows 11 22H2 or later, macOS 13 Ventura or later, iOS and iPadOS 16 or later, and Android 10 or later. Filter your device list by OS version and export anything below these. Anything still on Windows 10 is out of scope for Copilot on that device.

<span class="path">Devices > All devices</span>

4. **Check the Edge Update version on Windows.** Microsoft states that **EdgeUpdate must be version 1.3.253.25 or later**. This is the updater, not the browser itself, and it is easy to miss on devices where Edge updates are controlled. Check it on a sample device.

```powershell
(Get-Item "${env:ProgramFiles(x86)}\Microsoft\EdgeUpdate\MicrosoftEdgeUpdate.exe").VersionInfo.FileVersion
```

   If you see an older version, check whether a policy or script is blocking Edge updates. The installers come for x64 and ARM64, and you can deploy them with Intune, Configuration Manager or Group Policy.

5. **Make sure the Office Feature Updates task runs.** This one catches people out. Microsoft says the **Office Feature Updates** scheduled task must run on its normal schedule and reach the network for core Copilot features in Word, Excel, PowerPoint and OneNote. Hardening scripts and old builds sometimes disable it. Check its state and last run on a sample device.

```powershell
Get-ScheduledTask -TaskPath '\Microsoft\Office\' |
    Where-Object TaskName -like 'Office Feature Updates*' |
    ForEach-Object {
        $info = $_ | Get-ScheduledTaskInfo
        [pscustomobject]@{
            Task       = $_.TaskName
            State      = $_.State
            LastRun    = $info.LastRunTime
            LastResult = $info.LastTaskResult
        }
    }
```

   You want the tasks to show as **Ready** with a recent last run. If a task is **Disabled**, find what disabled it before you enable it again, or it will just be disabled at the next run of that script.

6. **Review the privacy controls for connected experiences.** Copilot in the desktop apps depends on connected experiences. If your Cloud Policy or Group Policy settings turn off connected experiences that analyse content, some Copilot features will not appear. Review those policies against Microsoft's privacy controls article before the pilot, and document any settings you change.

7. **Allow the whole cloud.microsoft domain.** This is the most important network change on the page. Allow `*.cloud.microsoft` on devices and on the network, and check that URL filtering, proxies, firewalls, tenant restrictions, Conditional Access and app control policies do not block `copilot.cloud.microsoft` or the Copilot app. Microsoft is explicit that it **does not support allowing only selected URLs** inside `*.cloud.microsoft`. Allow the whole domain, along with the standard worldwide Microsoft 365 URLs and IP ranges and the Copilot endpoints.

8. **Check WebSockets end to end.** Copilot needs working WebSocket connections from user devices to `*.office.com`, `*.cloud.microsoft` and `copilot.cloud.microsoft`. Microsoft lists three common causes of failure, which are blocked WebSockets, TLS inspection that interferes with the connection and aggressive proxy timeouts. If your proxy inspects TLS, talk to the network team about bypassing inspection for these destinations.

9. **Run the connectivity test from a real device.** Open `connectivity.m365.cloud.microsoft/copilot` on a pilot device, on each type of connection you support, such as office network, home broadband and VPN. Fix every failure before you widen the pilot. The general Microsoft 365 connectivity test tool is useful too.

10. **Allow the Safe Links cookies in the browser.** Links in Copilot Chat answers, including answers from agents built in Copilot Studio, are checked by **Safe Links** in Defender for Office 365. That check needs third party cookies for `*.safelinks.protection.outlook.com`. If the cookies are blocked, users see **"Unable to verify link"** and the link does not open. Add `[*.]safelinks.protection.outlook.com` to the **CookiesAllowedForUrls** policy for Edge and for Chrome. In Intune you can set this in a Settings catalog profile.

<span class="path">Devices > Windows > Configuration > Create > New policy > Settings catalog</span>

11. **Check cookies for Office on the web.** Separately, **third party cookies must be enabled** for Copilot in Word, Excel and PowerPoint for the web. If your browser baseline blocks third party cookies everywhere, add allowances for the Microsoft 365 web domains your users need.

12. **Turn on transcription or recording where it is needed.** For Copilot to use meeting content after a Teams meeting ends, transcription or recording must be enabled. For Teams Phone, VoIP calls need a Copilot licence, and PSTN calls also need Teams Phone and a calling plan. Participants receive the usual notification. Agree this with your compliance team first.

13. **Block personal accounts the right way.** If you want to stop users signing in to Copilot with personal Microsoft accounts, do not block parts of `cloud.microsoft`. Microsoft suggests **tenant restrictions** as the targeted control, which block consumer account sign in without breaking work accounts.

14. **Decide on web search and oversharing controls.** Web search lets Copilot pull results from Bing, and it can be managed by policy. Make a deliberate decision and document it. Microsoft also recommends **SharePoint Advanced Management** and **Microsoft Purview** to deal with oversharing and sensitivity labels before Copilot starts surfacing content that was never meant to be widely visible. These are not hard requirements, but skipping them is the fastest way to turn a Copilot pilot into a data exposure incident.

## Verify it worked

* **Licensing.** The licence diagnostic passes for every pilot user.
* **Devices.** Every pilot device meets the OS minimum, shows EdgeUpdate 1.3.253.25 or later and has the Office Feature Updates tasks in the Ready state with a recent run.
* **Network.** The Copilot connectivity test passes on the office network, at home and over VPN.
* **Apps.** Copilot appears in Word, Excel, PowerPoint, Outlook and Teams for pilot users, and Copilot Chat loads at `copilot.cloud.microsoft` without spinning.
* **Links.** A link in a Copilot Chat answer opens normally, with no "Unable to verify link" message.

## Roll back

Most of these changes are allowances, so they are easy to back out. Remove the cookie allowance from the Settings catalog profile, or put back the previous proxy or firewall rule, and the device returns to its old behaviour. If you re enabled the Office Feature Updates task and it causes a problem, disable it again through the same method and note the reason. For licences, removing the Copilot licence from a user takes the licensed features away without affecting the rest of Microsoft 365.

Keep a record of every allowance you add, so security reviews later can see why it is there.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| Copilot missing in Word, Excel or PowerPoint desktop | No licence, device based licensing, connected experiences off, or the Office Feature Updates task not running | Check steps 1, 5 and 6 |
| Copilot Chat spins or never loads | WebSockets blocked, TLS inspection or proxy timeouts | Run the connectivity test and review step 8 with the network team |
| "Unable to verify link" in answers | Third party cookies blocked for Safe Links | Add the Safe Links domain to CookiesAllowedForUrls |
| No mail or calendar answers | Mailbox is on premises or a group mailbox | Move the primary mailbox to Exchange Online |
| Copilot works in the office but not on VPN | The VPN path inspects or blocks `cloud.microsoft` traffic | Test over VPN and fix the tunnel or proxy rules |
| Meeting recap missing | Transcription or recording not enabled | Enable it in Teams meeting policy |

Nearly every Copilot ticket I hear about comes down to one of these. Run the checks on a pilot group first and the rollout becomes a licensing exercise rather than a troubleshooting one.

<div class="refs" markdown="1">

**References**

1. [Microsoft Learn on Microsoft Copilot requirements](https://learn.microsoft.com/en-us/copilot/plan/microsoft-copilot-requirements)
2. [Microsoft Copilot connectivity test](https://connectivity.m365.cloud.microsoft/copilot)
3. [Copilot License Details diagnostic](https://aka.ms/CopilotLicenseDetails)

</div>
