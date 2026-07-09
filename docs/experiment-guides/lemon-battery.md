# Lemon Battery — Experiment Guide

**Curriculum topic:** `exp_lemon_battery`
**Age:** Y4–9 (ages 9–14)
**Equipment needed:** 2–4 lemons (or limes, oranges, or potatoes), zinc nails or galvanised nails (hardware store), copper coins (pre-1992 UK pennies are 97% copper; US pennies post-1982 are copper-plated zinc — use copper wire instead if available), a cheap multimeter (under £5 / $6), LED (3mm LED from any electronics kit), optional: alligator clip leads

---

## What the Child Is Testing

| Test | What to measure | What it reveals |
|---|---|---|
| **Single lemon** | Voltage across one lemon cell | How much electrical potential one fruit generates |
| **Two lemons in series** | Voltage across two cells connected + to – | Whether voltage adds up (it should double) |
| **Different fruits** | Voltage of lemon vs potato vs orange vs apple | Whether acidity is the key variable, or whether other factors matter |
| **LED lighting** | How many cells needed to light an LED | Practical threshold — an LED needs ~1.8–2V |

**Expected values:** A single lemon cell typically produces 0.7–1.0 V at very low current (microamps to milliamps). Two in series should light a small LED. A multimeter is better than an LED for initial testing — it shows the voltage without requiring a minimum threshold.

---

## Tutor Script — Predict, Observe, Explain

### Before starting

Ask one predictive question before any electrodes are inserted:

- "If I told you I could make electricity from a lemon, what would you say — trick, or true? What would you need to see to believe it?"
- "What do you think electricity needs to flow? Does it always need a battery or a plug?"
- "Alessandro Volta invented the first battery in 1800. He didn't use lemons — he used discs of zinc and copper soaked in saltwater. What do those have in common with what we're about to do?"

### Setting up the first cell

Insert a zinc nail and a copper coin (or strip of copper wire) into the lemon, about 3 cm apart. Do NOT let them touch inside the lemon.

1. "Why do you think we need two different metals — why not two zinc nails?"
2. Use the multimeter set to DC voltage (2V range). Touch the red probe to copper, black to zinc. Read the voltage. "What does it say? Does that surprise you?"
3. "Is that enough to power anything?"

### Connecting cells in series

Connect two lemons: copper terminal of lemon 1 → zinc nail of lemon 2 (using alligator clips or just touching leads together). Measure voltage across the entire chain.

1. "Before you measure — what do you predict the voltage will be?"
2. Measure it. "Did it add up the way you expected?"
3. Try connecting an LED. "Why do you think it might not light with one lemon but does light with two?"

### Comparing fruits

Try the same nail + copper setup in a potato, an orange, and an apple. Measure voltage.

1. "Which fruit/vegetable produced the most voltage? The least?"
2. "What's different about a lemon compared to a potato? What do you think matters more — juice content, acidity, or something else?"
3. "A potato isn't acidic — but it still works. What does that tell you about what's actually doing the chemistry?"

### The chemistry connections

**What's actually happening:** This is a redox (reduction-oxidation) reaction — arguably the most important chemical reaction in all of chemistry and biology.

The zinc nail is more reactive than the copper. In the acidic fruit juice (which conducts electricity because of dissolved ions), zinc atoms lose electrons and dissolve into the juice as Zn²⁺ ions. Those electrons travel through the external wire to the copper terminal, where hydrogen ions (H⁺) from the acid pick them up and are reduced to hydrogen gas (tiny bubbles on the copper).

- **Zinc terminal (negative/anode):** Zn → Zn²⁺ + 2e⁻ (oxidation — zinc loses electrons)
- **Copper terminal (positive/cathode):** 2H⁺ + 2e⁻ → H₂ (reduction — hydrogen ions gain electrons)
- **The fruit/vegetable:** Acts as the electrolyte — a conducting medium that allows ions to move between the two metals

**Why different metals?** The voltage produced depends on the difference in "reactivity" (more precisely, the difference in electrochemical potential) between the two metals. Zinc and copper are far apart on the reactivity series. Two zinc nails are at the same position, so there's no potential difference — no electrons want to move.

**Why acidity helps but isn't essential:** Acid provides H⁺ ions as electron acceptors, making the reaction more vigorous. But any electrolyte (salt solution, soil) will work — the H⁺ just makes it more efficient. A potato works because of its water and mineral content, not acidity.

**The historical connection:** Alessandro Volta built the first battery in 1800 — a stack of zinc and copper discs separated by cloths soaked in saltwater. He called it a "voltaic pile." The unit of electrical potential (volt) is named after him. Before the voltaic pile, electricity only existed as static sparks (static electricity) or lightning — there was no way to store or sustain a current. The battery enabled the entire electrical age that followed.

**Connection to circuit_challenge and electroplating:** The lemon battery is the same principle as every battery in every phone and laptop, just with different materials. Lithium-ion batteries use lithium (very reactive, high potential difference) and cobalt oxide, with a lithium salt solution as electrolyte. The principles Volta discovered in 1800 are unchanged.

### Bloom-level questions by age

| Age | Question | Bloom level |
|---|---|---|
| 9–10 | "Name the three things every battery needs." (two different metals, an electrolyte, and a circuit to connect them) | 1–2 — Remember/Understand |
| 10–11 | "If you connected ten lemons in series, what would happen to the voltage? What would happen to the current?" | 3 — Apply |
| 11–12 | "A potato also makes a battery. A glass of pure water does not. What does the potato have that pure water lacks?" | 4 — Analyse |
| 12–13 | "Your phone battery stores about 4000 mAh. A lemon produces roughly 1 mA. How many lemons would you theoretically need to charge a phone from flat? What's wrong with just using lemons in real life?" | 4–5 — Analyse/Evaluate |
| 13+ | "Design a battery that would last longer using the same zinc-copper-acid principle. What would you change, and why?" | 6 — Create |

---

## The Bigger Picture Questions

After the practical, connect outward:

- **To circuit_challenge and electroplating:** "The electroplating experiment uses the same basic chemistry — a metal dissolving at one electrode and depositing at another. What does the lemon battery have in common with that?"
- **To history of science:** "Before Volta's battery, scientists could only study electricity as static sparks. What experiments became possible once you could have a continuous current? (Hint: electromagnets, electroplating, electric motors all followed within 30 years.)"
- **To the reactivity series:** "The reactivity series ranks metals from most reactive (potassium, sodium) to least (gold, platinum). Why do you think expensive jewellery is always made from gold, silver, and platinum rather than zinc or iron?"
- **To energy storage:** "A car has a lead-acid battery. An electric car has a lithium-ion battery. Both use the same principle as the lemon. What do you think is different about them — why does lithium-ion store so much more energy per kilogram?"
- **To biology:** "Your heart sends electrical signals to trigger each heartbeat. That electrical signal is also driven by ion concentration differences — potassium and sodium ions moving across cell membranes, not zinc and copper. Does that make a heartbeat a kind of battery effect?"

---

## What to Log

After the session, log to the interest graph:
- Tags to add: `electricity`, `redox chemistry`, `batteries`, `electrochemistry`, `history of science`
- If the child asked about phone/laptop batteries: flag `energy storage`, `materials science`
- If the child engaged with Volta's history: flag `history of science`, `scientific discovery`
- If the child connected to electroplating or circuits: note cross-topic link (`circuit_challenge`, `electroplating`)
- If the child asked about the reactivity series: flag `inorganic chemistry`
