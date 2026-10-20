---
title: "ConfigMgr 2609 moves your CMG to new Azure VM sizes. How to check vCPU quota before you upgrade"
date: 2026-10-20
author: Mahesh
type: How to
description: "Updating to ConfigMgr 2609 migrates every cloud management gateway to Dadv6 virtual machines, and the migration fails with QuotaExceeded if the subscription has no room. How to work out what you need, raise the quota and confirm the CMG is healthy afterwards."
tags: [ConfigMgr]
---

There is one part of the ConfigMgr 2609 update that has nothing to do with your site server and everything to do with your Azure subscription. When the site updates, every cloud management gateway is moved to a new virtual machine size from the Dadv6 family. If the subscription does not have enough vCPU quota for that family in the CMG's region, the migration fails and `CloudMgr.log` fills with `QuotaExceeded`.

Microsoft has added a quota check to the 2609 release notes for exactly this reason. Here is how to run it properly, with the sums worked out, before you click **Install Update Pack**.

## Why the size is changing

CMG scale sets used Av2 and B series sizes. Those sizes are due to retire in November 2028 and are already short of capacity in some regions. With 2609, each CMG tier maps to a new size.

| CMG tier | Old size | Old vCPU | New size | New vCPU | New memory |
|---|---|---|---|---|---|
| Small | `Standard_B2s` | 2 | `Standard_D2ads_v6` | 2 | 8 GiB |
| Medium | `Standard_A2_v2` | 2 | `Standard_D4ads_v6` | 4 | 16 GiB |
| Large | `Standard_A4_v2` | 4 | `Standard_D8ads_v6` | 8 | 32 GiB |

Medium and Large double their vCPU count. That doubling is what pushes subscriptions over their limit. The cost is described as close to the old sizes, but check it with whoever pays the Azure bill.

The same update also moves CMGs from Azure Load Balancer inbound NAT rules version 1 to version 2, turns off shared key access on CMG storage and uses a Windows Server 2022 image without the old .NET 6 packages. Version 1 NAT rules retire on 30 September 2027, so 2609 is not an update to sit on for a year.

## Before you start

* **ConfigMgr version.** The site must be on 2503 or later to take 2609 as an in console update.
* **ConfigMgr role.** You need **Full administrator** or **Infrastructure administrator** to manage the CMG.
* **SQL access.** Read access to the site database at the top level site, which is the CAS if you have one or the standalone primary otherwise.
* **Azure role.** Contributor, or a role that includes Contributor access, on each subscription that hosts a CMG. You need it to raise a quota request.
* **Azure CLI.** Installed on your admin workstation, or use Cloud Shell in the Azure portal.
* **Time.** Quota requests are often approved within minutes, but some need a support ticket. Do this at least a few days before the upgrade window.

## Step 1. List every CMG and its size

1. Open SQL Server Management Studio and connect to the site database at the top level site.
2. Run this query. It only reads data.

    ```sql
    SELECT Name, Region, SubscriptionId, VmSize, NumberOfInstances
    FROM Azure_Service;
    ```

    Expect one row per CMG. `VmSize` shows the current size, for example `Standard_A2_v2`, and `NumberOfInstances` shows how many VMs the scale set runs.

3. Copy the results into a spreadsheet. Group the rows by `SubscriptionId` and `Region`, because quota is counted per subscription per region.

## Step 2. Work out the vCPUs you need

4. For each CMG, find the new vCPU value from the table above and multiply it by `NumberOfInstances`.
5. Add up the totals for all CMGs in the same subscription and region.
6. Add whatever else already uses Dadv6 vCPUs in that subscription and region, such as other workloads your cloud team runs.
7. Add headroom for temporary instances during the upgrade and later maintenance. I add at least one extra instance's worth per CMG.

A worked example. Two Medium CMGs with two instances each, both in UK South in the same subscription. Each needs 4 vCPUs times 2 instances, so 8 vCPUs. Together that is 16 vCPUs. Add one temporary instance per CMG, another 8, and you need room for 24 Dadv6 vCPUs in UK South.

Then check the second number. **Total Regional vCPUs** is a separate limit that counts every VM family in the region. The old CMG cores are part of the current usage figure, and during the migration both the old and new instances can exist for a while, so make sure the regional limit has room for the new total on top of what is already running.

## Step 3. Check the quota with Azure CLI

8. Sign in with `az login` and run the following in PowerShell, replacing the placeholders. The subscription ID and region come from the SQL query.

    ```powershell
    $subscriptionId = '<subscription ID>'
    $region = '<region name>'
    $usage = az vm list-usage --location $region --query "[?name.value=='standardDadv6Family']" --output json --subscription $subscriptionId
    $usage

    az vm list-usage --location $region --query "[?name.value=='cores']" --output json --subscription $subscriptionId
    ```

    The first command returns the Dadv6 family entry and the second returns the total regional cores entry. Each shows the current usage and the limit.

9. Subtract the current usage from the limit for each one. If the remainder is at least the number you worked out in Step 2, you are fine for that region. If the Dadv6 query returns an empty list, check the region name first. If it is right, open the **Quotas** page described in Step 4 and look for the family there before you go any further.
10. Repeat for every subscription and region pair from your spreadsheet.

## Step 4. Raise the quota if you are short

11. In the Azure portal, type "quotas" into the search box and select **Quotas**.
12. On the **Overview** page select **Compute**.
13. On **My quotas**, filter to the right subscription and region and select the **standard Dadv6 Family vCPUs** row.
14. Select **New Quota Request**, then **Enter a new limit**.
15. In the **New Quota Request** pane, type the new limit. Use the current usage plus your Step 2 figure, rounded up.
16. Select **Submit**. When a family request is approved, Azure raises the regional vCPU quota for that region to match.
17. If the request is not approved automatically, the portal offers a link to open a support request instead. For a quota that cannot be adjusted on that page, select the support icon on the row, set **Quota type** to **Other Requests**, select **Next**, enter the limit you need under **Problem details**, then **Next** and **Create**.
18. Run the CLI commands from Step 3 again and confirm the limits now show the new values.

## Step 5. Upgrade and watch the migration

19. Install 2609 the normal way from **Administration > Updates and Servicing**.
20. When the site update finishes, upgrade the ConfigMgr console. The old console does not show the new CMG sizes correctly.
21. On the top level site server, open `CloudMgr.log` from the `Logs` folder under the ConfigMgr install directory and follow it with CMTrace. You will see the deployment and status activity for each CMG as it moves.

If the log shows a `QuotaExceeded` error, it looks like this.

```json
{
  "details": [
    {
      "code": "QuotaExceeded",
      "message": "Operation could not be completed as it results in exceeding approved Total Regional Cores quota. Additional details - Deployment Model: Resource Manager, Location: <Your location>, Current Limit: 10, Current Usage: 8, Additional Required: 8, (Minimum) New Limit Required: 16."
    }
  ]
}
```

The message tells you which limit you hit and the minimum new limit required. Raise that quota as in Step 4 and the migration can carry on.

## Verify it worked

1. In the console, go to the CMG node.

    <span class="path">Administration > Cloud Services > Cloud Management Gateway</span>

    Each CMG should show a healthy status, and with the new console the size column reflects the new VM size.

2. Select a CMG and choose **Connection analyzer** in the ribbon.
3. Pick **Microsoft Entra user** and select **Sign In**, or pick **Client certificate**, then select **Start**. Every test should pass. Select any failed entry to read the detail in the **Description** field.
4. In the Azure portal, open the CMG's virtual machine scale set and confirm the instance size is the Dadv6 size from the table.
5. Check `CMGService.log` and `SMS_Cloud_ProxyConnector.log` on the CMG connection point server for steady traffic from internet clients. Logs from the Azure side sync to storage every five minutes, so allow up to ten minutes before you worry.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| `QuotaExceeded` on Total Regional Cores | The regional limit is too low even though the family quota is fine | Raise **Total Regional vCPUs** for that region and let the migration retry |
| `QuotaExceeded` on the Dadv6 family | No family quota or not enough for all instances | Raise **standard Dadv6 Family vCPUs** using Step 4 |
| Dadv6 query returns nothing | Wrong region name, or the family is not listed for that subscription | Check the region name, then look for the family on the **Quotas** page and raise a support request if it is missing |
| Console still shows old sizes | The console was not upgraded after the site update | Install the new console from the prompt or the site server's console setup |
| Need more detail in `CloudMgr.log` | Default logging level | Raise **Logging level** under `HKLM\SOFTWARE\Microsoft\SMS\COMPONENTS\SMS_CLOUD_SERVICES_MANAGER` and reproduce the problem |
| Clients stop using the CMG after the move | Service or connector problem | Run the connection analyzer and read `CMGService.log` and `SMS_Cloud_ProxyConnector.log` |

The thing that trips people up is not the family quota, which everyone checks. It is the regional total, because CMG subscriptions are often shared with other teams who quietly used up most of it. Ask your cloud team for both numbers before the change board, not on the night.

<div class="refs" markdown="1">

**References**

1. [Microsoft Learn on what is new in ConfigMgr 2609, including the CMG VM sizes and quota check](https://learn.microsoft.com/en-us/intune/configmgr/core/plan-design/changes/whats-new-version-2609)
2. [Microsoft Learn on monitoring the cloud management gateway and its logs](https://learn.microsoft.com/en-us/intune/configmgr/core/clients/manage/cmg/monitor-clients-cloud-management-gateway)
3. [Microsoft Learn on planning a cloud management gateway](https://learn.microsoft.com/en-us/intune/configmgr/core/clients/manage/cmg/plan-cloud-management-gateway)
4. [Microsoft Learn on increasing VM family vCPU quotas](https://learn.microsoft.com/en-us/azure/quotas/per-vm-quota-requests)
5. [Microsoft Learn on increasing regional vCPU quotas](https://learn.microsoft.com/en-us/azure/quotas/regional-quota-requests)
6. [Microsoft Learn summary of changes in ConfigMgr 2609](https://learn.microsoft.com/en-us/intune/configmgr/hotfix/2609/2377842)

</div>
