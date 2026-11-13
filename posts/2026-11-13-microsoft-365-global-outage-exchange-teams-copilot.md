---
title: "Microsoft 365 global outage: Exchange Online, Teams, SharePoint and Copilot (MO1550821), now restored for most users"
date: 2026-11-13
author: Mahesh
type: Known issue
description: "A major Microsoft 365 outage that started on 12 November 2026 hit Exchange Online, Outlook, Teams, SharePoint, Copilot and Defender XDR worldwide. Service is now restored for most users. What happened, what Microsoft changed to fix it, and what to check in Outlook now that it is back."
tags: [Microsoft 365, Copilot, Defender, Intune]
---

> **Update, 13 November 2026, 14.00 UTC.** Service is now restored for most users. Microsoft rolled back a recent network configuration change and then rolled out a patch to an upstream authentication and routing component, region by region, which brought servers back to stable service. Some users may still see delayed mail or slow sync while the backlog clears, and Microsoft has not yet published the root cause. **If you use Outlook, please check it now.** The steps are in the section below.

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
| 13 November, morning | Microsoft rolls back a recent network configuration change that lined up with the start of the outage, and limits some traffic types while it checks stability |
| 13 November, later | Microsoft patches an upstream authentication and routing component and reports positive results for server stability. The patch rolls out region by region, starting with regions in or entering business hours |
| 13 November, afternoon | Service restored for most users. Mail delays may remain while queues clear |

## What is behind it

Microsoft has not published a root cause yet, so treat everything here as what is known so far, not the final answer.

* **It was not a traffic surge.** Microsoft said the load was not caused by more users. Servers had unexpectedly become unavailable.
* **Health checks played a part.** Servers were failing the automated health checks that decide whether they can take requests. As servers dropped out, the remaining ones took more load.
* **A core process was overwhelmed.** Microsoft found that a core process on the affected servers was being overloaded, which caused them to freeze. Restored servers sometimes froze again as soon as traffic returned.
* **A network change was rolled back.** Microsoft first said it had not found a matching change, but it later rolled back a recent network configuration change whose timing lined up with the start of the outage.
* **A patch brought stability back.** The fix that made the difference was a patch to an upstream authentication and routing component, rolled out region by region.
* **Not a cyberattack.** Microsoft has said there is no indication of a cyberattack.

Microsoft has still not confirmed a root cause, and its description of the problem changed several times during the incident. Microsoft usually publishes a preliminary post incident review in the admin center within a few days of a major incident, and a final one later. That is where the real root cause will appear.

## Check your Outlook now

Service is back for most people, but Outlook does not always recover cleanly on its own after a long outage. Please take two minutes to check these.

1. **Close Outlook completely and open it again.** Make sure it is not still running in the system tray. This forces a fresh connection.
2. **Look at the bottom status bar.** It should say **Connected to Microsoft Exchange** or **All folders are up to date**. If it says **Disconnected**, **Trying to connect** or **Working offline**, wait a few minutes and check that **Work Offline** is not switched on in the **Send / Receive** tab.
3. **Check your Outbox.** Anything you wrote during the outage may be sitting there. Open each message and send it again if it has not gone.
4. **Check your Sent Items.** Confirm that important emails you sent yesterday and today actually left. If they are missing, send them again.
5. **Expect late mail.** Mail sent to you during the outage is delayed, not lost. It may arrive in bursts over the next few hours, with the original sent time, so it can land lower down your inbox than you expect. Sort by received date if you are waiting for something.
6. **Check your calendar.** Meeting invites and replies may have been delayed. Confirm the meetings you care about for today and tomorrow are there, and that your responses were sent.
7. **Compare with Outlook on the web.** If something looks wrong in the desktop app, open Outlook on the web. If it is correct there, the desktop app is still catching up. Give it some time.
8. **Only then rebuild anything.** If Outlook on the web works but the desktop app still will not connect after an hour, restart the computer first. Do not rebuild your profile or reinstall Office unless your IT team asks you to.

If you work in IT, the same applies to Teams, where calendars and meeting recordings depend on Exchange, and to Purview and Defender, which may need time to catch up on events from the outage window.

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

I will update this post again when Microsoft publishes the post incident review with the confirmed root cause.

<div class="refs" markdown="1">

**References**

1. [Microsoft 365 service status page](https://status.cloud.microsoft)
2. [Cyber Security News on the Microsoft 365 outage, incidents EX1550543 and MO1550821](https://cybersecuritynews.com/massive-microsoft-365-outage/)
3. [Tom's Guide live updates on the Microsoft 365 outage](https://www.tomsguide.com/news/live/microsoft-outlook-down-live-updates-outage-11-12-26)
4. [Forbes Australia on the global Microsoft outage](https://www.forbes.com.au/news/world-news/microsoft-servers-crash-in-global-outage/)
5. [BleepingComputer on the Microsoft 365 outage disrupting Outlook, Teams and Copilot](https://www.bleepingcomputer.com/news/microsoft/massive-microsoft-365-outage-disrupts-outlook-teams-copilot-worldwide/)
6. [Windows Forum on the MO1550821 patch rollout after the first fixes failed](https://windowsforum.com/news/outlook-outage-mo1550821-microsoft-rolls-out-patch-after-initial-fixes-fail-megathread.452141/)
7. [Microsoft 365 Status on X](https://x.com/MSFT365Status/status/2120962673911181437)

</div>
