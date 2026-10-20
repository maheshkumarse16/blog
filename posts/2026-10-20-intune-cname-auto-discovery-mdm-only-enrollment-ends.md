---
title: "Intune stops using the EnterpriseEnrollment CNAME for Windows MDM only enrolment in January 2027"
date: 2026-10-20
author: Mahesh
type: What's new
description: "From 15 January 2027 Windows devices enrolling with Enroll only in device management will no longer find Intune through DNS. Who is affected, what users will see and how to update your enrolment steps now."
tags: [Intune, Windows 11]
---

Microsoft has announced in message center post MC1509780, published on 15 October 2026, that Intune will stop supporting DNS CNAME auto discovery for Windows MDM only enrolment. The change lands on 15 January 2027 or soon after.

For most organisations this changes nothing. If your Windows devices are Entra joined or Entra hybrid joined, the enrolment does not go through this path at all. The people who will feel it are the ones who still use the **Enroll only in device management** link in Windows Settings and rely on a DNS record to point the device at Intune.

## What actually changes

Today, when a user types their work email address into the MDM only flow, Windows looks for a CNAME called `EnterpriseEnrollment` in the user's email domain. If it finds one pointing at `EnterpriseEnrollment-s.manage.microsoft.com`, the device finds the Intune enrolment service without the user typing anything else.

After the change, Intune no longer honours that lookup for MDM only enrolment. Windows will fail to discover the service and the user will be asked for the server address. The address they need is this one.

```text
https://enrollment.manage.microsoft.com/enrollmentserver/discovery.svc
```

A few things stay exactly as they are.

* Devices that are already enrolled stay enrolled. Nothing is re enrolled or removed.
* MDM only enrolment itself is still supported. Only the DNS based discovery goes away.
* Enrolment through Entra join and Entra hybrid join is not affected.
* The `EnterpriseRegistration` CNAME, which points at `EnterpriseRegistration.windows.net`, belongs to Entra device registration and is outside this change.

## Who should care

The usual suspects are personally owned Windows devices, contractor laptops that cannot be joined, kiosks or lab machines set up by hand, and old enrolment guides that still tell users to pick **Enroll only in device management**. If your service desk has a script that walks users through that link, it is going to break for anyone who enrols after mid January.

## Check whether you rely on it

1. In the Intune admin center, open the Windows enrolment options.

    <span class="path">Devices > Device onboarding > Enrollment > Windows</span>

2. Under **Enrollment options**, open **CNAME Validation**, type each of your user email domains into **Domain** and select **Test**. A pass means the record exists and points at Intune, which tells you someone set this up for a reason.
3. From any machine, confirm the record with a quick lookup. Replace the domain with your own.

    ```powershell
    Resolve-DnsName -Name EnterpriseEnrollment.contoso.com -Type CNAME
    ```

    A result whose `NameHost` is `EnterpriseEnrollment-s.manage.microsoft.com` means the record is live. An error saying the name does not exist means you never used CNAME discovery and you can stop here.

4. Search your user guides, onboarding emails and service desk knowledge articles for the phrase "Enroll only in device management". Each hit needs an extra step adding the server address.

## Update the enrolment steps

The manual flow on the device stays almost the same. Here is how I would write it for users from January.

1. Open **Settings**, then **Accounts**, then **Access work or school**.
2. Select **Enroll only in device management**.
3. Type your work email address and select **Next**.
4. If Windows says it could not find a management endpoint for that address, enter the server address `https://enrollment.manage.microsoft.com/enrollmentserver/discovery.svc` in the box it shows and continue.
5. Sign in with your work account and complete any multifactor prompt.

If you would rather users never type a URL, Windows supports a deep link that opens the same MDM only flow with the values already filled in. It only opens from Microsoft Edge.

```text
ms-device-enrollment:?mode=mdm&username=user@contoso.com&servername=https://enrollment.manage.microsoft.com/enrollmentserver/discovery.svc
```

Put it behind a button on an intranet page or in an onboarding email and test it on a spare device before you send it out. The `servername` parameter is documented as the MDM server URL, so a quick test tells you whether your users get straight to the sign in page.

Government cloud tenants use different host names. The US Government record points at `EnterpriseEnrollment-s.manage.microsoft.us` and the manual fallback is `enrollment.manage.microsoft.us`, so check the published endpoint for your cloud before you edit any guide.

## If an enrolment fails after the change

Collect the MDM diagnostics on the device. From a PowerShell window opened as administrator, run this.

```powershell
mdmdiagnosticstool.exe -area "DeviceEnrollment;DeviceProvisioning;Autopilot" -zip "c:\users\public\documents\MDMDiagReport.zip"
```

The zip contains `MDMDiagHtmlReport.html` and the event logs. In Event Viewer the relevant channel is under **Applications and Services Logs**, **Microsoft**, **Windows**, then the DeviceManagement Enterprise Diagnostics Provider folder, in the **Admin** log. A discovery failure shows up there before any certificate or policy errors, which makes it easy to tell apart from a licence or enrolment restriction problem.

## Should you delete the record

Microsoft has not said you must remove the `EnterpriseEnrollment` CNAME, and leaving it in place does no harm. I would leave it until February and then tidy it up with your DNS team, so nobody spends an afternoon wondering why a record exists that no longer does anything. Leave `EnterpriseRegistration` alone.

The bigger win is to ask why devices are still enrolling this way at all. In most estates I have seen, MDM only enrolment survives because of one old process nobody revisited. If those devices can be Entra joined, this retirement is a good excuse to fix that instead of rewriting the old guide.

<div class="refs" markdown="1">

**References**

1. [Message center post MC1509780 on the end of CNAME auto discovery](https://mc.merill.net/message/MC1509780)
2. [Intune Customer Success blog on preparing for the end of CNAME auto discovery](https://techcommunity.microsoft.com/blog/intunecustomersuccess/preparing-for-end-of-support-for-cname-auto-discovery-in-windows-mdm-only-enroll/4564973)
3. [Microsoft Learn on enabling auto discovery of the Intune enrolment server](https://learn.microsoft.com/en-us/intune/device-enrollment/windows/create-cname-autodiscovery)
4. [Microsoft Learn on MDM enrolment of Windows devices and the deep link format](https://learn.microsoft.com/en-us/windows/client-management/mdm-enrollment-of-windows-devices)
5. [Microsoft Learn on collecting MDM diagnostic logs](https://learn.microsoft.com/en-us/windows/client-management/mdm-collect-logs)

</div>
