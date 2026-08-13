# The_First

# The First

**A branching narrative game about the first-generation college experience.**

You play a student on their first day, moving between home and school. Every choice costs something on both sides — there is no option that is simply correct. That constraint is the design, not a limitation of the writing.

Built solo in Unreal Engine 5 with all art authored in Blender, as a CSS 497 capstone at the University of Washington Bothell.

---

## The design rule

> If a choice has a costless right answer, it misrepresents a structural problem as a failure of judgement.

Research on first-generation and immigrant-origin students describes a difficulty that is *structural* — institutions run on rules nobody writes down. A game that offers an obviously correct option teaches the opposite: that you'd have been fine if you'd just chosen better.

So every branch carries a cost on both sides. Applying that rule as a test also found a bug: seventeen nodes where the player was choosing other people's reactions rather than their own action. All were rewritten.

**One example.** The first time anyone at school invites Laila out, she is also due to collect her four-year-old brother at three.

| Choice | Cost |
|---|---|
| Go — her sister covers | He waits eleven minutes at the gate |
| Decline, without explaining | They don't ask again on Thursday |
| Bring him along | She watches him all hour instead of talking |

---

## The story graph

| | |
|---|---|
| Dialogue nodes | **206** |
| Distinct root-to-ending paths | **9,396** |
| Choices per playthrough | **12–14** |
| Playthrough length | **~3–4 minutes** |
| Endings | **6** |
| Nodes that raise the Parent Anger Meter | **49** |
| Approx. words of dialogue | **5,500** |

Two playable characters at parity — **Mellad** (113 nodes) and **Laila** (92) — plus **Manuna**, who frames the day from the kitchen.

Six locations: school hallway (81 nodes), cafeteria (42), classroom (33), kitchen (23), bedroom at night (23), bathroom (4).

Every route converges on a shared homecoming sequence — morning, school, the walk home, the doorstep — so no branch is abandoned mid-story.

### Interactive flowchart

`docs/index.html` renders the whole graph in a browser: all 206 nodes laid out by beat of the day, home scenes warm and school scenes cool, with node-level path tracing and a running anger meter. It is generated from the live dialogue table, so it shows the real story rather than a diagram.

Open it directly — no server or install needed.

---

## Research grounding

Six constructs from the first-generation and immigrant-student literature shaped the writing. Each became a specific scene rather than a stated theme.

| Construct | Source | Where it appears |
|---|---|---|
| Cultural mismatch | Stephens et al., 2012 | The school-rules cluster: follow the sheet exactly and you're never in trouble, and never in the room where the real rules get explained |
| Family achievement guilt | Covarrubias & Fryberg, 2015 | The doorstep beat on every route — which version of the day you hand over |
| Family obligation | Fuligni, Tseng & Lam, 1999 | The invitation scene above |
| Language brokering | Orellana, 2009 | A walk-home option lists "a shift starting, or a sibling to collect, or a letter to translate" |
| Code-switching | Molinsky, 2007 | Borrowed cadence follows Laila onto the bus, with the front door four stops away |
| Bicultural identity integration | Benet-Martínez & Haritatos, 2005 | The endings resolve through neither assimilation nor withdrawal |

Full citations at the bottom of this file.

---

## Architecture

The story is **data, not code**. Eighty-nine nodes were added in one week without opening a Blueprint.

```
DT_DialogueNodes  (DataTable)
   206 rows: nodeId, dialogueText, choices[], speakerName, emotion, sceneName
        │
        ▼
WBP_Dialogue / WBP_Dialogue2D  (UMG)
   reads a row, resolves portrait by speaker + emotion,
   loads the scene backdrop, renders up to three choices
        │
        ▼
BP_TheFirstGameInstance
   AngerMeter · VisitedNodes · CurrentNodeID · PendingNodeID · PendingScene
```

**Two front-ends, one graph.** A 2D visual-novel mode and an explorable 3D world both read the same DataTable and write the same GameInstance, so a single story edit updates both.

**Parent Anger Meter.** Choices raise or ease it, driven by each node's emotion tag (Angry +18, Upset +10, Crying +8, Happy −6). In 2D mode it is also a fail condition: reach the threshold and the run ends early.

**Pending story handoff.** The GameInstance tracks one pending node and scene — the single place the story can continue. When a choice moves the story elsewhere, the conversation pauses and only the matching zone can resume it, so chapters fire in order and once each.

---

## Repository layout

```
Content/
  Blueprints/
    Dialogue/DT_DialogueNodes      the story graph
    BP_DialogueManager             proximity zones, pending handoff
    BP_TheFirstGameInstance        persistent state
    BP_Portal                      room-to-room doors
  UI/
    WBP_Dialogue                   3D-mode dialogue widget
    WBP_Dialogue2D                 2D visual-novel widget
    WBP_PauseMenu                  progress trail, anger meter, controls
    WBP_MainMenu, WBP_HUD
  Characters/
    Models/                        CH_Mellad, CH_Laila, CH_Manuna, CH_Avah
    Portraits/                     {Speaker}_{Emotion}, nine states
  SceneSets/                       six environment meshes + UCX collision
docs/
  index.html                       interactive story flowchart
```

---

## Running it

Requires **Unreal Engine 5.8**.

1. Clone the repo
2. Open `The_First.uproject`
3. Play from the main menu — **Play** for the 3D world, **Play 2D** for the visual novel

The 2D mode is complete. The 3D world is still in progress: rooms, doors and dialogue triggers work, while collision and layout are being finished.

---

## Notes from the build

Things worth recording, mostly because they cost time.

**Auto-generated collision cannot describe a room you walk inside.** Unreal generates a single convex hull per mesh, and a hull is solid by definition — so each imported set became a solid block. The fix was authoring collision explicitly in Blender as named `UCX_` primitives: five convex boxes per room forming a hollow shell.

**A line trace that starts inside geometry returns no hit.** My first attempt at verifying the collision fix used traces originating inside the meshes under test, so they reported clear passage regardless of the actual state. Verification had to be redone from open interior air.

**Check which mesh an actor actually references before repairing it.** A movement bug survived four correct-looking fixes because the actor in the level referenced a different mesh from the one being edited.

**PDF char-spacing persists between text blocks.** In the poster generator, letter-spacing applied to a heading silently widened every paragraph that followed it, while width measurement ignored it — so the layout logic and the render disagreed by a constant.

---

## References

Benet-Martínez, V., & Haritatos, J. (2005). Bicultural identity integration (BII): Components and psychosocial antecedents. *Journal of Personality*, 73(4), 1015–1050.

Covarrubias, R., & Fryberg, S. A. (2015). Movin' on up (to college): First-generation college students' experiences with family achievement guilt. *Cultural Diversity and Ethnic Minority Psychology*, 21(3), 420–429.

Fuligni, A. J., Tseng, V., & Lam, M. (1999). Attitudes toward family obligations among American adolescents with Asian, Latin American, and European backgrounds. *Child Development*, 70(4), 1030–1044.

Molinsky, A. (2007). Cross-cultural code switching: The psychological challenges of adapting behavior in foreign cultural interactions. *Academy of Management Review*, 32(2), 622–640.

Orellana, M. F. (2009). *Translating Childhoods: Immigrant Youth, Language, and Culture*. New Brunswick, NJ: Rutgers University Press.

Stephens, N. M., Fryberg, S. A., Markus, H. R., Johnson, C. S., & Covarrubias, R. (2012). Unseen disadvantage: How American universities' focus on independence undermines the academic performance of first-generation college students. *Journal of Personality and Social Psychology*, 102(6), 1178–1197.

---

## Credits

**Manuna Mady** — design, writing, programming, art  
Advisor: **Dr. Wooyoung Kim**  
Computing & Software Systems, University of Washington Bothell  
CSS 497 Capstone
