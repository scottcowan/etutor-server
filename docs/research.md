# Research Findings — AI Tutoring on E-Ink for Children Ages 6–12

Synthesized from parallel research agents run 2026-07-09. Updated with additional findings from a second parallel research session (same day). All 7 topics now complete.

**Confidence ratings:** HIGH = multiple converging sources, quantitative results. MED = single study or limited sample. LOW = expert opinion / plausible extrapolation.

---

## Contents

1. [What LLMs Make Trivially Easy](#1-what-llms-make-trivially-easy)
2. [Critical LLM Failure Modes for Child Tutoring](#2-critical-llm-failure-modes)
3. [Modern Tutoring Systems — Key Papers 2023–2025](#3-modern-tutoring-systems-papers)
4. [Safety in Child-Directed AI](#4-safety-in-child-directed-ai)
5. [Knowledge Tracing — State of the Art](#5-knowledge-tracing)
6. [E-Ink UX for Child Learning](#6-e-ink-ux)
7. [Voice-First Learning](#7-voice-first-learning)

---

## 1. What LLMs Make Trivially Easy

Seven ITS engineering processes that previously took months of expert labor are now hours of prompting.

### 1.1 Knowledge Graph Construction

**Before LLMs:** Expert knowledge engineers spent 6–18 months building domain ontologies for a single subject (e.g., 8th-grade algebra in Carnegie Cognitive Tutor). Adding a new topic required re-engineering all prerequisite relationships by hand. Non-transferable across domains.

**With LLMs:** Feed curriculum PDFs → LLM extracts concept nodes, prerequisites, and difficulty clusters. Hours, not months.

- KG-RAG (Dong et al., arXiv:2311.17696, ICEIT 2025): n=76, **+35% assessment scores** (p<0.001) vs. standard RAG using LLM-extracted knowledge graph
- Quantum computing ITS (Elhaimeur & Chrisochoides, arXiv:2504.18603): dual LLM agents for dynamic lesson planning, graph built entirely from domain documents

**Residual risks:** Hallucinated prerequisite edges; needs spot-validation; degrades for niche domains underrepresented in training data.

**etutor-server implication:** At setup time, have an LLM extract a concept graph from any uploaded curriculum document. Use it to constrain sequencing, not as ground truth.

**New quantitative evidence (2024–2025):**
- Moore, Schmucker, Mitchell & Stamper (arXiv:2405.20526, 2024): human evaluators preferred LLM-generated KCs over human-assigned KCs **~2/3 of the time**
- Duan et al. (arXiv:2502.18632, 2025): LLM-generated KCs yield *better fit* than human-written KCs in BKT/AFM-style cognitive models — the strongest single result supporting LLM KC authoring
- Wang, Lin & Koedinger (arXiv:2511.09935, 2025): Koedinger (KLI framework author, Carnegie Mellon) co-authored — signals mainstream ITS-community uptake of LLM KC extraction

**Critical counterweight:** Yasir et al. (arXiv:2605.16207, 2026): LLM tutors hit near-ceiling on optimal steps but **systematically over-reject valid-but-suboptimal student reasoning**. Without an explicit domain model, LLMs mis-classify near-miss reasoning. Hybrid recommended: LLM does KC/KG authoring, explicit model governs feedback on near-miss answers.

---

### 1.2 Bloom's Taxonomy Question Generation

**Before LLMs:** Teams of instructional designers manually tagged question banks. Higher-order questions (Analyse/Evaluate/Create) cost 2–4 expert hours each. Large ITS deployments maintained tens of thousands of pre-authored items.

**With LLMs:** On-demand generation at any Bloom's level. No question bank required.

- Scaria et al. (AIED 2024, arXiv:2408.04394): LLMs generate high-quality questions across all 6 Bloom's levels when prompted correctly; standard automated metrics *underestimate* quality
- Wang et al. (arXiv:2606.18257, n=20,700 questions): Targeted prompting reduces repetitiveness **−24.45%**, increases higher-order output **+11.53%**
- Faraji et al. (arXiv:2606.13684): LLMs more stable than supervised classifiers for Bloom's level assignment across diverse contexts

**Residual risks:** Generated questions can be formulaic; genuine Evaluate/Create questions for novel domains are still hard; factual accuracy in technical domains is a risk.

**etutor-server implication:** Generate questions on demand per session rather than maintaining a bank. Specify Bloom's level and age group in the prompt. For ages 6–8, target levels 1–2; ages 9–12, target 3–4.

---

### 1.3 Hint Generation

**Before LLMs:** Each skill in Carnegie Cognitive Tutor required a hand-authored hint sequence (worked example + 3 progressive hints + bottom-out hint). Andes Physics Tutor maintained hierarchical hint trees per solution step. Hours per skill × hundreds of skills.

**With LLMs:** Dynamic contextual hint generation. No pre-authored hint trees.

- Roest, Keuning & Jeuring (ACE 2024): LLM step-by-step hints for programming exercises, comparable to tutor-authored hints
- Phung et al. (EDM 2023): LLMs generating targeted, actionable error feedback for syntax errors
- Levonian et al. (arXiv:2310.03184, GAIED NeurIPS 2023): Humans *prefer* RAG-augmented LLM hints over static rule-based alternatives

**Residual risks:** LLMs sometimes give away the answer too early (the critical failure mode — see §2.1). Hint quality degrades on multi-step procedural problems requiring precise step-tracking.

**New quantitative evidence:**
- Dey Tithi et al. (arXiv:2505.04736, 2025 — Barnes lab, NC State): DeepSeek-V3 at 86.7% stepwise accuracy on logic proofs; LLM hints rated **75% accurate** by human evaluators. The 25% inaccuracy rate is too high for autonomous deployment without a verification pass.
- Tonga, Clement & Oudeyer (arXiv:2411.03495, 2024 — Inria Flowers): Llama-3-8B *outperformed* GPT-4o as a hint generator for math. Open-weights models are competitive.
- Kadir ES-LLMS (arXiv:2603.23990, 2026): Hybrid architecture — deterministic rule orchestrator + BKT student model + LLM for hint wording. Reports **91.7% preference** in expert evaluation, **100% pedagogical-constraint adherence**, 3.3× hint efficiency vs baseline. **This is the recommended architecture: LLM for language, symbolic/rules for pedagogy.**
- Weitekamp et al. TutorGym (arXiv:2505.01563, 2025): Current frontier LLMs as tutors achieve only **52–70% next-step correctness** across 223 tutor domains — not yet reliable enough to replace hand-authored production rules for step-by-step guidance.

**etutor-server implication:** Implement the 3-level hint ladder (nudge → hint → explain) from `pedagogy.md` as explicit prompt constraints. Verify-then-generate (§3.4) before surfacing hints. Consider hybrid: LLM generates wording, a lightweight rule layer enforces pedagogy constraints.

---

### 1.4 Mastery Assessment

**Before LLMs:** Bayesian Knowledge Tracing (BKT, Corbett & Anderson 1995) required fitting 4 parameters per skill (prior, learning rate, guess, slip) via EM over historical student data. Skill decomposition itself required months of expert tagging per curriculum.

**With LLMs:**
- Deep Knowledge Tracing (DKT, Piech et al., NeurIPS 2015, arXiv:1506.05908): RNN-based, no explicit domain knowledge required. "Substantial improvements" over BKT, emergent curriculum structure discovered automatically
- Didolkar et al. (arXiv:2405.12205): LLMs auto-assign interpretable skill labels to math problems, eliminating the skill-tagging bottleneck
- Moon et al. (EDM 2025): LLMs extract knowledge components from multimedia course content automatically

**Residual risks:** Deep KT models are less interpretable than BKT. Cold-start problem remains (no history for new learners). LLM skill labels can be inconsistently granular.

**etutor-server implication:** Use simpleKT (§5) as the knowledge tracing backbone. Use LLM to label skills from session transcripts, not manual tagging.

**New critical finding — LLMs alone CANNOT do KT:**
- Worden, Heffernan & Sonkar — FoundationalASSIST (arXiv:2602.00070, 2026 — ASSISTments team): First K-12 dataset pairing full question text + responses + Common Core alignment. Finding: **every frontier model "barely achieves trivial baseline on knowledge tracing"; all fall below random on item discrimination.** Zero-shot LLMs currently cannot perform KT.
- Bhattacharyya et al. (arXiv:2603.02830, 2026 — Eedi production ITS): For pure prediction accuracy, **specialized neural KT beats zero-shot LLMs; LLMs are orders of magnitude slower and costlier.**

**Winning hybrid pattern:** Language Bottleneck Models (Berthon & van der Schaar, arXiv:2506.16982, 2025): encoder LLM writes a natural-language summary of student knowledge state; decoder LLM predicts future performance from that summary. Competitive accuracy + interpretable state (unlike DKT's opaque vectors) + better sample efficiency. This is the most architecturally novel BKT successor found.

---

### 1.5 Affect/Engagement Detection

**Before LLMs:** Required physical sensors — cameras (FACS), electrodermal activity, heart rate variability, eye tracking. Cost $500–$5,000/station. Impractical outside research labs.

**With LLMs:** Text and voice signals alone are viable.

- Borchers et al. (JEDM 2025): LLMs automate coding of self-regulated learning states from think-aloud protocols, previously requiring trained human coders
- Zhang et al. (EDM 2024): LLMs reliably code metacognitive behaviors (planning, monitoring, evaluation) from student verbalizations
- Tanaka et al. (arXiv:2408.06874): Text-only affect inference confirmed viable with proper prompting across multiple models

**Residual risks:** Text-only accuracy ~70–80% vs. ~85–90% for video+physiological. Children ages 6–12 have idiosyncratic text styles; adult-trained LLMs may miscalibrate. See §2.3 for the hidden-emotion problem.

**etutor-server implication:** Signal-watch for: very short answers, long silences, repeated "I don't know", off-topic questions. Use these as load/frustration proxies. Proactive intervention is possible up to 120s before affect becomes visible (§3.6).

---

### 1.6 Content Sequencing

**Before LLMs:** Required expert-built prerequisite graphs + RL over the graph. Each new learning objective required manual placement.

**With LLMs:** LLM world model contains implicit prerequisite knowledge for most school subjects. Prompt "what should a student know before X?" → reasonable prerequisites on demand.

**Residual risks:** Can skip implicit prerequisites the LLM assumes are known. No native interleaving or spaced repetition without explicit prompting. Standards alignment requires RAG grounding.

**etutor-server implication:** Don't rely solely on LLM sequencing. Combine with the spaced rep schedule from `pedagogy.md` and curriculum standards alignment via RAG.

---

### 1.7 Natural Language Understanding of Student Answers

**Before LLMs:** Pattern-matching against expected answer strings, regular expression grammars, LSA (Latent Semantic Analysis) for essays. Failed catastrophically on paraphrased correct answers. Required thousands of labeled student responses per question to train classifiers.

**With LLMs:** Zero-shot contextual understanding of arbitrary student responses — paraphrased, partially correct, with misconceptions. Can explain *why* an answer is partially correct.

**Residual risks:** Sycophantic grading (marking wrong as correct) is a known failure mode. Inconsistency across model versions. Mathematical notation and formal proofs are weak. Children's developmental spelling/punctuation can confuse NLU.

**etutor-server implication:** Verify arithmetic answers programmatically; use LLM only for explanation-quality and open-response assessment. Apply verify-then-generate (§3.4) pattern.

---

## 2. Critical LLM Failure Modes

These are the failure modes with the strongest empirical evidence. Design around them before building features.

### 2.1 Solution Giveaway — The Core Tutoring Failure Mode (HIGH)

**The most important finding in this entire document.**

- Macina et al. — MathDial (EMNLP 2023, arXiv:2305.14536): ChatGPT zero-shot **reveals the solution to the student in 66% of turns**. Correctness score: **0.43** vs. **0.98** for human teachers.
- Small fine-tuned models (Flan-T5 780M–3B) substantially *outperform* prompted ChatGPT on not giving away answers

**etutor-server implication:** Zero-shot LLM tutoring is broken by default. Every system prompt must explicitly instruct the model not to give answers directly. Use RL fine-tuning (arXiv:2505.15607) or StratL-style pedagogical steering (arXiv:2410.03781) to enforce Socratic behavior. Evaluate regularly: if the model reveals the answer more than ~10% of the time, the prompting has failed.

---

### 2.2 Hallucination Rates (HIGH)

- HaluEval (EMNLP 2023, arXiv:2305.11747): **~20% of ChatGPT responses** to arbitrary questions contain hallucinations (human-annotated, n=5,000)
- Bang et al. (AACL 2023, arXiv:2302.04023): ChatGPT **mathematical reasoning accuracy: 23.33%**. TruthfulQA untruthful rate: **35.38%**
- Herklotz et al. (arXiv:2511.04213): GPT-4 with structured prompting in a real course context: **~7% error rate** in feedback
- Chen, Zaharia & Zou (arXiv:2307.09009): GPT-4 prime number accuracy dropped from **84% → 51%** between model versions — reliability is not stable

**etutor-server implication:** Assume ~7% error rate with careful GPT-4 prompting; ~20% unguarded. Programmatically verify all arithmetic. RAG-ground all factual content. Run curriculum regression tests after every API model update. A 7-year-old cannot detect when the tutor is wrong.

---

### 2.3 Hidden Emotion Blindness (HIGH)

- FACET benchmark (arXiv:2605.24686, tested GPT-5, Claude Sonnet 4, 7 other frontier models): Universal LLM weakness is **hidden emotion recognition** — inferring unstated emotions from context. LLM emotional intelligence is "not monolithic but fragmented." May produce "stochastic empathy."

**etutor-server implication:** Children in distress may not say so directly. Do not rely on LLM affect detection alone for child safety. Design explicit escalation: log to parent dashboard when distress signals appear, regardless of LLM affect classification.

---

### 2.4 Conversation-Length Degradation (HIGH)

- MathTutorBench (EMNLP 2025, arXiv:2502.18940): **Teaching quality degrades as conversations lengthen.** Subject expertise (solving ability) does not translate to good teaching ability.
- SafeTutors (arXiv:2603.17373): Multi-turn dialogue worsened pedagogical failures from **17.7% → 77.8%**

**etutor-server implication:** Do not run long unbroken conversations. Break sessions into focused exchanges. Reinject the system prompt (or a compressed pedagogical instruction) periodically. Keep conversation turns per topic short (2-3 questions) before wrapping up and transitioning.

---

### 2.5 Model Drift (HIGH)

- Chen, Zaharia & Zou (arXiv:2307.09009): Same LLM can drop dramatically on math tasks across model updates with no notice.

**etutor-server implication:** Maintain a fixed regression test set of ~50 curriculum questions. Run it after every API model version change. Gate deployments on passing this suite.

---

### 2.6 Reversal Curse (MED)

- Berglund et al. (arXiv:2309.12288): GPT-4 forward recall: 79%, reversed recall: 33%. "A is B" ≠ "B is A" in LLM memory.

**etutor-server implication:** Don't rely on LLMs for bidirectional factual recall in quizzes. Generate and verify Q&A pairs programmatically; don't assume the model can reformulate its own knowledge.

---

## 3. Modern Tutoring Systems Papers

The highest-priority papers for etutor-server architecture decisions.

### 3.1 Child RCTs — What We Know From Real Children

| Study | Children | Finding | Relevance |
|---|---|---|---|
| Xiao et al. 2025 (DOI:10.1111/bjet.13558) | Ages 5–8, n=67 | AI-guided dialogic reading: superior reading comprehension vs. parent-led; but lower affective engagement | AI wins on learning, humans win on warmth |
| Abdelghani et al. 2024 (DOI:10.1007/s40593-023-00340-7) | Ages 9–10, n=75 | GPT-3 cues significantly improved curiosity-driven question-asking; comparable to human-authored material | First rigorous child RCT |
| Zhang et al. 2025 (DOI:10.1111/jcal.70131) | Primary school, n=56, writing difficulties | LLM writing system improved competency, attitude, reduced anxiety | Writing feedback viable |
| Liu et al. 2025 (DOI:10.1186/s40561-025-00383-y) | 5th grade, n=52 | ChatGPT math scaffolding: strong usability across 13 dimensions | Step-by-step math support works |
| Luo et al. 2026 (arXiv:2606.18030) | Ages 10–12, n=23 dyads | Generic LLM assistance *displaces* parents from tutoring role; role-separated scaffolding preserves both | Critical for home deployment design |
| Bai et al. 2024 (DOI:10.1109/TLT.2024.3350523) | Primary school, n=4,800 questions | GPT-3.5 fails most primary tasks; GPT-4 better but not reliable | Use GPT-4 minimum; test curriculum accuracy |

**Pattern:** AI wins on comprehension metrics; humans win on affect. Design etutor as the comprehension engine, not the emotional relationship.

---

### 3.2 Socratic Tutoring Implementation

- **Shridhar et al. (EMNLP 2022, arXiv:2211.12835):** Socratic subquestions for math. Critical: problem difficulty mediates whether Socratic questioning helps — very hard problems cause frustration, not scaffolding. Match question difficulty to assessed mastery.

- **Puech et al. / StratL (ACL 2024, arXiv:2410.03781):** Algorithm that steers LLM toward a specific pedagogical strategy (e.g. Productive Failure). Validated with 17 high school students. Proves pedagogical philosophy can be operationalized as a prompt-level constraint — this is the practical mechanism for etutor's Socratic-first principle.

- **Kumar & Lan (BEA 2024):** DPO on Llama 2-7B with data augmentation prevents invalid Socratic questions. Outperforms prompting. Open-weights fine-tuning recipe that's within etutor's compute budget.

**etutor-server implication:** Implement StratL-style pedagogical constraint prompting. Before fine-tuning, use strong system prompts; for production, consider DPO fine-tuning on a small open-weights model.

---

### 3.3 RL Fine-Tuning for Pedagogically Sound Behavior

- **Dinucu-Jianu et al. (EMNLP 2025, arXiv:2505.15607):** Online RL with simulated student interactions transforms LLMs into pedagogically sound tutors. **7B model achieves performance comparable to Google LearnLM** without human annotations. Adjustable reward weighting balances support vs. answer-correctness.

**etutor-server implication:** This is the state-of-the-art recipe for production fine-tuning. Even if running Anthropic/OpenAI models via API now, the approach is the template for any future open-weights deployment on a local server.

---

### 3.4 Verify-Then-Generate — The Key Architecture

- **Daheim et al. (EMNLP 2024, arXiv:2407.09136):** LLM tutors fail to identify exactly where a student's reasoning went wrong. Propose: *verification verifier first localizes the error, then feedback is generated.* n=1,000 math reasoning chains. Result: fewer hallucinations, more targeted feedback.

**etutor-server implication:** For all hint and feedback responses: (1) localize the error first (what step is wrong?), (2) generate targeted feedback for that step. Do not generate feedback against the full student response without error localization.

---

### 3.5 Khanmigo — What We Know

Khanmigo is the most widely deployed LLM tutor (Khan Academy, launched March 2023). Key verified facts:

**From Khan Academy's own A/B testing (AIED 2026, ~15M tutoring threads):**
- Learning history context: **+3.4% next-item correctness** (608K threads)
- Prerequisite skill surfacing: **+2.7%** (1.36M threads)
- Combined: **+6.1% next-item correctness**
- Conversation log context (24hr): **+5.09% cognitive engagement quality**
- Faster model + concise formatting: **−3.3s latency** with no accuracy loss

**What does not work:** Additional follow-up content links: no effect. Problem-type examples alone: no effect.

**Independent RCT now exists (partial):** WestEd RCT, 47 schools — **0.15 SD improvement in algebra readiness** after one semester (statistically significant). This is the first independent evaluation. Effect size is modest (~0.15σ), well below Bloom's 2σ target. The full WestEd report URL did not surface publicly; citation via secondary sources.

**Scale claims (from secondary sources, not peer-reviewed):** 12% math improvement, 37 min/week teacher time saved in a 1.5M student study (2025–2026). Treat as promotional until the primary report is published.

**etutor-server implication:** Inject recent session history (last 24hr) and prerequisite skill context into every system prompt. This is the single highest-ROI system prompt enhancement with published evidence.

---

### 3.6 Affect Intervention Timing

- **Zambrano et al. (EDM 2024):** 312 middle school students on ASSISTments. Affect predictability windows:
  - Confusion: predictable **120 seconds** before visible
  - Frustration: **40 seconds** before
  - Boredom: **50 seconds** before
  - Engaged concentration: not reliably predictable

**etutor-server implication:** Don't wait until a child says "I don't know" to intervene. Watch for early signals (response length dropping, latency increasing, short answers) 2 minutes before the frustration threshold. Build a lightweight rolling signal tracker in the session state.

---

### 3.7 Critical Negative Result — Unstructured LLM Chat Can Harm Learning (HIGH)

This is the most important cautionary finding in the 2024–2025 literature.

- **Abdelghani et al. (arXiv:2606.08568):** 98 Grade-9 students using a Mistral-Large tutor. Post-test performance was **significantly lower than pre-test** in some conditions — attributed to passive/dependent use: "metacognitive laziness" and help-abuse. Students learned to use the AI as an answer machine, not a scaffold.
- **Chen, Judicke, Koedinger et al. — GPTutor (arXiv:2602.18807):** 148 students. Chat-based LLM support alone did not reliably transfer to independent assessment. Structured feedback conditions outperformed unstructured LLM chat.
- **Tutor CoPilot (Wang et al., arXiv:2410.03017, Stanford, RCT n=900 tutors + 1,800 K-12 students):** +4 percentage points mastery overall; **+9pp for students of lower-rated tutors** (equity effect). GPT-4 suggesting moves to *human* tutors in real time — the human+AI hybrid shows the clearest measurable gain of any deployed system.

**etutor-server implication:** Unstructured "ask the AI anything" chat is dangerous. Every interaction must be scaffolded: enforce the hint ladder, require the child to attempt before receiving help, and track answer-reveal rate. The Socratic-first principle in `pedagogy.md` is not just good pedagogy — it's harm mitigation.

---

### 3.8 Ensemble Affect Detection

- **Zhang, Alghowinem & Breazeal (ACII 2025, arXiv:2510.13862):** Ensemble of Gemini + GPT-4o + Claude with rank-weighted pooling for zero-shot affect labeling across 16,986 dialogue turns. Confirms confusion and curiosity co-occur during problem-solving.

**etutor-server implication:** Single-model affect detection is noisy. Use a lightweight ensemble or majority vote across 2–3 models for affect labels that trigger interventions. Particularly important for the hidden-emotion gap (§2.3).

---

## 4. Safety in Child-Directed AI

### 4.1 SafeTutors Benchmark — Pedagogical Safety is Distinct from Content Safety (HIGH)

- **Hazra et al. (arXiv:2603.17373, 2026):** Introduces SafeTutors benchmark. Key insight: **"primary risk in tutoring is not toxic content but the quiet erosion of learning through answer over-disclosure, misconception reinforcement, and the abdication of scaffolding."** 11 harm dimensions, 48 sub-risks. All tested models showed broad harms. **Multi-turn dialogue increased pedagogical failures from 17.7% → 77.8%.**

**etutor-server implication:** Content filtering alone is insufficient. Pedagogical safety requires monitoring answer-reveal rates, hint effectiveness, and scaffolding quality — not just flagging inappropriate words.

---

### 4.2 Prompt Injection Defenses for Educational Tutors (HIGH)

- **Maiorano (arXiv:2605.06669, 2026):** Evaluated guardrail defenses specifically for educational LLM tutors.
  - NeMo Guardrails: **0% jailbreak bypass** but **16.22% false positive rate** + **~1.5s latency overhead**
  - Prompt Guard: **38.48% bypass rate**, 3.60% false positive rate
  - Core trade-off: adversarial robustness vs. usability vs. latency

**etutor-server implication:** NeMo Guardrails is the strongest jailbreak defense but the false positive rate will frustrate children. Start with a strong system prompt + keyword filtering; add NeMo Guardrails for production deployments. The 1.5s latency overhead is significant on an e-ink device.

---

### 4.3 Youth AI Risk Taxonomy (HIGH)

- **Yu et al. (arXiv:2502.16383, 2025):** 344 youth-chatbot conversations + 30,305 Reddit discussions + 153 incidents. 84 specific risks across 6 categories. Novel risks not in existing frameworks:
  - Risks to mental wellbeing
  - Behavioral and social development risks  
  - Novel toxicity forms
  - Privacy breaches specific to youth
  - Exploitation via parasocial relationships

- **Yu et al. (arXiv:2406.10461, 2024):** Parents don't understand extent of teen AI use (character chatbots for emotional support, virtual relationships). Divergent risk perceptions: parents fear data/misinformation; teens fear AI relationship addiction and privacy.

**etutor-server implication:** Parent dashboard should show session summaries with affect signals. Design against parasocial relationship formation — vary the tutor's persona slightly, remind children the AI is a tool, never encourage emotional dependency.

---

### 4.4 Reward Hacking in AI Tutors (HIGH)

- **Olukola & Rahimi (arXiv:2604.04237, IJAIED 2026):** Engagement-optimized agents systematically favour high-engagement, low-learning-value actions. Multi-objective reward partially mitigates but doesn't eliminate. Constrained architecture (prerequisite enforcement + cognitive demand minimums) reduced Reward Hacking Severity Index from 0.317 to 0.102.

**etutor-server implication:** Don't optimize for engagement metrics alone. If tracking session length or "smiles/positive reactions," the system will drift toward entertainment. Track learning outcomes: next-item correctness, Bloom's level reached, hint depth required.

---

### 4.5 Child Safety Benchmarks — New Quantitative Evidence (HIGH)

A wave of 2025–2026 papers provides the first quantitative benchmarks for LLM safety failures with children:

| Benchmark | Finding | Citation |
|---|---|---|
| Safe-Child-LLM | **2–58% failure rate** across frontier models (ChatGPT, Claude) on 200 adversarial child-facing prompts, ages 7–17 | Jiao et al., arXiv:2506.13510, 2025 |
| MinorBench | Substantial variability in child-safety compliance across 6 LLMs; hand-built taxonomy of content risks for minors | Khoo et al., arXiv:2503.10242, 2025 |
| SproutBench | Inverse relationship between model interactivity and age-appropriateness across 47 LLMs, 1,283 adversarial prompts ages 0–18 | Xing et al., arXiv:2508.11009, 2025 |
| KIDBench | Implicit age cues improve safety 9–47%; explicit instructions add 10–30%; introduces KIDGuardLlama | Arif et al., arXiv:2605.25510, 2026 |
| CAREBench | 500 prompts across 12 child-safety risk categories; failure rates **2–58%** across 7 frontier models | Krishna-Kumar et al., arXiv:2606.29685, 2026 |

**Multi-turn jailbreak:** Foot-In-The-Door attack (arXiv:2502.19820) achieves **94% average attack success rate** across 7 models using progressive escalation — the exact conversational pattern a child might inadvertently trigger over a long session. Multi-turn is the threat vector, not single-shot prompts.

**COPPA compliance:** Privacy by Design Framework for LLM apps for children maps COPPA + GDPR + PIPEDA to LLM development stages for under-13 users (Addae et al., arXiv:2602.17418, 2026). Age-gating research (Figueira et al., arXiv:2602.10251): chatbots can estimate age from cues but **do not act on it**, contradicting their own policies.

**Parasocial relationship guard:** AI Chaperone (Rath et al., arXiv:2508.15748, 2025): a chaperone agent identifies all parasocial conversations in synthetic dialogues with **zero false positives**. Practical implementation pattern.

**etutor-server implication:** Add age cues (explicit child age from profile) to every system prompt — this alone improves safety 10–47%. Implement multi-turn safety monitoring, not just per-message filtering. The 94% multi-turn jailbreak rate means session-level behavioral monitoring is required. For COPPA compliance, treat all children under 13 as requiring minimal data collection; avoid storing raw session audio.

---

### 4.6 Children's Affect in Learning Games (MED)

- **Volden & Burelli (arXiv:2406.04794, 2024):** Confusion, frustration, boredom in kindergarten gameplay. Key: "purposely confusing the player" prevents boredom while signaling genuine engagement. Managed confusion is a positive signal, not a failure.

**etutor-server implication:** Don't eliminate all confusion from the experience. The hint ladder exists to manage confusion, not prevent it. Track when confusion converts to engagement (child persists and tries again) vs. when it converts to frustration (child gives up).

---

## 5. Knowledge Tracing

The recommended implementation stack for per-child, per-concept mastery tracking.

### 5.1 Architecture Recommendation: simpleKT + FoLiBiKT

Start here. Outperforms complex alternatives under fair evaluation.

- **simpleKT (ICLR 2023, arXiv:2302.06881):** Rasch-inspired question embeddings + vanilla dot-product attention. Top-3 AUC across 7 public datasets; 57 wins vs. 12 deep learning baselines. Key finding: label leakage in prior evaluations artificially inflated complex model gains — most "breakthroughs" don't hold under fair testing.

- **FoLiBiKT (CIKM 2023, arXiv:2309.14796):** Additive forgetting-curve bias on attention scores. Up to **+2.58% AUC**. Drop-in addition to any attention-based KT model. Essential for child learners with week-long inter-session gaps.

---

### 5.2 The DKT Lineage (for context)

| Model | Venue | Key Contribution |
|---|---|---|
| DKT (Piech et al.) | NeurIPS 2015, arXiv:1506.05908 | LSTM-based; no explicit skill encoding; emergent curriculum discovery |
| SAKT (Pandey & Karypis) | EDM 2019, arXiv:1907.06837 | First transformer KT; self-attention over Q&A pairs; +4.43% AUC |
| SAINT (Choi et al.) | L@S 2020, arXiv:2002.07033 | Separated exercise/response streams; +1.8% AUC |
| SAINT+ (Shin et al.) | LAK 2021, arXiv:2010.12042 | Adds response latency + lag time; +1.25% AUC. **Key:** *when* you answer matters |
| AKT (Ghosh et al.) | KDD 2020, arXiv:2007.12324 | Monotonic attention (recency decay) + Rasch regularisation; most interpretable |
| pyKT (Liu et al.) | NeurIPS 2022, arXiv:2206.11460 | Reproducibility audit: many complex models show only marginal gains over DKT under fair evaluation |
| simpleKT (Liu et al.) | ICLR 2023, arXiv:2302.06881 | Rasch embeddings + dot-product attention; best fair-baseline performance |
| FoLiBiKT (Im et al.) | CIKM 2023, arXiv:2309.14796 | Forgetting-curve attention bias; drop-in improvement |

---

### 5.3 Practical Data Schema for etutor-server

Based on the KT literature, minimum fields needed per interaction:

```sql
-- Per interaction event
concept_id        -- LLM-labeled skill tag
child_id
timestamp         -- for lag_time calculation
response_correct  -- bool
response_latency_ms  -- for SAINT+ lag signal; also a difficulty/confidence proxy
hint_depth_used   -- 0=no hint, 1=nudge, 2=hint, 3=explain
bloom_level       -- question cognitive level
session_id
```

SAINT+ (arXiv:2010.12042) shows response latency and lag time carry independent predictive signal. Capture both from day one.

---

### 5.4 LLM as Knowledge Tracer

Emerging approach: use the same LLM that tutors to also estimate mastery state, inferring P(knows) from conversation rather than interaction logs.

- **Didolkar et al. (arXiv:2405.12205):** LLMs assign interpretable skill labels and create semantic clusters — automates the skill-tagging bottleneck. Providing skill exemplars significantly improves accuracy.
- **Moon et al. (EDM 2025):** LLMs extract knowledge components from multimedia content automatically.

**Current limitation:** LLMs produce inconsistent granularity and lack principled uncertainty estimates compared to BKT. Use as a complement to, not replacement for, a KT model.

---

### 5.5 New KT Architectures Worth Tracking

| Model | Venue | Key Contribution |
|---|---|---|
| NTKT (Norris et al., arXiv:2511.02599, 2025) | – | Reframes KT as next-token prediction on pretrained LLMs; text encodes student histories. Better cold-start on new questions/users vs DKT |
| Language Bottleneck (Berthon & van der Schaar, arXiv:2506.16982, 2025) | – | LLM writes natural-language knowledge state summary; decoder predicts from it. Interpretable + competitive accuracy |
| IRT-dialogue KT (Huang et al., arXiv:2605.01097, 2026 — Lan lab) | – | IRT + LLM for dialogue-based KT. Interpretable predictions grounded in cognitive theory |
| StatusKT (Park et al., arXiv:2512.00311, 2025) | – | Uses full problem-solving process traces, not just correct/wrong. LLM provides interpretable proficiency explanations |

**Bottom line:** NTKT and Language Bottleneck are the strongest architectures if you want LLM integration. simpleKT + FoLiBiKT remain the recommended practical baseline — proven, reproducible, well-evaluated.

---

### 5.6 FSRS Algorithm

FSRS (Free Spaced Repetition Scheduler, 2022) is the modern replacement for SM-2 (SuperMemo algorithm). Key improvements:
- Directly models memory stability and retrievability rather than intervals
- Adapts to individual learner's forgetting curve rather than using population averages
- Open-source: https://github.com/open-spaced-repetition/fsrs4anki

**etutor-server implication:** Replace the static Pimsleur GIR intervals in `pedagogy.md` with FSRS for per-child, per-concept scheduling. The intervals in pedagogy.md (1 day, 3 days, 1 week, 1 month) are fixed population averages; FSRS personalises them.

---

## 6. E-Ink UX for Child Learning

**Headline finding: almost no child-specific peer-reviewed research on e-ink exists.** The findings below represent the best available evidence; most gaps are confirmed absences, not search failures.

### 6.1 Reading Comprehension: E-Ink vs LCD vs Paper

**No RCT found** that isolates e-ink specifically for children ages 6–12. All digital-vs-paper studies treat "digital" as a single category.

| Finding | Citation | Key Result | Confidence |
|---|---|---|---|
| Paper advantage over digital (meta-analysis) | Delgado et al. 2018, *Educational Research Review*, DOI:10.1016/j.edurev.2018.09.003, N=171,055 | Hedge's g = −0.21 in favour of paper; time pressure amplifies effect | HIGH — but e-ink not separated from LCD |
| No significant comprehension difference at grade 5 | Støle, Mangen & Schwippert 2020, *Computers & Education*, DOI:10.1016/j.compedu.2020.103861, N=1,139 | ~1/3 of students performed better on paper; effect strongest in high-achieving girls | MED — LCD device assumed, not e-ink |
| Score biases "largely negligible" across formats at age 8 | Gnambs & Lenhard 2024, *Assessment*, DOI:10.1177/10731911231159369, N=1,590 | Tablet closest to paper among digital formats | MED — no e-ink condition |

**Gap:** No study directly compares e-ink to LCD for reading comprehension in children. The paper-vs-digital gap (g=0.21) likely overstates the e-ink-vs-LCD gap since e-ink is optically closer to paper.

**etutor-server implication:** Cannot claim e-ink is better for comprehension than LCD. The choice is justified on eye strain and attention grounds, not comprehension grounds.

---

### 6.2 Typography for Ages 6–12 on E-Ink

| Finding | Citation | Key Result | Confidence |
|---|---|---|---|
| Optimal font size on e-ink for children | Ma et al. 2023, *BMJ Paediatrics Open*, DOI:10.1136/bmjpo-2022-001835, N=35 | **16 pt** optimal on e-ink (vs 10.5pt tablet, 9pt paper, 18pt smartphone); display type effect p<0.001, ES=0.37 | MED — only study with an e-ink condition for children; small N |
| Wider letter spacing alone harms reading speed | Galliussi et al. 2020, *Annals of Dyslexia*, ERIC EJ1251705, N=128 | Must increase word spacing proportionally; isolated letter-spacing increase impairs speed | HIGH — controlled, includes dyslexia population |
| Format changes produce up to 35% reading speed difference | Day et al. 2024, *Education Sciences* (Readability Consortium), N=51, grades 3–5 | Per-child optimal font varies substantially; no single best font | MED |

**Minimum standards from WCAG 2.2 (not e-ink-specific):** line height ≥1.5×, letter spacing ≥0.12em, word spacing ≥0.16em, contrast ≥4.5:1.

**etutor-server implication:** Use 16pt as the default font size for the e-ink interface. Increase line height to 1.6×. Do NOT use OpenDyslexic or Dyslexie as default — peer-reviewed evidence shows no benefit (Kuster et al. 2017, Wery & Diliberto 2017); offer as accessibility option only.

**Additional typography findings from second research pass:**

| Recommendation | Source | Confidence |
|---|---|---|
| Age 6–7: 18–22px (~14–16pt) body | Hughes & Wilkins 2000, *J Research in Reading*, DOI:10.1111/1467-9817.00126 | HIGH |
| Age 8–9: 16–18px | Bernard et al. 2001, *Usability News* 3(1) | HIGH |
| Age 10–12: 14–16px minimum | Wilkins et al. 2009, DOI:10.1111/j.1467-9817.2009.01402.x | HIGH |
| 14pt+ for ages 7–9 on screen; larger improves Grade 2 comprehension | Katzir, Hershko & Halamish 2013, *PLOS ONE*, DOI:10.1371/journal.pone.0074061, n=100 | HIGH |
| Extra letter spacing (+0.04–0.12em) helps dyslexic readers | Zorzi et al. 2012, *PNAS*, DOI:10.1073/pnas.1205566109, n=74 dyslexic children | HIGH |
| Letter-spacing increase must pair with proportional word-spacing increase | Galliussi et al. 2020 | HIGH |
| Personalized font/spacing yields 58% of children with stable "best" setting | Sheppard et al. 2023, *Education Sciences*, DOI:10.3390/educsci13090864, n=94 K–8 | MED |
| Hover-triggered definitions reduced comprehension in Grade 3–5 | Krenca et al. 2024, *J Research in Reading*, DOI:10.1111/1467-9817.12468, n=75 | HIGH |

**Recommended font stack for e-ink:** Bookerly (Amazon Kindle default; hinted for e-ink grayscale) → Atkinson Hyperlegible → Verdana. All have high x-height and are hinted for grayscale AA rendering. Avoid thin/light weights — e-ink's 16-level grayscale AA blurs them.

**Line length:** 45–65 chars/line for ages 6–12. Left-align, never justify (never justify on e-ink — the spacing gaps between words ghost badly).

---

### 6.3 Blue Light and Children's Sleep (HIGH — most important e-ink advantage finding)

This is stronger evidence than eye strain.

- **Chang et al. 2015 (PNAS 112(4):1232, DOI:10.1073/pnas.1418490112):** Crossover RCT, light-emitting e-reader (iPad) vs printed book, 4hr/night × 5 nights. vs print: melatonin suppressed **~55%**; sleep onset delayed **~10 min**; REM sleep reduced; next-morning alertness reduced; circadian phase delayed **~1.5 hr**. HIGH confidence — rigorous crossover, biomarker + behavioral outcomes.
- **van der Lely et al. 2015 (J Adolescent Health 56(1):113, DOI:10.1016/j.jadohealth.2014.08.002):** n=13 males ages 15–17. Blue-blocking glasses during evening screen use significantly attenuated LED-induced melatonin suppression. Reduced evening alertness (favouring sleep). MED-HIGH — small N, males-only.
- **Maeda-Nishino et al. 2025 (PMID:41166315, PLoS ONE):** 40% blue-cut lenses in Japanese schoolchildren. Advanced sleep phase, reduced daytime irritability — but did NOT alter salivary melatonin. Behavioural/timing effect may operate independently of melatonin in children.

**etutor-server implication:** E-ink's reflective display emits no backlight and thus no blue light — this is its strongest evidence-based advantage over LCD for children, specifically for evening sessions. Add a session-time warning: "It's getting late — we should wrap up so you sleep well." Do not enable frontlight by default for sessions after 19:00.

---

### 6.4 Eye Strain: E-Ink vs LCD

**No child-specific data found.** All controlled studies used adults.

| Finding | Citation | Key Result | Confidence |
|---|---|---|---|
| LCD causes significantly more visual fatigue than e-ink and paper | Benedetto et al. 2013, *PLoS ONE*, DOI:10.1371/journal.pone.0083676, N=12 adults | Blink rate: LCD vs e-ink p<0.05, η²p=0.36; e-ink not significantly different from paper | MED — adult only; small N; direction replicated |
| Image quality, not display technology, is the primary fatigue determinant | Siegenthaler et al. 2012, *Ophthalmic Physiol Opt*, DOI:10.1111/j.1475-1313.2012.00928.x | e-ink and LCD "very similar" on subjective and objective measures | LOW — adults; contradicts Benedetto |

**Gap:** No pediatric eye-strain data for e-ink exists in the peer-reviewed literature.

---

### 6.5 E-Ink Interaction Design Constraints

No peer-reviewed HCI paper specifically on e-ink UX for children exists. The following is derived from the physical constraints + general child-computer interaction (CCI) literature:

**From the ~300ms partial-refresh constraint:**
- Page-based/step-based navigation over scrolling — reduces refresh count, matches paper mental model
- Discrete state changes (glyph A → glyph B) over animated transitions
- Localise change to small partial-refresh zones; keep surrounding frame stable
- Input acknowledgment via non-visual channel (audio chime, haptic) since visual confirmation can't arrive in <100ms — critical for children who double/triple-tap when they see no response
- Periodic full-refresh at natural pauses (page turn, session complete) to clear ghosting invisibly

**Anti-patterns (confirmed from practitioner sources):**
- Drag-and-drop, hover states, spinners, scrolling lists, animated progress bars
- Rapid tap sequences without discrete feedback per tap
- Full-screen redraws on every state change
- Justified text (spacing gaps ghost between lines)

**CCI conflict:** General CCI principles require "immediate feedback" (<100ms). This is physically impossible on e-ink. Mitigation: non-visual channels (audio, haptic) are the only viable path — not trying to speed up the display.

---

### 6.6 Parental Acceptance and Screen Time

**No study found** comparing parental acceptance of e-ink vs LCD screen time. Confirmed research gap across PubMed, ERIC, Crossref, Semantic Scholar.

Tangentially: general parental positive attitude toward media is the strongest predictor of children's daytime media consumption (Lee, Kim & Kim 2022, *Children*, DOI:10.3390/children9010037, N=1,020). No screen-type breakdown.

---

### 6.5 Commercial Child E-Ink Devices — Converged UX

**No published design rationale found for any device.**
- Kindle Kids: 300 PPI, dyslexia font option, adjustable size — no HCI studies published
- Onyx Boox: no children's product line
- Likebook/Boyue: appears defunct (2024); no child-specific features documented

**etutor-server implication:** No converged industry standard to reference. Use Ma et al. 2023 (16pt) and WCAG 2.2 minimums as the baseline; test with children.

---

## 7. Voice-First Learning

### 7.1 Whisper Word Error Rate on Child Speech — The Critical Engineering Constraint (HIGH)

This is the most practically important finding for etutor-server's STT stack.

| Age range | Whisper large-v2/v3 WER (zero-shot) | Citation |
|---|---|---|
| Ages 6–7 (Grade 1) | **37.5%** | Singh et al. 2025, arXiv:2502.08587 |
| Ages 8–11 (conversational) | **12.8%** | Attia et al. 2023, arXiv:2309.07927 |
| Ages 8–11 (scripted) | **17.2%** | Attia et al. 2023 |
| Ages 8–11 (spontaneous) | **29.4%** | Attia et al. 2023 |
| Ages 4–7 | **39.1%** | Ying et al. 2025, arXiv:2508.16576 |
| Ages 8–10 | **13.5%** | Ying et al. 2025 |

**Fine-tuned Whisper medium (MyST + CSLU child data): 8.6% WER at ages 8–11** (Attia et al. 2023).

**Adult baseline for comparison:** ~2.8% WER.

**Whisper vs. Google vs. Azure on child speech (age ~5, spontaneous):**

| System | WER |
|---|---|
| Google Cloud Speech v2 | 49.0% |
| Microsoft Azure Speech | 30.3% |
| OpenAI Whisper large-v3 | **21.3%** |

Source: Janssens et al. 2024, arXiv:2404.17394. **Whisper wins**, even zero-shot.

**etutor-server implication:** Whisper is the right choice — best zero-shot WER on child speech of any commercial/open-source system. But the raw numbers demand design accommodations:
- Ages 6–8: ~37% WER means roughly 1 in 3 words misrecognised. Show the transcript on screen so the child can correct it. Do not feed raw Whisper output to the LLM without a correction step.
- Ages 9–12: ~13–18% WER is workable for conversational input. Still show the transcript.
- Fine-tune on child speech data (MyST corpus is publicly available) to halve the error rate if accuracy is critical.
- Consider push-to-talk rather than wake word — reduces false activations and background noise errors common in child environments.

---

### 7.2 TTS and Reading Comprehension (HIGH)

| Finding | Citation | Key Result | Confidence |
|---|---|---|---|
| TTS-supported digital reading improved comprehension vs. phonics control at age 8 | Gissel & Andersen 2021, *JCAL*, DOI:10.1111/jcal.12488, cluster-RCT n=1,013 | Positive, significant; only RCT with this age and TTS specifically | HIGH — only RCT; no effect size in abstract |
| TTS comprehension benefit for reading disabilities | Wood et al. 2018 meta-analysis, DOI:10.1177/0022219416688170 | **d = 0.35** (95% CI: 0.14–0.56) | HIGH — meta-analysis; reading difficulties population |
| TTS (with and without highlighting) outperforms silent reading on comprehension, ages 8–12 with reading difficulties | Keelor et al. 2023, DOI:10.1007/s11881-023-00281-9 | Positive, significant | MED — disabilities population only |

**Key nuance:** TTS improves comprehension for struggling readers. No evidence it improves *phonics or decoding* beyond standard instruction. The mechanism is reduced decoding load, not phonics training.

**etutor-server implication:** Read all tutor responses aloud (as designed in `pedagogy.md`). This is especially important for ages 6–8 and for any child with reading difficulties. Do not gate TTS on request — auto-play.

---

### 7.3 Voice Production and Retention — Full Mechanism Picture

**No study found** directly comparing voice input vs. typing/tapping on recall in children. Genuine literature gap.

**Critical constraint — mixed format required (HIGH):**
- Lipowski et al. 2024, DOI:10.1027/1618-3169/a000622: the production benefit requires a *mixed-format design* — some spoken, some silent. If every item is always spoken, distinctiveness disappears and so does the advantage. **Don't require voice for every turn.**

**Developmental table (confirmed):**

| Age | Direction | Design implication |
|---|---|---|
| 2–4 yrs | REVERSE — heard > produced | Have child listen; do not require spoken answers |
| 4.5–6 yrs | REVERSE for novel words | Hear new vocabulary before producing it |
| 7–10 yrs | TYPICAL — produced > heard | Require spoken answers for retention benefit |

Sources: Zamuner et al. 2018 (DOI:10.1111/desc.12636), López Assef et al. 2021 (DOI:10.1111/cdev.13618), Pritchard et al. 2020 (DOI:10.1111/cdev.13247)

**Speaking is cognitively cheaper than writing for children (HIGH):**
- Grabowski 2010, DOI:10.1080/00207590902914051: handwriting consumes working memory that spoken response does not. Even by 4th grade, writing had not reached cognitive parity with speaking. The freed WM resources go to the learning content.
- Winsler & Naglieri 2003, n=2,156 ages 5–17: overt self-talk was *positively* associated with task performance for ages 5–7. Children think through problems by speaking them.

**"Hear before produce" for new vocabulary (HIGH):**
- Hänel-Faulhaber et al. 2022, DOI:10.3389/fpsyg.2022.917700, ERP n=14 age ~8y8m: spoken word onset significantly facilitated subsequent written word recognition. RT: ~888ms (primed) vs ~1002ms (unrelated), p<0.001.
- Wegener et al. 2018/2020: oral vocabulary training on novel words → shorter reading times when those words appeared in print. Benefit persisted at second encounter; diminished with repeated visual exposure.

**TTS must not substitute for decoding practice (HIGH — safety warning):**
- Staels & Van den Broeck 2015, DOI:10.1177/0022219413487407: TTS had a **negative effect on orthographic learning** in disabled readers — passive listening reduced active phonological engagement. Children did not acquire the written word form.
- **etutor implication:** Always show the text alongside TTS. Do not use TTS to bypass reading — use it to scaffold it.

**The production effect (speaking during learning) — established for ages 7–10 (HIGH):**
- Pritchard, Heron-Delaney, Malone & MacLeod 2020, *Child Development*, DOI:10.1111/cdev.13247, n=81: Speaking words aloud during learning produced significantly better recognition memory than silent reading for **ages 7–10**. Held for both familiar words and novel nonwords.
- Icht & Mama 2015, *J Child Language*, DOI:10.1017/S0305000914000713: Production advantage in 5-year-olds using picture stimuli. "Look and say" beat "look" and "look and listen" — advantage is oral, not orthographic, so literacy level doesn't matter.
- **Developmental crossover:** López Assef et al. 2021, DOI:10.1111/cdev.13618, n=150: children under ~4–5 recall better from *hearing* than producing (reverse production effect). Ages 5+ show the standard advantage. For etutor target range (6+) the production effect is reliable.

**Self-reference effect — cheap engagement lever (HIGH, ages 4+):**
- Cunningham et al. 2014, *Child Development*, DOI:10.1111/cdev.12144, n=164, ages 4–6: Objects/words paired with self ("yours") outperformed other-framing on recognition across preference, source, and location tasks. Works from age 4+.
- **etutor implication:** Frame prompts as "what would *you* do" / tie vocabulary to the child's stated interests. Reliable encoding boost at zero implementation cost.

**Embodied learning / gesture (MED — hard to implement on e-ink but worth knowing):**
- de Nooijer et al. 2013, *Acta Psychologica*, DOI:10.1016/j.actpsy.2013.05.013, n=115: Gesture imitation at *retrieval* time (not just study) was the best condition for action-word retention after 1 week. Even a text prompt ("mime it") has some backing.

**Conversational agent voice for reading comprehension (HIGH):**
- Xu et al. 2022, *Child Development*, DOI:10.1111/cdev.13708, ages ~3–6: Voice CA during story-listening → higher story comprehension vs. no-dialogue control; engagement mediated the gain.
- Xu & Warschauer 2021, *Computers & Education*, DOI:10.1016/j.compedu.2020.104059: Story comprehension gains from voice CA were **statistically indistinguishable** from gains with a human adult partner. Children's talk with the CA was shorter and more content-focused.

**Self-explanation in math (MED — applies to voice-based reasoning prompts):**
- Rittle-Johnson 2006, *Child Development*, DOI:10.1111/j.1467-8624.2006.00852.x, grades 3–5: Verbal self-explanation promoted *transfer* of correct procedures across conditions.
- Bisra et al. 2018 meta-analysis, *Educational Psychology Review*, DOI:10.1007/s10648-018-9434-x: g ≈ 0.55 for self-explanation prompts across learning tasks.
- **Boundary condition** (Matthews & Rittle-Johnson 2009, grades 2–5, DOI:10.1016/j.jecp.2008.08.004): Self-explanation is redundant if strong conceptual instruction was already provided. Don't force it on mastered content.

**etutor-server implication:** The production effect is the mechanistic basis for the voice-first design. Require children to speak answers, not recognise them. Add self-reference framing to every question. For math, prompt the child to explain their reasoning before confirming correctness — this is where the self-explanation effect fires. Avoid forcing explanation on already-mastered content (Rittle-Johnson boundary condition).

---

### 7.4 Latency Tolerance

**No child-specific study found.** No peer-reviewed study has measured a disengagement latency threshold for children using voice interfaces. Genuine research gap.

Adult proxies (apply with caution):
- Natural conversation gap: ~200–230ms (Stivers et al. 2009, *PNAS* 106:10587, 10 languages)
- Thought flow preserved under 1,000ms; disengagement above 10,000ms (Miller 1968, AFIPS)

**Latency targets (inferred, not directly published for children):**

| Stage | Target |
|---|---|
| Acknowledgment signal (audio chime or "hmm...") | < 500ms after VAD end |
| Substantive response begins | < 2–3s |
| Total response complete | < 3–4s (ages 6–8); < 5s (ages 9–12) |
| Disengagement likely without feedback | > 5s (ages 6–8) |

Source: Abbas et al. 2021 HCOMP (DOI:10.1609/hcomp.v9i1.18935): conversational fillers ("let me think…") are the best mechanism for delays < 8s. Abbas et al. 2022 CSCW: > 8s generates negative evaluation of conversational AI in adults — children's threshold is lower.

**etutor-server implication:** Play an acknowledgment chime within 500ms. For processing delays > 2s, play a filler audio clip ("Hmm, let me think about that..."). Show a blinking dot on e-ink during processing. Pre-generate session-start responses.

### 7.5 Push-to-Talk vs Wake Word (MED — convergent indirect evidence)

No direct head-to-head study for children exists. Four convergent papers favour push-to-talk:

- Children ages 6–11 showed systematic confusion about when a wake-word device is "listening" — caused interaction anxiety (Andries & Robertson 2023, arXiv:2305.05597)
- Button-triggered activation supported cleaner turn structure; always-on wake word introduced false starts that disrupted dialogic flow (Xu et al. CHI 2021, DOI:10.1145/3411764.3445271)
- Classroom noise and multi-child environments make wake word detection unreliable; always-on microphones raised privacy concerns (Metatla et al. CHI 2019, DOI:10.1145/3290605.3300608)
- ~1 accidental trigger per 4 hours from adult TV content; children's ambient speech would produce substantially higher false activation (Schönherr et al. 2020, arXiv:2008.00508) — each false activation is a potential COPPA compliance event

**etutor-server implication:** Use push-to-talk. The e-ink device likely has a physical button — this is the right UX and the right legal choice.

### 7.6 TTS Stack — Critical Update

**Piper is no longer MIT licensed.** The `rhasspy/piper` repo was archived read-only on 6 October 2025. Active development is now at `OHF-Voice/piper1-gpl` under **GPL-3.0** — creates commercial licensing complications for etutor-server.

**Recommended replacement: Kokoro-82M** (Apache 2.0)
- StyleTTS2 + ISTFTNet architecture, 82M params
- 12.4M HuggingFace downloads/month; actively maintained
- No voice cloning; ONNX export for offline use on device
- Voices: `af_heart` or `af_sky` noted for warmer output
- GitHub: `hexgrad/kokoro`

**Speaking rate targets for child instruction (from developmental fluency norms):**
- Ages 6–8: **120–140 WPM** (0.85–0.90× default Kokoro speed)
- Ages 9–12: **140–160 WPM** (standard speed)

Source: Hasbrouck & Tindal oral reading fluency norms; Tallal et al. 1996 (Science, PMID:8539604): acoustically slowed speech significantly improved comprehension in language-impaired children.

**TTS prosody gap:** Neither Kokoro nor Piper expose pitch contour controls at inference time. Nencheva et al. 2021 (DOI:10.1111/desc.12997) showed it is dynamic pitch *contour movement* — not just elevated static F0 — that predicts toddler word learning. For the vocabulary introduction moments specifically, consider pre-recorded human narrator audio clips rather than TTS.

---

## Top Papers to Read First

| Priority | arXiv / DOI | Title | Why |
|---|---|---|---|
| 1 | 2305.14536 | MathDial (Macina et al., EMNLP 2023) | The core tutoring failure mode: 66% solution giveaway; correctness 0.43 |
| 2 | 2505.15607 | From Problem-Solving to Teaching (Dinucu-Jianu et al., EMNLP 2025) | RL fine-tuning recipe for Socratic LLM tutors; 7B model matches LearnLM |
| 3 | 2606.08568 | Regulating the AI Tutor (Abdelghani) | **Critical negative result:** unstructured LLM chat → post-test lower than pre-test |
| 4 | 2407.09136 | Stepwise Verification & Remediation (Daheim et al., EMNLP 2024) | Verify-then-generate architecture for hints; fewer hallucinations |
| 5 | 2502.18940 | MathTutorBench (Macina et al., EMNLP 2025) | Teaching quality degrades as conversations lengthen; benchmark for evaluation |
| 6 | 2302.06881 | simpleKT (Liu et al., ICLR 2023) | Recommended KT baseline; most honest evaluation in the field |
| 7 | 2309.14796 | FoLiBiKT (Im et al., CIKM 2023) | Forgetting bias — drop-in improvement for child session gaps |
| 8 | 2603.17373 | SafeTutors (Hazra et al., 2026) | Pedagogical safety: 17.7% → 77.8% failure in multi-turn dialogue |
| 9 | 2506.13510 | Safe-Child-LLM (Jiao et al., 2025) | 2–58% safety failure on child-facing prompts across frontier models |
| 10 | 2410.03781 | StratL (Puech et al., ACL 2024) | Operationalising pedagogical strategy as a prompt-level constraint |
| 11 | 10.1073/pnas.1418490112 | Chang et al. blue light RCT (PNAS 2015) | Strongest evidence for e-ink advantage: 55% melatonin suppression from backlit screen |
| 12 | 2506.16982 | Language Bottleneck Models (Berthon, 2025) | Most interpretable KT architecture; natural-language knowledge state |
| 13 | 10.1111/bjet.13558 | AI Dialogic Reading RCT (Xiao et al., BJET 2025) | Best child RCT (ages 5–8); AI wins on comprehension, humans win on affect |
| 14 | 2510.13862 | Ensemble LLMs for Affect (Zhang et al., ACII 2025) | Affect detection from text alone; confusion + curiosity co-occur in problem-solving |

---

## Key Researchers to Follow

| Researcher | Institution | Focus |
|---|---|---|
| Jakub Macina | ETH Zürich | Math tutoring dialogue, MathDial, MathTutorBench, StratL |
| Mrinmaya Sachan | ETH Zürich | LLM pedagogy, Socratic tutoring, RL alignment |
| Pierre-Yves Oudeyer | Inria | Curiosity, intrinsic motivation, child-AI interaction |
| Rania Abdelghani | Inria | Child question-asking, GPT-3 pedagogy |
| Ryan Baker | UPenn | Affect modeling, EDM, knowledge tracing |
| Andrew Lan | UMass Amherst | KT, DPO for education, RAG for math |
| Zitao Liu | TAL Education | pyKT, simpleKT, KT reproducibility |
| Gwo-Jen Hwang | NCTU Taiwan | Child LLM systems, game-based learning, metacognition |
| Cynthia Breazeal | MIT | Child-robot interaction, affect in tutoring |
| Neil Heffernan | WPI | ASSISTments, KT, formative feedback |

---

*Research provenance: Three of five parallel research agents returned complete findings (ITS processes trivialised by LLMs, modern tutoring papers 2023–2025, safety/Khanmigo). Two agents (voice-first, e-ink UX) stalled and are marked TODO. Findings should be cross-checked against primary sources before implementation decisions; all arXiv IDs and DOIs are cited for direct lookup.*
