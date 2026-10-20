---
title: "Office LTSC 2021 is out of support. How to replace it with Microsoft 365 Apps"
date: 2026-10-20
author: Mahesh
type: How to
description: "Office LTSC 2021 and Office 2021 stopped getting security updates on 13 October 2026. This guide covers finding the remaining installs, removing LTSC 2021 with the Office Deployment Tool, installing Microsoft 365 Apps and checking the result."
tags: [Microsoft 365, ConfigMgr, Windows 11]
---

Support for Office LTSC 2021, Visio LTSC 2021 and Project LTSC 2021 ended on 13 October 2026, and so did support for the retail Office 2021 suites. Microsoft confirmed it in Message Center post MC1509797 on 15 October. There is no extension and no extended security update programme. The apps keep running, but there will be no more security fixes, bug fixes or technical support.

The last builds those products received came out on the same day. Office LTSC 2021 volume licensed stops at Version 2108 build 14334.20974, and Office 2021 retail stops at Version 2608 build 20326.20232. Every Office CVE published from November onwards will apply to those machines and stay unpatched.

Microsoft offers two ways forward. Microsoft 365 Apps is the default for anything that connects to the internet. Office LTSC 2024, supported until October 2029, is meant for regulated, process control and fully disconnected machines. This guide covers the Microsoft 365 Apps route on Windows.

## Before you start

**Licences.** Users need a plan that includes Microsoft 365 Apps. For enterprises that is Microsoft 365 E3, Office 365 E3 or Microsoft 365 Apps for enterprise. Under 300 users, Business Premium, Business Standard or Apps for business. Visio and Project need their own subscriptions, such as Visio Plan 2 or Project Plan 3 or 5.

**Permissions.** Local administrator on the target devices, or a deployment tool such as Configuration Manager or Intune that runs as system.

**Tools.** The Office Deployment Tool (`setup.exe`) from the Microsoft Download Center, a share or package to hold it, and the Office ADMX templates (Download Center ID 49030) if you manage settings with Group Policy.

**Disk and network.** At least 4 GB free on the system drive. Delivery Optimization is supported on Windows 10 and 11 and saves a lot of WAN traffic when you upgrade a whole site at once.

**Copilot.** If these users will get Copilot later, put them on Monthly Enterprise Channel or Current Channel. Copilot needs one of those two channels.

## Find what is left

1. If you run Configuration Manager, open the Office 365 Client Management dashboard and build a dynamic collection of devices grouped by Office version. Anything reporting Version 2108 on the PerpetualVL2021 channel is LTSC 2021.
2. On a single machine, open Word and go to **File > Account**. The product name under **Product Information** tells you which suite and year is installed.
3. Note which machines also have Visio LTSC 2021 or Project LTSC 2021. They share the same end of support date, so remove them in the same pass and plan their replacement licences at the same time.
4. Split the list. Machines that are genuinely offline or regulated go to Office LTSC 2024. Everything else goes to Microsoft 365 Apps.

## Prepare the removal package

LTSC 2021 is a Click to Run product, so the `RemoveMSI` element does not touch it. That element only handles MSI installs of 2007, 2010, 2013 and 2016. Microsoft's guidance is to uninstall the previous version before installing Microsoft 365 Apps, and for Click to Run products the tool for that is the `Remove` element.

5. Create `remove-ltsc2021.xml` next to `setup.exe`. List each product ID you found in the inventory.

```xml
<Configuration>
  <Remove All="FALSE">
    <Product ID="ProPlus2021Volume" />
    <Product ID="VisioPro2021Volume" />
    <Product ID="ProjectPro2021Volume" />
  </Remove>
  <Display Level="None" AcceptEULA="TRUE" />
  <Property Name="FORCEAPPSHUTDOWN" Value="TRUE" />
</Configuration>
```

Leaving out the `Language` element removes every installed language for each product. Use `Standard2021Volume`, `VisioStd2021Volume` or `ProjectStd2021Volume` if that is what the device has. `FORCEAPPSHUTDOWN` closes any Office app that blocks the removal, and users will lose unsaved work, so schedule this outside working hours or leave it out and accept some failures to retry.

## Prepare the install package

6. Create `install-m365apps.xml` in the same folder.

```xml
<Configuration>
  <Add OfficeClientEdition="64" Channel="MonthlyEnterprise">
    <Product ID="O365ProPlusRetail">
      <Language ID="en-us" />
    </Product>
  </Add>
  <RemoveMSI />
  <Display Level="None" AcceptEULA="TRUE" />
</Configuration>
```

Change the language to match your users. Keep `RemoveMSI` in, because it cleans up any Office 2016 MSI leftovers that sometimes sit on the same machines. If some devices run 32 bit Office today and you want them on 64 bit, add `MigrateArch="TRUE"` to the `Add` element. For Remote Desktop session hosts, add `<Property Name="SharedComputerLicensing" Value="1" />`.

7. Download the source files once to your share so devices do not each pull from the internet.

```cmd
setup.exe /download install-m365apps.xml
```

If you plan to install from the share, add `SourcePath="\\server\share"` to the `Add` element before you run the download.

## Run the upgrade

8. On a pilot device, from an administrator command prompt in the tool folder, run the removal.

```cmd
setup.exe /configure remove-ltsc2021.xml
```

The command returns when the removal is complete. Check **Apps > Installed apps** in Windows Settings and confirm the LTSC 2021 entries are gone.

9. Run the install.

```cmd
setup.exe /configure install-m365apps.xml
```

10. Sign in to Word with the user's work account. Microsoft 365 Apps activates against the user's licence. The first launch can show the **Your Privacy Matters** dialog, and the user must accept it to finish setup.

11. Once the pilot works, wrap both commands into a single deployment. A small batch file that runs the two `setup.exe` lines in order works as the install command for a Configuration Manager application or an Intune Win32 app.

12. If Configuration Manager was managing Office updates for these devices, disable the **Management of Microsoft 365 Apps for enterprise** policy for the upgraded collection and confirm the `OfficeC2RCom` component is no longer registered on the clients. Otherwise Configuration Manager and the new update channel will compete.

## Verify it worked

13. Open Word and go to **File > Account**. You should see Microsoft 365 Apps for enterprise under **Product Information**, the signed in user, and Monthly Enterprise Channel next to the version.
14. Compare the build with the current Monthly Enterprise build. In October 2026 the security update builds are 20430.20180 for Version 2609, 20326.20232 for 2608 and 20228.20276 for 2607.
15. Next to **Update Options** confirm **Updates are automatically downloaded and installed** is shown.
16. Rerun your inventory query from step 1. The device should drop off the LTSC 2021 list.

## Clean up the stubborn ones

17. If the removal fails or leaves broken entries, use the scrub scenario in the Microsoft Support and Recovery Assistant command line tool.

```cmd
SaRAcmd.exe -S OfficeScrubScenario -AcceptEula -OfficeVersion All
```

Replace `All` with a specific version if you only want to remove one release. Restart the device and run the install package again.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| Visio or Project 2021 still installed after the upgrade | Product IDs missing from the removal file | Add their product IDs to the removal file and run it again |
| Removal reports success but LTSC still listed | An Office app was open and blocked removal | Add `FORCEAPPSHUTDOWN` or schedule the job when users are signed out |
| Office installs but will not activate | User has no Microsoft 365 Apps licence | Assign the licence and have the user sign in again |
| Office cannot activate after install | Wrong product ID in the install file | Check the `Product ID` value, the wrong ID prevents activation |
| Device lands on Current Channel | Channel attribute missing | Set `Channel="MonthlyEnterprise"` in the `Add` element or set **Update Channel** by policy |
| Updates fight with Configuration Manager | Office 365 client management still on | Disable the **Management of Microsoft 365 Apps for enterprise** client setting |
| Bandwidth spikes on a site | Every device downloading from the CDN | Install from a local share and turn on Delivery Optimization |
| Users still prompted for privacy settings | First run dialog | Expected, the user accepts once |

The machines that hold this up are rarely the desktops. It is the one PC on a lab bench or a production line that runs a macro nobody has tested on a newer build, and someone will ask for an exception. Give those a date for moving to Office LTSC 2024 instead of leaving them on an unsupported product, because LTSC 2024 keeps them fixed in place and still patched until 2029.

<div class="refs" markdown="1">

**References**

1. [Message Center MC1509797 on the end of support for Office LTSC 2021](https://mc.merill.net/message/MC1509797)
2. [Office LTSC 2021 lifecycle](https://learn.microsoft.com/lifecycle/products/office-ltsc-2021)
3. [End of support for Office 2021](https://support.microsoft.com/en-us/office/system-requirements/end-of-support-for-office-2021)
4. [Plan your upgrade from older versions of Office](https://learn.microsoft.com/en-us/microsoft-365-apps/end-of-support/plan-upgrade-older-versions-office)
5. [Office Deployment Tool configuration options](https://learn.microsoft.com/en-us/microsoft-365-apps/deploy/office-deployment-tool-configuration-options)
6. [Product IDs supported by the Office Deployment Tool](https://learn.microsoft.com/en-us/office365/troubleshoot/installation/product-ids-supported-office-deployment-click-to-run)
7. [Release notes for Microsoft 365 Apps security updates](https://learn.microsoft.com/en-us/officeupdates/microsoft365-apps-security-updates)
8. [Deploy Office LTSC 2024](https://learn.microsoft.com/en-us/office/ltsc/2024/deploy)

</div>
