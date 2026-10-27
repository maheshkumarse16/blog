---
title: "Users can create agent blueprints from November: check the Entra setting now (MC1506733)"
date: 2026-10-27
author: Mahesh
type: How to
description: "Microsoft is letting ordinary users in Entra create agent blueprints by default from 4 November 2026, under message MC1506733. This step by step guide shows where the setting lives, what the default means, how to set it to No, and how to check your existing agents before the rollout reaches your directory."
tags: [Entra ID, Microsoft 365, Copilot]
---

Microsoft has announced message MC1506733, and it changes who can create agent blueprints in Microsoft Entra. Until now, a blueprint was something only administrators created. From 4 November 2026, with the rollout finishing in late November, any user without a built in or custom Entra role will be able to create one unless an administrator turns the setting off.

I checked the setting before writing this up. The setting is shown below. In the directory I checked, it is set to **No**, so ordinary users cannot create blueprints. That is the position I recommend for most organisations. The rest of this post explains what the setting does, what the default means for you, and what to check before the change reaches your directory.

<figure>
<img src="/images/2026/10/entra-agent-blueprints-setting.png" alt="Microsoft Entra admin center showing Users User settings with the Default user role permissions list. The setting Users can register agent identity blueprints is set to No and is circled in red." width="1818" height="865">
</figure>

## What an agent blueprint is

An AI agent is a program that signs in and acts using its own identity in Entra. A blueprint is the template that agent identities are built from. It defines how an agent is set up and how it signs in. Creating a blueprint is the first step in making a new agent.

That makes it a control point. Whoever can create blueprints can decide what new agent identities look like and how they authenticate, so the setting deserves the same care as the one that controls app registrations.

## What the default means for you

Microsoft's change makes the default **Yes** for ordinary users from 4 November. An ordinary user is anyone without a built in or custom Entra role. Admins and people holding the Agent ID Developer role can still create blueprints whatever the setting says.

Two things to note from the change.

* Turning the setting off does not delete blueprints or agents that already exist.
* The setting is separate from **Users can register applications**. A directory that has blocked app registrations is not automatically protected from this change, so check both settings.

## Before you start

* **Role.** You need at least the Cloud Application Administrator role to change the setting.
* **Know your current position.** Open the setting and record what it says now. The screenshot above shows **No** in the directory I checked, which means nothing changes for users until Microsoft's rollout reaches it. Yours may be different.
* **Know who holds the Agent ID Developer role.** Those people can still create blueprints even with the setting off, so you need their names before you start.
* **Decide who should create agents.** Agree the answer with the people who own agent use cases. In most organisations that is a small group, and everyone else should go through them.

## The steps, in order

1. **Open the Microsoft Entra admin center.** Sign in with an account that has the Cloud Application Administrator role or higher.

2. **Go to the user settings.** Select **Entra ID**, then **Users**, then **User settings**. The page opens on the user settings list in the centre column.

3. **Find the Default user role permissions section.** This section holds the switches that apply to ordinary users. It sits near the top of the page, below the Learn more link.

4. **Find the agent blueprint switch.** Look for **Users can register agent identity blueprints**. This is the switch shown circled in the screenshot. Microsoft's own documentation may call it **Users can create agent blueprints**. Both names refer to the same setting.

5. **Read the current value.** The switch shows Yes or No. If it shows Yes, ordinary users can create blueprints now, and you should change it. If it shows No, you are already protected from this change.

6. **Set it to No.** Turn the switch off and save. Use the same change window you use for other user setting changes, so the change is traceable.

7. **Check the app registration switch.** Look at **Users can register applications** in the same section. Set it to whatever your application governance says. This switch controls a different risk, but it is part of the same decision.

8. **Review who can create agents.** Admins and Agent ID Developers can still create blueprints. Review the assignments for those roles and check that each person still needs them.

9. **Move privileged roles to eligible.** Where you use Privileged Identity Management, assign the Agent ID Developer role as eligible rather than permanent. Users then activate it only when they need it.

10. **Inventory existing blueprints and agents.** Make a list of every agent identity blueprint and agent that exists in the directory now. For each one, record the owner, what it does and whether it is still needed. Blueprints created before the change keep working, so this list is your starting point for a review.

11. **Check the sign in and audit logs.** Look for agent sign ins and for blueprint creation events in your audit logs. Note any that come from accounts you do not expect. This gives you a baseline before the change, so you can compare later.

12. **Record the decision.** Write down the date, the value you set, who approved it and why. Add a note to review the setting every month, because Microsoft may change it again.

13. **Tell the helpdesk and service owners.** Explain that ordinary users cannot create agent blueprints, and give them a route for requests. Without this, the first person to try will open a ticket and nobody will know the answer.

## Verify it worked

* **Setting.** Reopen **User settings** and confirm that **Users can register agent identity blueprints** shows **No**.
* **Test as an ordinary user.** Sign in with a standard test account that has no Entra role and try to create a blueprint. It should be refused. If the test account can still create one, check the Default user role permissions again and confirm the change has saved.
* **Admin path.** Sign in with an admin account and confirm that the admin can still create a blueprint. This confirms the change is limited to ordinary users.
* **Inventory.** Compare the inventory from step 10 with the list of blueprints now in the directory. Any new blueprint you did not expect is a finding to investigate.

## Roll back

If a team needs ordinary users to create blueprints, you can set the switch back to Yes. Do this only with a documented reason, a named owner and a review date. Keep the decision record from step 12 up to date when you do.

Rolling back does not change anything that already exists. The inventory from step 10 still applies, so keep it current whether the switch is Yes or No.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| The switch is missing from the page | Your role does not allow you to see the setting | Sign in with an account that has the Cloud Application Administrator role or higher |
| A user can still create a blueprint after you set it to No | The change has not saved, or the user holds a role such as Agent ID Developer | Reopen the setting, then check the user's role assignments |
| The label on your page is different | Microsoft has renamed the setting in the portal | Look for the switch with the agent blueprint wording, and check the Learn more link |
| An existing agent stops working after the change | Turning the switch off does not remove existing agents, so the cause is elsewhere | Check the agent's sign in logs and its owner, then look at any recent policy change |
| You are unsure whether a blueprint is needed | The owner is no longer in the business or the use case has ended | Put the blueprint on the review list from step 10 and agree a removal date with the owner |

## Priorities for this week

Check the switch now. It takes a few minutes, and it means the change is already in place when the rollout reaches your directory. Then do the inventory and the log check, because those tell you whether anyone has already created agents you did not expect. The rest of the steps can follow on your normal review cycle.

<div class="refs" markdown="1">

**References**

1. [Microsoft message center post MC1506733 on users creating agent blueprints in Microsoft Entra](https://mc.ai-news.cz/message/MC1506733)
2. [precloud.us summary of MC1506733 with the admin steps](https://precloud.us/blog/mc1506733-entra-users-create-agent-blueprints)
3. [LazyAdmin on Microsoft Entra letting users create agent blueprints by default](https://lazyadmin.nl/office-365/microsoft-entra-lets-users-create-agent-blueprints-by-default/)
4. [Office365ITPros on the agent blueprint option](https://office365itpros.com/2026/10/15/agent-blueprint-option/)

</div>
