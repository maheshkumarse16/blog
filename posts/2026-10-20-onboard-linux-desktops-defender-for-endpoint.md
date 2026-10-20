---
title: "How to onboard Linux desktops to Defender for Endpoint now the preview is open"
date: 2026-10-20
author: Mahesh
type: How to
description: "A full walk through for putting Ubuntu, Fedora and other Linux workstations into Defender for Endpoint during the public preview, from the onboarding package to a tested EDR alert."
tags: [Defender, Vulnerability Management]
---

Microsoft has opened a public preview of Defender for Endpoint on Linux desktops. The announcement went out on the Defender blog on 14 October 2026 and the Learn prerequisites page now carries the preview text. For most of us this closes an awkward gap. Developers have been running Ubuntu or Fedora laptops for years, and the honest answer to "is that box covered" was usually no.

The good news is that nothing about the agent is new. It is the same `mdatp` package and the same onboarding script you already use on Linux servers. Defender decides whether a device is a workstation from signals on the box, and the deployment methods are identical. This post takes you from nothing to a desktop that shows in device inventory, passes a connectivity test and raises a test EDR alert.

## Before you start

**Licence.** Linux desktops need Microsoft Defender for Endpoint Plan 2, which is also included in Microsoft 365 E5 and Microsoft 365 E7. Defender for Servers and Defender for Business servers cover servers only, so do not count those licences for laptops. Plan 1 is not listed for Linux desktops.

**Permissions.** You need root or sudo on the workstation and a Defender for Endpoint role that lets you download onboarding packages in the Defender portal.

**Supported distributions.** Every distribution supported on servers is supported on desktops, and support follows the distribution and kernel, not the desktop environment. GNOME, KDE and the rest make no difference. For x64 the list includes Ubuntu LTS 20.04, 22.04, 24.04 and 26.04 (older LTS releases are still listed too), Debian 9 to 13, RHEL 7.2 and later through 10, Fedora 33 to 44, openSUSE Leap 15.6 and 16, Rocky, Alma, Oracle Linux and SLES. Anything not on the published list is unsupported, and a home grown spin of a supported distribution may work but support can ask you to reproduce on stock.

**Minimum system.** Kernel 3.10.0 build 327 or later, 1 CPU core, 1 GB RAM, 2 GB of free disk and `systemd`. Device isolation needs `iptables` and `ip6tables` (or the `nft` variants) installed.

**Network.** Only static or transparent proxies work. PAC files, WPAD and authenticated proxies are not supported, and TLS inspection of the Defender endpoints breaks the agent. If your web proxy inspects traffic, get the bypass for the Defender domains in place first.

**Other security tools.** Running Defender next to another product that uses Fanotify in blocking mode is unsupported and can hang the machine. Developer laptops often carry a second agent, so check before you install.

## Get the onboarding package

1. Sign in to the Defender portal at security.microsoft.com and open the onboarding page.
<span class="path">System > Settings > Endpoints > Device management > Onboarding</span>
2. In the first drop down, **Select operating system to start onboarding process**, choose **Linux Server**. There is no separate desktop entry. The same package onboards workstations.
3. In the **Deployment method** drop down choose **Local Script**.
4. Select **Download onboarding package**. The browser saves `WindowsDefenderATPOnboardingPackage.zip`.
5. Copy the zip to the workstation and extract it.

```bash
unzip WindowsDefenderATPOnboardingPackage.zip
ls
# MicrosoftDefenderATPOnboardingLinuxServer.py
```

Do not edit or repackage that Python file. Microsoft treats a modified package as unsupported.

## Install and onboard with the installer script

The installer script is the quickest route for a handful of machines and the easiest to wrap in Ansible, Chef or Puppet later.

6. Download `mde_installer.sh` from the `microsoft/mdatp-xplat` repository on GitHub (the path is `linux/installation/mde_installer.sh`) and make it executable.

```bash
chmod +x mde_installer.sh
```

7. Run a prerequisite check on its own first. This reports problems such as an unsupported distribution or missing packages without changing anything.

```bash
sudo ./mde_installer.sh --pre-req
```

8. Install from the production channel and onboard in one go.

```bash
sudo ./mde_installer.sh --install --onboard ./MicrosoftDefenderATPOnboardingLinuxServer.py --channel prod --pre-req
```

Useful switches if you need them are `--passive-mode` to start with antivirus in passive mode, `--tag GROUP <value>` to tag the device, `--http-proxy` or `--https-proxy` for a static proxy, and `--log-path` to write the script output somewhere you can collect it.

If you would rather use the package manager by hand, add the Microsoft repository for your distribution, install the `mdatp` package with `apt` or `dnf`, then run `sudo python3 MicrosoftDefenderATPOnboardingLinuxServer.py`. If you install but skip onboarding, the product stays unlicensed and the health check returns false.

## Check the agent locally

9. Confirm the device has picked up your organisation ID.

```bash
mdatp health --field org_id
```

A good result prints the organisation ID of the tenant. A blank result means onboarding did not run.

10. Check overall health and real time protection.

```bash
mdatp health --field healthy
mdatp health --field real_time_protection_enabled
mdatp health --field definitions_status
```

Expect `true` for the first two. On a brand new install `healthy` can stay false until the first definitions download completes, so give it a few minutes before you chase it. If real time protection is off, turn it on with `mdatp config real-time-protection --value enabled`.

11. Test the cloud connections.

```bash
mdatp connectivity test
```

Every line should end with `[OK]`. A failure against the `winatp-gw` or `events.data.microsoft.com` addresses almost always means a proxy or TLS inspection problem.

## Verify it worked

12. Trigger an antivirus detection with the EICAR test file and confirm it was caught.

```bash
curl -o /tmp/eicar.com.txt https://secure.eicar.org/eicar.com.txt
mdatp threat list
```

The threat list should show the EICAR file as quarantined.

13. Run the EDR test. Download the script from `https://aka.ms/MDE-Linux-EDR-DIY`, then run it.

```bash
chmod +x mde_linux_edr_diy.sh
./mde_linux_edr_diy.sh
```

An alert for the test should appear in the Defender portal after a few minutes.

14. Find the device in the portal.
<span class="path">Assets > Devices</span>
Search for the host name. A new device usually appears within 5 to 20 minutes. Open it and check the device type. If Defender could not find enough desktop signals it classifies the machine as a server, and Microsoft says that is by design. Note which machines land as servers before you build device groups or reports on device type.

If you want a quick list across the estate, this advanced hunting query shows Linux devices and how Defender has classified them.

```kql
DeviceInfo
| where Timestamp > ago(1d)
| where OSPlatform == "Linux"
| summarize arg_max(Timestamp, DeviceType, OSDistribution, OSVersion) by DeviceName
| order by DeviceType asc
```

A good result lists each laptop with `Workstation`. Rows with `Server` are the ones to look at.

## Turn on debug logging when something fails

15. Raise the log level, reproduce the problem, then collect a diagnostic bundle.

```bash
mdatp log level set --level debug
sudo mdatp diagnostic create --path /tmp
mdatp log level set --level info
```

The first command answers `Log level configured successfully` and the second prints the path of a zip file. Always set the level back to info afterwards because debug logging grows fast on a busy desktop. The install log lives at `/var/log/microsoft/mdatp/install.log`.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| `org_id` is blank | Onboarding script never ran or failed | Run `sudo python3 MicrosoftDefenderATPOnboardingLinuxServer.py` and check the install log |
| `healthy` is false straight after install | Definitions not downloaded yet | Wait a few minutes and check `definitions_status` |
| Connectivity test fails with curl error 35 or 60 | TLS inspection on the proxy | Run `curl -v https://winatp-gw-weu.microsoft.com` and check the issuer is Microsoft, then exempt the Defender domains and restart `mdatp` |
| Connectivity test fails through a PAC or authenticated proxy | Unsupported proxy type | Use a static proxy with `mdatp config proxy set --value http://address:port` |
| Desktop freezes or file access stalls | Another Fanotify based security agent | Check the `conflicting_applications` field in `mdatp health` and put Defender antivirus in passive mode |
| Laptop shows as Server in inventory | Not enough workstation signals | Expected behaviour in the preview, group these machines by tag instead of device type |
| Isolation does nothing | `iptables` or `ip6tables` missing | Install the packages and retry the isolation |
| Agent broken after a distro release upgrade | Major OS upgrade with the agent in place | Uninstall `mdatp`, upgrade the OS, then reinstall and onboard |

The part that trips people up on developer laptops is not the agent, it is the proxy. Corporate laptops that run Linux often sit on a PAC file that works fine for browsers, and Defender quietly refuses it. Sort out a static proxy setting for these machines before you roll the script out, and the rest of the deployment is the same dull process you already run on servers.

<div class="refs" markdown="1">

**References**

1. [Defender blog post on securing Linux desktops](https://techcommunity.microsoft.com/blog/microsoftdefenderatpblog/secure-linux-desktops-with-microsoft-defender/4560822)
2. [Prerequisites for Defender for Endpoint on Linux](https://learn.microsoft.com/en-us/defender-endpoint/mde-linux-prerequisites)
3. [Deploy Defender for Endpoint on Linux with the installer script](https://learn.microsoft.com/en-us/defender-endpoint/linux-installer-script)
4. [Deploy Defender for Endpoint on Linux manually](https://learn.microsoft.com/en-us/defender-endpoint/linux-install-manually)
5. [Troubleshoot cloud connectivity on Linux](https://learn.microsoft.com/en-us/defender-endpoint/linux-support-connectivity)
6. [Resources for Defender for Endpoint on Linux](https://learn.microsoft.com/en-us/defender-endpoint/linux-resources)
7. [Petri coverage of Linux desktop support](https://petri.com/?p=780702)

</div>
