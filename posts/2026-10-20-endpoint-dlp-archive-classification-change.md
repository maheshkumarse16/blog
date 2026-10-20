---
title: "Endpoint DLP will report zip and rar files as one item from late October"
date: 2026-10-20
author: Mahesh
type: What's new
description: "Endpoint DLP on Windows is changing how it classifies archives, so events will name the outer zip or rar file instead of each file inside. Here is what changes, when, and which reports and alerts to check before it lands."
tags: [Purview, Windows 11]
---

Message Center post MC1474107, published on 18 September 2026, announced a change to how Endpoint DLP on Windows classifies archive files. Public preview ran from late September to mid October 2026 and general availability for worldwide tenants is due between late October and early November 2026. So it is landing now.

There is no setting to turn on and no opt out. The change matters because it alters the shape of the events your DLP reports, SIEM rules and alert counts are built on.

## What changes

Today, when Endpoint DLP on a Windows device classifies a .zip or .rar file, the files inside the archive can raise their own classification events. After the change the archive is classified directly in a single operation. Events report only the outer archive, and the files inside no longer generate events of their own.

What does not change is the policy behaviour. Microsoft says DLP still evaluates the content inside archives, including sensitivity labels and the context conditions in your rules. A rule that blocked copying a zip containing card numbers to USB still blocks it. Only the reporting changes.

The roadmap item, 570965, says the aim is to line endpoint behaviour up with how cloud workloads already treat archives, reduce noise in event reporting and speed up archive processing.

One warning on dates. The Message Center post gives late October to early November. A mirror of the roadmap entry from 10 September shows preview in November and release in December. I would plan on the Message Center dates because they are later and more specific, and treat the roadmap as out of date.

## Who is affected

Any tenant that runs Endpoint DLP on Windows 10, Windows 11 or Windows Server 2019 and later with archive classification in play. The Learn page lists the archive extensions monitored through policy on Windows as .zip, .rar, .7z, .tar, .gz, .arj, .bz2, .cab, .chm, .lzh, .lzma, .mhtml, .xar and .xz. The Message Center post names .zip and .rar as examples, so expect the new behaviour across the archive types Endpoint DLP already handles.

macOS devices are not part of this change.

## What to check before it lands

Most of the work here is outside the Purview portal, in whatever consumes DLP events.

**SIEM rules and dashboards.** Any rule that counts DLP events per file, or alerts when one user triggers more than a set number of events, will see lower numbers once an archive of fifty files becomes one event. If you tuned thresholds against the old counts, retune them after rollout. Rules that look for a specific file name inside an archive will stop matching, because the inner name no longer appears as its own event.

**Activity explorer reviews.** Analysts used to seeing the inner file names in Activity explorer will now see only the archive. Open Activity explorer at `https://purview.microsoft.com/informationprotection/dataclassification/activityexplorer`, apply the **Endpoint DLP activities** filter set and look at a recent event on an archive so you have a before picture to compare with.

**Investigation runbooks.** If your runbook tells an analyst to read the inner file from the event, update it. With full file evidence turned on in Endpoint DLP settings, the analyst can still retrieve the archive itself and open it. Without evidence collection they will only have the archive name.

**Reports for compliance teams.** Monthly figures will drop. Tell whoever reads them before the November numbers come out, or someone will report it as an improvement in user behaviour.

## How to tell when it has arrived

Microsoft has not published a client version or a registry value that marks the change, so there is no switch to check on the device. The practical test is to watch for it in your data.

1. Pick a pilot device that is onboarded and showing **Updated** for policy sync on the device onboarding page in Purview.
2. Create a zip on that device containing two files that each match a sensitive information type in an existing device rule.
3. Copy the zip to a location your rule audits, such as a USB drive or a network share.
4. In Activity explorer, filter on that user and device. Before the change you can see events tied to the inner files. After it, a single event names the zip.

Repeat the test every week or so until the behaviour flips. It will not change on every device at the same moment, so expect a mixed period.

## Related change from earlier in the year

Roadmap item 566617, released in August 2026, taught Endpoint DLP to detect sensitivity labels on files inside archives. If you wrote rules that rely on that, they keep working. The archive change only affects how the result is reported.

I would not spend long on this one. Find the two or three places where someone counts or names DLP events on archives, adjust them, and tell the compliance team why the numbers fell. The policy side needs nothing.

<div class="refs" markdown="1">

**References**

1. [Message Center MC1474107 on archive file classification in Endpoint DLP](https://mc.merill.net/message/MC1474107)
2. [Roadmap item 570965 on archive classification for Windows endpoints](https://mc.merill.net/message/RM570965)
3. [Learn about Endpoint data loss prevention](https://learn.microsoft.com/en-us/purview/endpoint-dlp-learn-about)
4. [Get started with Activity explorer](https://learn.microsoft.com/en-us/purview/data-classification-activity-explorer)
5. [Roadmap item 566617 on labels inside archives](https://mc.merill.net/message/RM566617)

</div>
