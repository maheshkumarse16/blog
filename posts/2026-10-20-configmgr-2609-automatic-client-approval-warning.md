---
title: "ConfigMgr 2609 now warns if you automatically approve all computers. How to change it safely"
date: 2026-10-20
author: Mahesh
type: What's new
description: "The 2609 prerequisite check flags the Automatically approve all computers option, which Microsoft plans to remove. How to see which clients depend on it, switch to trusted domain approval and approve the stragglers."
tags: [ConfigMgr]
---

When you run the prerequisite check for Configuration Manager 2609, you may see a new warning called **Insecure client approval method**. It appears on a central administration site or primary site when the hierarchy is set to **Automatically approve all computers (not recommended)**.

It is only a warning and the upgrade will still go ahead. The important part is what comes next. Microsoft says the option is planned for removal in a future release, because it lets any computer that installs a client be trusted without anyone looking at it. When it goes, hierarchies still using it will have to change anyway, so it is better to do it on your own schedule.

## What client approval actually controls

Approval only matters for clients that talk to site systems over HTTP with a self signed certificate. Approving such a client tells the site it is a trusted computer.

Clients that always use HTTPS, or that use a PKI certificate over HTTP, do not need approval at all. By default the site also approves clients from the same Active Directory forest, trusted forests and connected Microsoft Entra tenants.

There are three methods in the hierarchy settings, matching these PowerShell values.

| Method | `Set-CMHierarchySetting` value |
|---|---|
| Manual approval of each computer | `ManuallyApproveEachComputer` |
| Automatic approval for computers in trusted domains | `AutomaticallyApproveComputersInTrustedDomains` |
| Automatic approval of all computers | `AutomaticallyApproveAllComputers` |

Microsoft describes trusted domain approval as the most secure choice. Approving everything is only reasonable when something else, such as network access control, already stops untrusted machines reaching the network.

## Find out who depends on the setting

Before changing anything, work out which clients would stop being approved. In practice these are workgroup machines, devices in untrusted forests and anything on HTTP that is not domain joined.

1. In the console, go to the devices list.

    <span class="path">Assets and Compliance > Devices</span>

2. Right click a column heading to add the **Domain** column if it is not showing, then sort by it. Devices whose domain is a workgroup name or a forest you do not trust are the ones to look at.
3. Check how those devices talk to the site. If your management points only accept HTTPS, approval does not apply to them and you can ignore them.
4. Make a short list of the HTTP, self signed clients outside trusted domains. These are the machines you will approve by hand after the change.

## Change the approval method

1. Go to the sites node.

    <span class="path">Administration > Site Configuration > Sites</span>

2. Select **Hierarchy Settings** in the ribbon.
3. Open the **Client Approval and Conflicting Records** tab.
4. Change the approval method from the automatic for all computers option to automatic approval for computers in trusted domains.
5. Select **OK**. The change applies to the whole hierarchy.

If you prefer PowerShell, connect to the site drive from the console and run this.

```powershell
Set-CMHierarchySetting -ApprovalMethod AutomaticallyApproveComputersInTrustedDomains
```

Open **Hierarchy Settings** again afterwards to confirm the tab shows the new method.

## Approve the clients that are left

New clients outside trusted domains will now wait for approval. Approve the ones on your list.

1. In **Assets and Compliance > Devices**, select one or more devices.
2. Select **Approve** in the ribbon, or right click and choose **Approve**.

Or from PowerShell, by name or through the pipeline.

```powershell
Approve-CMDevice -DeviceName "WKS-LAB-01"

Get-CMDevice -Name "WKS-LAB-01" | Approve-CMDevice
```

A client can only be approved after it is installed and assigned to a site. If you try earlier, there is nothing to approve yet.

If you ever need to stop trusting a machine, **Block** in the same ribbon stops it receiving policy. It only blocks communication from that client to site systems, so pair it with the usual steps if the device has been compromised.

## Check the warning has gone

Run the prerequisite check again from **Administration > Updates and Servicing** by right clicking the 2609 update and selecting **Run prerequisite check**. Follow `C:\ConfigMgrPrereq.log` on the site server. The **Insecure client approval method** line should no longer appear as a warning.

## My take

This is one of those settings that was usually switched on years ago to fix a lab or a migration and then forgotten. In most hierarchies I have seen, almost every client is domain joined or on HTTPS already, so trusted domain approval changes nothing visible. The handful of workgroup kiosks or test VMs that need a manual approval are a fair price for closing a hole that let any machine with a client installer join your site. If every device already talks to the site over HTTPS, the switch is close to free, so there is no reason to leave it until Microsoft removes the option for you.

<div class="refs" markdown="1">

**References**

1. [Microsoft Learn on what is new in ConfigMgr 2609](https://learn.microsoft.com/en-us/intune/configmgr/core/plan-design/changes/whats-new-version-2609)
2. [Microsoft Learn list of prerequisite checks, including the insecure client approval method](https://learn.microsoft.com/en-us/intune/configmgr/core/servers/deploy/install/list-of-prerequisite-checks#insecure-client-approval-method)
3. [Microsoft Learn on managing clients, including approve and block](https://learn.microsoft.com/en-us/intune/configmgr/core/clients/manage/manage-clients)
4. [Microsoft Learn on security and privacy for ConfigMgr clients](https://learn.microsoft.com/en-us/intune/configmgr/core/clients/deploy/plan/security-and-privacy-for-clients)
5. [Set-CMHierarchySetting reference](https://learn.microsoft.com/en-us/powershell/module/configurationmanager/set-cmhierarchysetting)
6. [Approve-CMDevice reference](https://learn.microsoft.com/en-us/powershell/module/configurationmanager/approve-cmdevice)

</div>
