---
created: 2026-07-11T00:00:00
title: Minecraft Education Edition — Bedrock iPad client connecting to Java server
area: general
files: []
---

## Problem

Children using Minecraft Education Edition on iPad (Bedrock protocol) cannot
connect to Java Edition servers directly. We want to run a curriculum-aware
Java server (Paper/Spigot with educational plugins) and have iPad students
connect to it via MEE.

Additionally, the etutor server should be aware of what a child is building
in Minecraft so the AI tutor can ask Socratic questions about their choices
("why did you use that material?", "what does this redstone circuit do?").

## Known Solution — GeyserMC Stack

**Geyser** (https://geysermc.org)
- Open source proxy: sits in front of a Java server, translates Java ↔ Bedrock
  protocol in real time
- Bedrock clients (iPad, Xbox, Switch, Windows Bedrock) connect to Geyser port
- Geyser forwards to the Java server transparently
- Java server sees it as a Java client

**Floodgate** (https://github.com/GeyserMC/Floodgate)
- Companion Geyser plugin
- Lets Bedrock players authenticate without a Java account
- Passes Xbox account info through to the Java server
- Required for children who only have Xbox/Microsoft accounts

**The MEE complication**
- Minecraft Education Edition uses a modified Bedrock protocol with additional
  Microsoft Education/school account authentication layer
- Standard Geyser does not handle MEE's auth out of the box
- Options to investigate:
  1. MEE "allow non-educational accounts" setting — some versions allow standard
     Microsoft accounts, which Geyser/Floodgate can handle
  2. Geyser forks/branches that target MEE compatibility
  3. Use standard Bedrock on iPad instead of MEE — same engine, MEE is just
     a skin on top with extra auth and lesson management
  4. Run MEE as the server (MEE has a dedicated server binary) — children join
     MEE-to-MEE, no Java needed but lose Java plugin ecosystem

## etutor Integration Angle

Once children are on the server, the etutor connection could work via:

1. **Minecraft plugin → etutor API** — a Paper/Spigot plugin that:
   - Logs significant events (builds completed, deaths, crafting, commands)
   - POSTs events to etutor-server `/v1/minecraft/events`
   - etutor stores these in the session log alongside voice interactions
   - Tutor system prompt includes: "Jamie just completed a redstone circuit in
     Minecraft — ask them to explain how it works"

2. **RCON bridge** — etutor-server connects to the Minecraft server via RCON
   (remote console) to query game state or send messages to the in-game chat

3. **Curriculum-tagged builds** — structured "lessons" where children must
   complete a specific build to unlock the next topic (Roman aqueduct → water
   flow → gravity → pressure → Archimedes)

## Research Needed

- [ ] Does MEE on iPad support connecting to external servers at all?
      (MEE classrooms are usually hosted by the teacher's instance, not a
      separate server — this may be the core constraint)
- [ ] Which GeyserMC version is most stable for iPad Bedrock → Java?
- [ ] Is there a maintained MEE-compatible Geyser fork?
- [ ] What Paper/Spigot plugins exist for educational/curriculum tracking?
      (EduCraft, ClassiCube, etc.)
- [ ] Can the etutor FastAPI server be the Minecraft plugin's webhook target
      without adding significant latency to gameplay?

## Links to Investigate

- https://geysermc.org
- https://github.com/GeyserMC/Geyser
- https://github.com/GeyserMC/Floodgate
- https://education.minecraft.net/en-us/get-started/technical
- https://learn.microsoft.com/en-us/education/windows/set-up-minecraft-education
