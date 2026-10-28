---
title: "Apps and games crash when AC3 audio plays after KB5124010: how to confirm it and fix it"
date: 2026-10-28
author: Mahesh
type: Fix
description: "Older apps and games close without an error when they play AC3 Dolby Digital audio after the September 2026 KB5124010 update. The reports I checked say the fix is in KB5127648 and later. This guide shows how to confirm the update, install the fixed build, and use a temporary workaround if you cannot update straight away."
tags: [Windows 11, Intune]
---

A few friends asked me about this one too, so I thought it was worth writing up for everyone. The symptom is hard to pin down at first. An app or a game runs fine, then closes without any error as soon as it plays a certain kind of audio, such as music or an audio clip in a game. Nothing is written to the screen, so users blame the app, the game or their own machine.

The cause is the AC3 audio codec, also known as Dolby Digital. Windows has a built in decoder for AC3 audio, and some older apps depend on it. After the September 2026 update KB5124010, that decoder path failed for these apps. The reports I checked say the problem affects Windows 11 24H2, 25H2 and 26H2, and that it is fixed in the October update KB5127648 and later. I could not open Microsoft's own release health entry from this session, so please check it yourself before you rely on the detail.

This post covers how to confirm that you are seeing this issue, how to install the fixed build, and a temporary workaround if you cannot update straight away.

## What is happening

An app that uses the built in AC3 decoder hands audio to Windows. After KB5124010, the decoder path crashed when AC3 audio started playing. The app had no way to recover, so it closed.

The reports name a few affected titles, including older games and a productivity app, but Microsoft does not give a complete list. Most affected software is older or specialised, and it relies on Windows for AC3 decoding instead of bringing its own decoder. Modern apps and games that bundle their own audio decoder are less likely to be affected.

## Who is affected

You are in scope if all of the following are true.

* The device runs Windows 11 24H2, 25H2 or 26H2.
* The device has KB5124010 installed and does not yet have KB5127648 or a later update.
* The app or game closes without an error when it plays AC3 audio, or when music starts.

If the app still crashes on a fixed build, it may have a separate problem, so check the app vendor's support pages before you continue.

## Before you start

* **Admin access.** You need local admin on the affected device to remove an update or install a codec.
* **A test device.** Pick one device that shows the crash, and keep a copy of the app's error or crash behaviour so you can compare after the fix.
* **Know the app.** Note the app name, version and what triggers the crash, such as opening a file or starting playback.
* **Check your software policy.** If you plan to install a third party codec pack, check your organisation's rules first, because a codec installed outside the standard process is an extra piece of software you have to manage.

## The steps, in order

1. **Confirm the symptom.** Reproduce the crash on the test device. Open the app, then play the audio that triggers it. Note whether the app closes with no message at all.

2. **Confirm KB5124010 is installed.** Run the following command in PowerShell on the test device.

```powershell
Get-HotFix -Id KB5124010
```

   If the command returns a result, the update is installed. If it returns nothing, the device has a different update level, so look for another cause.

3. **Check whether the fixed update is installed.** Run the same check for the fixed update.

```powershell
Get-HotFix -Id KB5127648
```

   If this returns a result, the device already has the fix, so check the app vendor and the crash logs instead. If it returns nothing, continue to the next step.

4. **Look for the crash in Event Viewer.** Open Event Viewer and go to Windows Logs, then Application. Look for an Application Error entry from the app at the time of the crash. Some reports show a fault in `msmpeg2ac3dec.dll` with exception code `0xc0000602`. Use this to confirm, but it is not required for the fix.

5. **Install the fixed update on the pilot device.** Install KB5127648 or the latest cumulative update through Windows Update, or deploy it through your normal Intune update ring. Restart the device when prompted.

6. **Test the app after the update.** Start the app again and play the audio that caused the crash. Repeat it at least three times, because a fault that depends on timing can look fixed on the first try.

7. **Use the uninstall route only if the fixed update does not help.** Removing an update also removes its security fixes, so use this only as a temporary step. Go to Settings, then Windows Update, then Update history, then Uninstall updates. Select KB5124010, choose Uninstall, then restart.

8. **Uninstall from the command line if the Settings route fails.** Open Command Prompt as administrator and run the following command, confirm when asked, then restart.

```powershell
wusa /uninstall /kb:5124010
```

   Do this only on the test device, and plan to install the fixed update as soon as possible.

9. **Install a codec as a temporary workaround.** If you cannot update straight away, one option is LAV Filters version 0.83, which provides its own audio decoders. Download the installer only from the official release page on GitHub. Run the installer and keep the default components selected, including the audio decoder components for x86 and x64.

10. **Restart the app and test.** Close the app completely, start it again and repeat the action that caused the crash. Check that the audio plays and the app stays open.

11. **Remove the codec when you no longer need it.** Go to Settings, then Apps, then Installed apps, select LAV Filters and uninstall it. Remove it as soon as the fixed update is in place and tested.

12. **Roll out the fix in rings.** Once the fixed update works on the pilot devices, include it in your normal update ring. Track the crash tickets and close them once the fixed build is confirmed.

## Verify it worked

* **Update level.** The hotfix check for KB5127648 returns a result on the affected devices.
* **App behaviour.** The app plays AC3 audio and stays open after repeated attempts.
* **Event log.** No new Application Error entries appear for the app when it plays AC3 audio.
* **Fleet.** Crash tickets for the affected app fall to zero after the fixed build is deployed.

## Roll back

If you removed KB5124010 as a temporary step, install the fixed update again once it is tested, and remove any codec you added. Do not leave a device without the security fixes for longer than you need to.

If you added LAV Filters, remove it from Installed apps once the fixed update is in place. Keep a record of the change so the codec does not stay on devices forgotten.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| The app still crashes on the fixed build | A separate problem in the app itself | Check the app vendor's support pages and ask for a version that bundles its own decoder |
| `Get-HotFix -Id KB5127648` returns nothing after an update | The update did not install, or the device is waiting for a restart | Check Windows Update history, restart and check again |
| The codec does not fix the crash | The app uses a different audio path | Remove the codec and check the app's audio settings or vendor advice |
| Removing KB5124010 fails | The update is not listed for removal | Use the command line route in step 8, or install the fixed update instead |
| Other apps stop playing audio after installing a codec | A codec conflicts with the existing audio setup | Remove the codec and restart the device |

The quickest path is to install the fixed build. Use the codec or the uninstall route only when you cannot update the device yet, and remove the temporary step once the fix is in place.

<div class="refs" markdown="1">

**References**

1. [BetaNews on KB5127648 fixing the Dolby Digital crashes in games and apps](https://betanews.com/article/windows-11-kb5127648-dolby-digital-crashes/)
2. [WinTips on apps and games crashing after KB5124010 because of AC3 audio](https://www.wintips.org/apps-and-games-crash-after-kb5124010-due-to-ac-3-audio-how-to-fix/)
3. [Windows forum on KB5127648 fixing Dolby Digital AC3 app crashes](https://windowsforum.com/news/kb5127648-fixes-windows-11-dolby-digital-ac-3-app-crashes-but-usb-audio-issues-remain.449851/)
4. [Microsoft Windows release health dashboard for Windows 11, version 25H2](https://learn.microsoft.com/en-us/windows/release-health/status-windows-11-25h2)

</div>
