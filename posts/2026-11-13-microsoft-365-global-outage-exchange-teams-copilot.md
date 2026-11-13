---
title: "Microsoft 365 global outage: Exchange Online, Teams, SharePoint and Copilot down (MO1550821)"
date: 2026-11-13
author: Mahesh
type: Known issue
description: "A major Microsoft 365 outage that started on 12 November 2026 has hit Exchange Online, Outlook, Teams, SharePoint, Copilot and Defender XDR worldwide. What happened, what Microsoft has said, what is behind it so far, and what admins should and should not do while it is being fixed."
tags: [Microsoft 365, Copilot, Defender, Intune]
---

> **Status as of 13 November 2026, 03:00 UTC.** The outage is still ongoing. Microsoft is bringing servers back in stages and reports that this is starting to work, but it has not declared full recovery and has not given a time for it. I will update this post as Microsoft posts more.

If your users could not open their mail, join a Teams meeting or get a response from Copilot overnight, it is not your network and it is not your setup. Microsoft 365 has had one of its biggest outages in a long time, and at its peak Downdetector showed around 130,000 reports for Outlook alone.

## Where to track it

Microsoft is tracking this under two incident IDs in the Microsoft 365 admin center.

| Incident | What it covers |
|---|---|
| **EX1550543** | Exchange Online mailbox connectivity |
| **MO1550821** | The wider impact across Microsoft 365 services and features |

Check both. Microsoft has updated the list of affected services more than once, and the current list is in MO1550821. If the admin center itself is slow or will not load, use the public status page at `status.cloud.microsoft`.

## What is affected

Microsoft has confirmed impact on **Exchange Online, Microsoft Teams, SharePoint Online, Microsoft Copilot and Microsoft Defender XDR**. Some reports also list Outlook on the web, OneDrive, Office Online, Planner, To Do, Intune, Defender for Office 365, Purview, Power BI and Universal Print, though not every organisation sees every one. It started with mailbox access in the Americas, and Microsoft then said connectivity problems could affect users in **any region**.

## Timeline so far

All times are UTC.

| Time | What happened |
|---|---|
| 12 November, around 17.54 | Microsoft starts investigating reports of users unable to reach Exchange Online mailboxes through multiple connection methods in the Americas |
| 12 November, 18.53 | Microsoft says the issue may affect Microsoft 365 connectivity in any region |
| 12 November, 19.00 | Microsoft starts redistributing connection traffic across its worldwide infrastructure to balance the load |
| 12 November, 19.35 | Microsoft pauses deployments and configuration changes |
| 12 November, 21.30 | An alternative health check method lets a subset of affected servers return to service |
| 13 November, early hours | Microsoft warns that restored servers can become unresponsive again once they receive traffic, and limits traffic to affected infrastructure in some locations |
| 13 November, around 02.00 | Bringing servers back a few at a time is reported to be working. No full fix yet |

## What is behind it

Microsoft has not published a root cause yet, so treat everything here as what is known so far, not the final answer.

* **It was not a traffic surge.** Microsoft said the load was not caused by more users. Servers had unexpectedly become unavailable.
* **Health checks played a part.** Servers were failing the automated health checks that decide whether they can take requests. As servers dropped out, the remaining ones took more load.
* **A core process was overwhelmed.** Microsoft found that a core process on the affected servers was being overloaded, which caused them to freeze. Restored servers sometimes froze again as soon as traffic returned.
* **No matching change found at first.** Microsoft said it had not identified a recent change that lined up with the start, but it is assessing a rollback of several recent configuration updates as a recovery option.
* **Not a cyberattack.** Microsoft has said there is no indication of a cyberattack.

Microsoft usually publishes a preliminary post incident review in the admin center within a few days of a major incident, and a final one later. That is where the real root cause will appear.

## What admins should do now

* **Tell your users early.** A short message on a channel that does not depend on Microsoft 365, such as SMS, an intranet page hosted elsewhere or your phone tree, saves your service desk hundreds of calls. Say it is a Microsoft wide issue and that nothing on their device needs fixing.
* **Do not troubleshoot devices.** Resetting Outlook profiles, reinstalling Teams, clearing credentials or enrolling devices again will not help and creates clean up work for later. The problem is in Microsoft's service.
* **Avoid tenant changes.** Do not change Conditional Access, mail flow rules or DNS to work around this. When the service recovers, you want your configuration exactly as it was.
* **Use cached data where you can.** Outlook in cached mode still shows mail and calendar already synced, so users can read and draft offline. Files synced by OneDrive are still available locally.
* **Watch for phishing.** Outages are a gift to attackers. Warn users that Microsoft will not email them asking them to sign in again, reset passwords or "restore" their mailbox, and treat any such message as suspicious.
* **Do not assume endpoint protection has stopped.** Defender XDR portal access being disrupted does not mean protection on devices has stopped. Agents keep running locally.

## What to check once service returns

* **Mail flow.** Expect queued mail to arrive in bursts and some delays. Check message trace for anything that bounced and needs to be resent.
* **Teams meetings and recordings.** Meetings during the outage may be missing recordings or transcripts, which also means no Copilot meeting recap for them.
* **Intune and Defender.** If either was affected for you, check that device check ins, policy assignments and alerts have caught up before you act on any report from the outage window.
* **Service health history.** Read the post incident review when it is published, and save it for your own incident records.

I will keep this post updated as Microsoft confirms recovery and the cause.

<div class="refs" markdown="1">

**References**

1. [Microsoft 365 service status page](https://status.cloud.microsoft)
2. [Cyber Security News on the Microsoft 365 outage, incidents EX1550543 and MO1550821](https://cybersecuritynews.com/massive-microsoft-365-outage/)
3. [Tom's Guide live updates on the Microsoft 365 outage](https://www.tomsguide.com/news/live/microsoft-outlook-down-live-updates-outage-11-12-26)
4. [Forbes Australia on the global Microsoft outage](https://www.forbes.com.au/news/world-news/microsoft-servers-crash-in-global-outage/)
5. [BleepingComputer on the Microsoft 365 outage disrupting Outlook, Teams and Copilot](https://www.bleepingcomputer.com/news/microsoft/massive-microsoft-365-outage-disrupts-outlook-teams-copilot-worldwide/)

</div>
