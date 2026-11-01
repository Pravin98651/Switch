# I Let Four AI Agents Argue About My Invention (And Why Falsification Beat Brainstorming)

*By the IDEAForge Team — Built for the Flip the Switch Hackathon (Track 02: Best Personal or Creative Workflow)*

---

## The "Yes-Man" Trap in AI Brainstorming

If you have ever fed an early invention idea into a general-purpose AI chat, you have almost certainly experienced the **sycophant trap**:
> *"That's a revolutionary concept! Here are 10 venture capital firms that would love this!"*

When you're building physical hardware, software-defined instruments, or novel mechanical assemblies, uncritical enthusiasm is dangerous. Fabricating physical prototypes based on unchecked assumptions wastes weeks of machine-shop time, burns budgets on unnecessary components, and often leads to tests that cannot even prove whether the underlying physics actually work.

For the **Flip the Switch Hackathon**, we built **IDEAForge 2.0** around a contrary principle:
**Falsify Before You Fabricate.**

Instead of one AI cheerleader, IDEAForge deploys four specialist agents into a shared Switch collaboration room who actively stress-test your idea, challenge your assumptions, hunt for source evidence, and design the smallest decisive experiment to distinguish your hypothesis from competing baseline explanations.

---

## Meet the Crew

Inside our Switch room (`ideaforge-demo`), four agents operate under strict epistemic taxonomy:

```
                  ┌──────────────────────┐
                  │    Human Inventor    │
                  └──────────┬───────────┘
                             │ START IDEA / Scope Confirmation / Approval
                             ▼
                  ┌──────────────────────┐
                  │      forge-lead      │ (Orchestrator & Synthesizer)
                  └──────────┬───────────┘
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
┌──────────────────────┐          ┌──────────────────────┐
│    evidence-scout    │          │       red-team       │
│  (Source Locators)   │          │ (Adversarial Critic) │
└──────────────────────┘          └──────────────────────┘
            │                                 │
            └────────────────┬────────────────┘
                             │ Synthesized Trade-offs & Confirmed Scope
                             ▼
                  ┌──────────────────────┐
                  │ experiment-designer  │ (Minimum Decisive Experiment)
                  └──────────────────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │    Experiment Kit    │ (Card, CSV Template, analysis.py)
                  │   Epistemic Ledger   │ (Computed counts)
                  │ Tamper-Evident Dossier│ (SHA-256 pre-registered)
                  └──────────────────────┘
```

1. **`@forge-lead`**: Orchestrator, editor, and human gatekeeper. Manages the intake protocol, verifies confidentiality, enforces the scope gate, and executes deterministic validation.
2. **`@evidence-scout`**: The forensic reader. Ingests PDFs, DOCX, and markdown docs into a verifiable manifest. Every claim must have an exact locator (`line:42`, `page:3`, `paragraph:2`). If a claim lacks proof, it is banned from being labeled as fact.
3. **`@red-team`**: The designated falsifier. Reviews the idea independently to identify confounding variables, mounting resonance, baseline noise, and alternative explanations.
4. **`@experiment-designer`**: The test engineer. Translates surviving hypotheses into a **Minimum Decisive Experiment (MDE)**—the smallest test capable of distinguishing the proposed mechanism from competing baselines.

---

## 4 Features We Built to Make Switch Do More

### 1. One-Click Reproduction via `ideaforge.template.yaml`
Switch's agent template format allows distributing an entire multi-agent workspace in a single declarative file. In `ideaforge.template.yaml`, we packaged:
- All 4 agents with customized provider backends (`codex`, `claude`, etc.)
- Granular addressing policies (`anyone` for public scouts and critics; `owner-agents` for the approval-capable lead)
- Complete room instructions with strict provenance rules
- Automated kickoff welcome routine

A hackathon judge or new user can launch the entire studio in Switch Console with a single import click.

### 2. The Epistemic Ledger (Computed, Never Estimated)
Every claim in IDEAForge is tagged with one of six epistemic classifications:
`SOURCE_BACKED`, `USER_PROVIDED`, `INFERENCE`, `ASSUMPTION`, `HYPOTHESIS`, or `UNKNOWN`.

At the top of every dossier and Experiment Card, IDEAForge deterministically counts these claims:
```markdown
- **Epistemic Ledger:** 14 source-backed, 9 inferences, 11 assumptions, 6 unknowns, 0 user-provided, 1 hypothesis
```
No rounding, no vibes. If you haven't verified a claim against an ingested document, it stays an assumption.

### 3. Tamper-Evident Approval & Pre-Registration
In physical experiments, the easiest way to fool yourself is moving the goalposts after seeing noisy data. IDEAForge solves this cryptographically:
When the human runs `python -m ideaforge approve <CASE_ID> --statement "..."`, IDEAForge computes a SHA-256 hash of the entire approved dossier and the acceptance criteria.

If anyone alters a single number or threshold in the approved files, `python -m ideaforge validate` immediately fails:
```text
tamper check failed: acceptance criteria modified after approval (expected 4d7a12b..., got 9e88c01...)
```
This 20-second demo proves that approval is real, permanent, and auditable.

### 4. Room Isolation for Blind Review
A common failure mode in LLM collaboration is **anchoring bias**: if Agent B reads Agent A's critique before analyzing the raw sources, Agent B simply echoes Agent A.
Using Switch's multi-room architecture, `@red-team` can be placed in a private room with access only to the user's raw brief and reference sources. Once its critique is generated independently, `@forge-lead` brings the critique into the main room alongside `@evidence-scout`'s findings for side-by-side synthesis.

---

## Real-World Troubleshooting: What First-Time Switch Users Need to Know

Setting up multi-agent environments locally is rewarding, but there are sharp edges. Here are the 4 biggest gotchas we navigated:

### 1. The `@mention` Requirement is Absolute
Switch agents communicate inside real-time chat bridges (Mattermost, Slack). If you write:
*"Forge lead, please start the case"*, nothing will happen.
You must use the exact registered identifier:
`@forge-lead START IDEA: Conveyor belt vibration monitoring...`
Make sure your room instructions emphasize exact mention syntax to all participants.

### 2. Messaging Account Linking & Webhooks
When connecting Switch to Mattermost or Slack, verify that:
- Bot accounts have permission to post in private and public channels.
- The webhook URL matches the host bridge port (typically `http://localhost:8065` for local Mattermost).
- Agent display names in Switch match their Mattermost bot usernames.

### 3. First-Run Container Pulls Take Time
When launching the Switch stack via Docker Compose for the first time, images for the bridges, databases, and model harnesses need to download (~2–4 GB depending on your bridge).
*Tip:* Pre-pull images (`docker compose pull`) before running a live demo so you don't hit timeouts during presentation.

### 4. Addressing Policy Boundaries
Switch provides an `addressing` setting on agents:
- Use `anyone` for analysis agents (`evidence-scout`, `red-team`) so visiting mentors or team members can query them.
- Use `owner-agents` for workflow controllers (`forge-lead`, `experiment-designer`) so only the room owner can approve a case or trigger an experiment plan.

---

## The Verdict

By forcing agents to cite exact line numbers, challenge assumptions in parallel rooms, and lock decisions with cryptographic hashes, IDEAForge turns messy invention ideas into actionable, testable benchtop reality.

Clone the repo, import `ideaforge.template.yaml` into your Switch Console, and start falsifying before you fabricate.
