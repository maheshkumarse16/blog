---
title: "Agent usage metrics in the Microsoft 365 admin center no longer need an Agent 365 licence"
date: 2026-10-20
author: Mahesh
type: What's new
description: "From late November 2026 the active users, sessions, exceptions and run time figures for Microsoft built agents show in the admin center without Agent 365 or E7. Here is where the numbers appear, what they mean and how to read them without comparing the wrong reports."
tags: [Copilot, Microsoft 365]
---

Until now, if you opened an agent in the Microsoft 365 admin center and selected the Activity tab, you got a prompt telling you that you needed Microsoft 365 E7 or an Agent 365 licence. That is changing. Message Center post MC1506727, published on 13 October 2026, says Microsoft is removing the Agent 365 licence requirement for usage and activity metrics on supported agents built by Microsoft or on Microsoft platforms. General availability for worldwide tenants starts in late November 2026 and should complete the same month.

For anyone who has been asked "which of these agents does anyone actually use", this is the most useful admin change in the Copilot space this month.

## What becomes visible

The change covers existing and new supported agents. Once it arrives, these figures show without the extra licence.

1. In the agent registry, the **Active users**, **Total sessions**, **Exception rate** and **Run Time** columns.
2. On the agent overview page, the **Active users** figure, the **Active users over time** chart and the **Trending agents by active users** card.
3. In an agent's details, the **Activity** tab with its **Active users**, **Sessions**, **Exceptions** and **`Agent run-time`** cards, plus the **Active users over time** and **Sessions over time** charts.

Risk signals stay behind the licence. The Risks column in the registry, the Security tab and the other Agent 365 protection features still need E7 or Agent 365. Third party agents are also unchanged.

## Where to find it

The registry is the place to start.
<span class="path">Agents > All agents > Registry</span>

Select an agent to open its details fly out and pick the **Activity** tab. The default range is the last 30 days and you can change it. The tab also has an **Active users** table with **User principal name**, **Total sessions** and **Last activity date (UTC)** columns, which you can export to CSV.

The overview page gives the tenant wide picture.
<span class="path">Agents > Overview</span>

Monitoring is open to any admin who can see the agents pages. Governance actions such as approving requests or assigning owners need AI Administrator, or Global Administrator, which Microsoft says to keep for emergencies.

## What the numbers mean

The definitions are worth reading once, because they are not what most people assume.

**Active users** counts unique users with at least one interaction. **Sessions** are conversations, and a new session starts after 30 minutes of inactivity, so someone who returns after lunch counts twice. **Exceptions** are sessions that hit an error. **`Agent run-time`** is the total hours from the start of an interaction to the completion of the activity, so a long running agent can rack up hours with very few users.

Supported agent types for the activity metrics are agents built with Microsoft Copilot Agent Builder, SharePoint agents and agents built with the Microsoft 365 Agents Toolkit. Foundry, Copilot Studio and Agent Builder agents send their observability data automatically. Custom and third party agents only report if their developers instrumented them.

## Do not compare it with the Copilot usage report

This is the part that will cause arguments. The Copilot usage report under **Reports > Usage > Microsoft 365 Copilot > Agents** covers agent use in Copilot Chat, Word, Excel and PowerPoint. The registry and Activity tab count use in Copilot, Teams, Outlook, SharePoint and the Microsoft 365 apps. Microsoft says plainly not to compare the two sets of numbers. If your Copilot adoption pack already quotes agent figures from the usage report, label which source each number comes from before someone puts them side by side.

## Expect thin data at first

Microsoft warns that early metrics may look low or incomplete. It takes up to 30 days after data collection begins before an agent shows a full 30 day view. The data also only exists if the agent or platform sends activity and your observability settings allow it. Observability data is kept for 30 days and then deleted automatically, and it is stored in the default geography of the tenant, honouring the EU Data Boundary, with some service metrics possibly replicated to the EU or the US. Advanced Data Residency is not supported for this data. If you report quarterly, export monthly, because nothing older than 30 days will be there to pull.

## Pulling the list with Graph

If you want the agent list in a script alongside the new figures, the catalog is available through Microsoft Graph with the `CopilotPackages.Read.All` scope, and it works for an account holding the AI Administrator role. Learn marks the API as preview.

```powershell
Connect-MgGraph -Scopes 'CopilotPackages.Read.All'
$uri = "https://graph.microsoft.com/v1.0/copilot/admin/catalog/packages"
$all = @()
do {
    $r = Invoke-MgGraphRequest -Method GET -Uri $uri
    $all += $r.value
    $uri = $r.'@odata.nextLink'
} while ($uri)
$all | ForEach-Object { $_.displayName }
"Total agents: $($all.Count)"
```

A good run prints each agent name and a total that matches the **Total agents** tile in the registry. A 403 means the account lacks the role or the consent for the scope.

## Getting ready

Before late November, decide who will own the review of these numbers, export the current registry with **Export** and **All agents** so you have a baseline, and tell your adoption lead that the first month of data will undercount. The Learn page for agent details still says you need E7 or Agent 365 for the Activity tab. Expect that text to change when the rollout reaches you.

My view is that the run time figure will turn out to be the interesting one. Active users tells you who clicked. Run time tells you which agents are doing real work, and that is the number that should decide which agents you keep when the registry gets crowded.

<div class="refs" markdown="1">

**References**

1. [Message Center MC1506727 on agent usage and activity insights](https://mc.merill.net/message/MC1506727)
2. [Understand agent details in the Microsoft 365 admin center](https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-details)
3. [Agent 365 overview in the Microsoft 365 admin center](https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-365-overview)
4. [Agent registry in the Microsoft 365 admin center](https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-registry)
5. [Agent 365 data residency, protection and compliance](https://learn.microsoft.com/microsoft-agent-365/admin/data-residency-protection-compliance)

</div>
