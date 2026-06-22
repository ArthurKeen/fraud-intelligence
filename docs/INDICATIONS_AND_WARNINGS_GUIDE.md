# Indications & Warnings: Demo Guide

**Purpose**: Instead of starting a demo from a known suspect (Victor Tella) and
expanding outward, start from a **red flag** ("indication & warning") — a
suspicious *pattern* in the data — then expand the graph around it to reveal
**who is involved**, arriving at the suspect from the evidence.

All saved queries and canvas actions below are installed by
[scripts/install_graph_themes.py](../scripts/install_graph_themes.py) into the
ArangoDB Graph Visualizer (the `_queries`, `_canvasActions`, and viewpoint-link
collections) for the **DataGraph** and **KnowledgeGraph**.

> **Install / refresh:** `python scripts/install_graph_themes.py`
> (the script is idempotent — it upserts by stable key).

Every query and canvas action returns **graph elements (vertices / edges /
paths)** — the Queries panel only draws those; queries that return scalar or
aggregate objects render an empty canvas. This was verified end-to-end against a
throwaway ArangoDB seeded with the planted demo patterns.

---

## How to use in the demo

1. Open **Visualizer → DataGraph** (or KnowledgeGraph).
2. Open the **Queries** panel — the `[I&W] …` saved queries are your hunting
   starting points (no node selection required).
3. Run an `[I&W]` query → a suspicious pattern renders on the canvas.
4. **Right-click** a node → run a **canvas action** to expand around it (trace
   the money, reveal the owner, expose aliases, surface the ring).
5. Keep pivoting until the network resolves to Victor Tella / the suspect.

---

## Saved queries (the "indications")

Reliability tier is based on the planted demo dataset
([scripts/generate_data.py](../scripts/generate_data.py)): a 4-account transfer
**cycle**, a 50-mule **ring** sharing one device into one hub, an undervalued
property sale, and synthetic **aliases** for Victor Tella.

| Saved query | Indication it surfaces | Returns | On demo data |
|---|---|---|---|
| **[I&W] Circular Transaction Patterns** | Closed-loop / round-trip transfers (money returns to origin) | cycle **paths** | ✅ finds the planted 4-account cycle |
| **[I&W] Shared Device Mule Ring** | One device/IP used by many accounts | `accessedFrom` **edges** (device hub + spokes) | ✅ finds the 50-mule device |
| **[I&W] Rapid Inbound Bursts (Collection Velocity)** | Many transfers landing in one account within an hour | inbound **edges** | ✅ finds the mule hub |
| **[I&W] Round Amount Transfers (Suspiciously Uniform)** | Large exact-round-thousand amounts (non-organic) | transfer **edges** | ✅ surfaces the cycle's ₹crore transfers |
| **[I&W] Suspect Aliases (High-Risk Consolidations)** | One Golden Record with ≥2 Person aliases (benami / proxy identity) | resolved-alias **paths** | ✅ if Phase 2 entity resolution has run |
| **[I&W] Risk Propagation (Guilt by Association)** | Associates of the highest-risk people inherit risk | associate **paths** | ✅ if Phase 3 risk scoring + `relatedTo` exist |
| **[I&W] Gateway Accounts (Pass-Through Intermediaries)** | Accounts with both high in- and out-degree (layering) | transfer **paths** | ⚠️ data-dependent (needs accounts with in≥3 & out≥3) |
| **[I&W] Structuring Chains (Amount Decay Pattern)** | 3-hop chains where each transfer is ≥5% smaller (skim/fee) | chain **paths** | ⚠️ data-dependent (needs a decaying chain to exist) |

Plus the existing use-case queries: `UC1: Find Victor Tella`, `UC2: Top Fan-In /
Fan-Out Accounts`, `UC3: Undervalued Property Sales`, `UC4: Highest-Risk
Entities`, `Account Transfer Chain`.

> ⚠️ The two data-dependent queries are correct AQL and render when matching data
> exists, but the current planted dataset may not contain a qualifying gateway or
> a strictly-decaying chain. Run them once before the demo; if empty, lower their
> thresholds (`@minInDegree`/`@minOutDegree`, or `@decay` toward `0.99`) or skip
> them. The six ✅ queries are the safe demo spine.

### Tunable bind variables

| Query | Bind vars (defaults) |
|---|---|
| Circular Transaction Patterns | `minLen=2, maxLen=6, limit=10` |
| Shared Device Mule Ring | `minAccounts=5, limit=2` |
| Rapid Inbound Bursts | `minBurstSize=5, limit=3` |
| Round Amount Transfers | `minAmount=100000, limit=25` |
| Suspect Aliases | `limit=10` |
| Risk Propagation | `minRisk=50, seedLimit=3, depth=2, limit=25` |
| Gateway Accounts | `minInDegree=3, minOutDegree=3, limit=5` |
| Structuring Chains | `decay=0.95, limit=5` |

---

## Canvas actions (the "expand around it")

Right-click a selected node to run these. All return paths/edges so the canvas
grows in place.

### BankAccount
- **[BankAccount] Find cycles (AQL)** — directed transfer cycles back to the selected account.
- **[BankAccount] Trace Funding Sources (upstream)** — walk inbound transfers N hops: *who funded this account?*
- **[BankAccount] Trace Downstream Flow** — walk outbound transfers N hops: *where did the money go?*
- **[BankAccount] Show Owner & Linked Accounts** — account → holder → the holder's other accounts.
- **[BankAccount] Show Co-Accessed Accounts (shared device)** — account → device/IP → every other account that used it (mule-ring reveal).

### Person
- **[Person] Reveal Aliases (Golden Record)** — person → Golden Record → other identities/aliases.
- **[Person] Show Accounts & Money Flows** — person → their bank accounts → the transfers those accounts make.
- **[Person] Show Associate Network** — walk `relatedTo` to surface known associates (guilt-by-association).

Plus the generic `Find 2-hop neighbors (default)` and `[<Type>] Expand
Relationships` actions for every collection.

---

## Suggested demo walkthrough: "from indication to Victor Tella"

**Scene 1 — Circular pattern (headline).**
Run **[I&W] Circular Transaction Patterns** → a closed loop of accounts renders.
*"Money leaves this account and comes right back — a classic round-trip
laundering signature. But who controls these accounts?"*
Right-click a loop account → **Show Owner & Linked Accounts** → owner appears.

**Scene 2 — The mule ring.**
Run **[I&W] Shared Device Mule Ring** → a single device fans out to many accounts.
*"Dozens of 'different' accounts all logged in from the same device."*
Confirm velocity: run **[I&W] Rapid Inbound Bursts** → those accounts all dump
into one hub within an hour. Right-click the hub → **Trace Funding Sources** /
**Show Co-Accessed Accounts** to expand the ring.

**Scene 3 — Hidden identity.**
Run **[I&W] Suspect Aliases** → a Golden Record with multiple Person aliases.
Right-click → **[Person] Reveal Aliases** → the alias cluster, including Victor
Tella. Right-click Victor → **Show Accounts & Money Flows** to tie him back to
the cycle / ring accounts from Scenes 1–2.

**Scene 4 — Tainted associates.**
Run **[I&W] Risk Propagation** → Victor's associate network lights up.
*"Everyone one hop from our highest-risk actor inherits scrutiny."*

**Close.** *"We never started from the suspect. We started from patterns —
cycles, shared devices, velocity, aliases — and the evidence led us to Victor
Tella."*

---

## Notes & follow-ups

- **Performance:** *Circular Transaction Patterns* and *Structuring Chains* scan
  all BankAccounts with bounded-depth traversals (`uniqueEdges:"path"` + `LIMIT`).
  Fine on the demo dataset; if the graph grows large, seed them from high-degree
  hubs to bound cost.
- **WatchlistEntity has no edges** in this data model — watchlist hits are stored
  as `riskScore` / `riskReasons` on `Person`. Risk Propagation therefore seeds
  from the highest-risk *Person* and walks `relatedTo`, not from WatchlistEntity.
- **Orphan cleanup:** the installer upserts; it does not delete queries you remove
  from the script. If an earlier draft of this work was ever installed, the
  retired `[I&W] Compartmentalized Flows (Bimodal Distribution)` query may linger
  in `_queries` and can be deleted manually.
