# Supplier ESG Intelligence Agent
## Product Requirements Document
**Version:** 1.0 — MVP
**Status:** Approved for Implementation
**Date:** July 2026

---

## Table of Contents

1. Product Overview
2. Problem Statement
3. Target Users
4. User Goals
5. User Stories
6. Success Metrics
7. Functional Requirements
8. Non-Functional Requirements
9. Input Specifications
10. Output Specifications
11. Scope 3 Readiness Classification Rules
12. Disclosure Completeness Assessment Rules
13. Gap Detection Rules
14. Confidence Indicator Rules
15. Follow-Up Question Generation Rules
16. MVP Scope
17. Explicit Out-of-Scope Items
18. Risks and Mitigations
19. Acceptance Criteria
20. Future Roadmap — V2 and V3

---

## 1. Product Overview

**Product Name:** Supplier ESG Intelligence Agent

**One-Line Description:** An AI-powered agent that converts a supplier's BRSR filing into a structured, cited Supplier ESG Intelligence Brief — covering disclosure completeness, Scope 3 readiness, critical gaps, and ready-to-use follow-up questions — in under 90 seconds.

**Core Value Proposition:** Procurement and sustainability analysts currently spend 45–90 minutes per supplier manually reading BRSR filings to determine whether a supplier meets minimum ESG disclosure standards and is ready for Scope 3 reporting. The Supplier ESG Intelligence Agent reduces that to under 90 seconds, with every finding traceable to a specific source section in the document.

**Primary Framework:** Business Responsibility and Sustainability Report (BRSR), as mandated by the Securities and Exchange Board of India (SEBI) for the top 1,000 listed companies by market capitalisation. BRSR is structured around the nine principles of the National Guidelines on Responsible Business Conduct (NGRBC).

**Target Market:** Indian enterprises and ESG professionals engaged in supplier onboarding, procurement risk assessment, and Scope 3 supply chain data collection.

---

## 2. Problem Statement

### The Gap in Procurement ESG Workflows

Organisations that procure from Indian-listed suppliers are increasingly required to assess those suppliers on ESG criteria — driven by their own BRSR value-chain disclosure obligations, CSRD supply chain requirements, and internal sustainability commitments. However, no current tool transforms a supplier's BRSR disclosure directly into a procurement-ready ESG assessment.

The current manual process is:
- Time-intensive: An analyst reads a 200–400 page annual report to extract the BRSR chapter and interpret its contents.
- Inconsistent: Different analysts apply different standards when evaluating the same supplier filing.
- Incomplete: The most important procurement signal — whether a supplier is ready for Scope 3 reporting — is buried in Principle 6 tables that require domain expertise to interpret.
- Untracked: Identified gaps and follow-up questions are captured in analyst notes, not in a structured, repeatable format.

### The Specific Scope 3 Problem

Scope 3 emissions represent approximately 70–90% of a large enterprise's total carbon footprint. Yet as of FY2024, only approximately 27% of India's top 1,000 listed companies voluntarily disclosed Scope 3 emissions in their BRSR filings. This means the most important ESG data point for a buyer's own carbon accounting is also the most likely to be missing from a supplier's filing — and currently, there is no fast, systematic way for a buyer to determine *how* missing it is and *what to ask for*.

---

## 3. Target Users

### Primary User: ESG Analyst / Sustainability Analyst

**Role Context:** Sits within the sustainability, ESG, or procurement function of a large enterprise. Responsible for supplier ESG assessments, BRSR value-chain disclosure, Scope 3 data collection, and compliance reporting.

**Technical Literacy:** Comfortable with digital tools. Familiar with BRSR and ESG frameworks. Not necessarily a data analyst or engineer.

**Current Pain:** Spends disproportionate time on document reading and manual data extraction before being able to perform meaningful analysis. Struggles to maintain consistent evaluation standards across a large supplier base.

**What They Need From This Tool:** A structured, reliable first-pass assessment of a supplier's BRSR disclosure that they can act on immediately — without reading the entire document first.

### Secondary User: Procurement Manager

**Role Context:** Makes supplier onboarding, monitoring, and renewal decisions. Receives ESG assessments from analysts as inputs to procurement decisions.

**Technical Literacy:** Business-oriented. Reads output briefs, does not perform extractions or analyses.

**What They Need From This Tool:** A clear, jargon-minimised output with a direct answer to: "Can we approve this supplier?" or "What do we need to ask before we can approve?"

### Future User (V2+): ESG Consultant

**Role Context:** Advises client companies on supplier ESG assessment, BRSR compliance, and Scope 3 data collection programs. Would use the tool as a research accelerator across multiple client supplier portfolios.

---

## 4. User Goals

### ESG Analyst Goals
- Assess a supplier's BRSR disclosure completeness across all 9 NGRBC principles without reading the full document.
- Determine immediately whether a supplier has disclosed Scope 3 emissions in a usable format.
- Identify the most critical disclosure gaps to prioritise in supplier engagement.
- Generate supplier follow-up questions without drafting them from scratch.
- Maintain a consistent evaluation standard across all assessed suppliers.
- Have every finding traceable to a source section in the filing, so they can verify any claim before acting on it.

### Procurement Manager Goals
- Receive a clear, structured supplier ESG brief rather than an unstructured analyst note.
- Understand whether a supplier has an ESG disclosure gap that affects procurement approval.
- Know exactly what information to request from a supplier before making a sourcing decision.

---

## 5. User Stories

**US-01 — Document Upload**
As an ESG Analyst, I want to upload a supplier's BRSR PDF so that the system can begin processing it without requiring me to pre-format or annotate the document.

**US-02 — Disclosure Completeness View**
As an ESG Analyst, I want to see a principle-by-principle completeness assessment of the uploaded BRSR so that I understand which areas of the supplier's ESG disclosure are complete, partial, or absent.

**US-03 — Scope 3 Readiness Verdict**
As an ESG Analyst, I want to receive a clear Scope 3 readiness verdict — with the specific evidence that supports or contradicts readiness — so that I can determine whether this supplier can contribute to our Scope 3 inventory.

**US-04 — Gap Identification**
As an ESG Analyst, I want to see the top five most procurement-relevant disclosure gaps, each citing the specific BRSR indicator and source section, so that I know exactly what is missing and where to look in the source document.

**US-05 — Follow-Up Questions**
As an ESG Analyst, I want the system to generate ready-to-use follow-up questions for the supplier based on detected gaps, so that I can initiate supplier engagement without drafting questions from scratch.

**US-06 — Confidence Transparency**
As an ESG Analyst, I want to know the system's confidence in its extraction — and to receive a clear directive on whether the brief requires human review before being acted upon — so that I do not make procurement decisions based on low-quality extractions.

**US-07 — Source Citations**
As an ESG Analyst, I want every factual claim in the brief to reference the specific BRSR section or page from which it was extracted, so that I can verify any finding by going directly to the source document.

**US-08 — Procurement Manager Consumption**
As a Procurement Manager, I want to receive the ESG Intelligence Brief in a structured, readable format so that I can understand the supplier's ESG status and any required follow-up actions without needing domain expertise in BRSR.

---

## 6. Success Metrics

### Primary MVP Success Criterion
The MVP is successful when a user uploads a BRSR PDF from any NSE/BSE top-1,000 listed company and receives a complete Supplier ESG Intelligence Brief within 90 seconds, where every factual claim in the brief cites a specific section or page from the uploaded document.

### Quantitative Metrics

| Metric | Target |
|---|---|
| Brief generation time | ≤ 90 seconds from upload completion |
| Citation coverage | 100% of factual claims carry a source citation |
| Scope 3 verdict accuracy | Classification matches domain expert review in ≥ 85% of test cases |
| Completeness assessment accuracy | Per-principle state matches expert review in ≥ 85% of test cases |
| Gap relevance | ≥ 4 of 5 generated gaps rated as procurement-relevant by a domain expert |
| Follow-up question usability | ≥ 3 of 5 generated questions rated as ready-to-use without editing |
| Confidence calibration | Low/High confidence assignments validated against actual extraction quality in ≥ 90% of cases |

### Qualitative Success Signals
- An ESG analyst who has manually reviewed the same BRSR filing confirms the brief contains no material factual errors.
- A procurement manager can read the brief and correctly identify the supplier's Scope 3 status and the highest-priority follow-up question without analyst support.

---

## 7. Functional Requirements

### FR-01 — Document Ingestion
The system must accept a single PDF file as input and extract machine-readable text from it. The system must attempt to locate the BRSR section within the document, including when the BRSR is embedded as a chapter within a larger annual report.

### FR-02 — Quality Assessment
Before any ESG analysis begins, the system must assess document quality and produce a quality signal covering: (a) whether the document is machine-readable or image/scanned, (b) what proportion of the BRSR section is parseable, (c) whether critical sections — specifically Principle 6 (Environment) — are locatable and extractable. If quality falls below the Low Confidence threshold defined in Section 14, the system must halt the analysis pipeline and return a Human Review flag with a description of the quality failure before producing any output.

### FR-03 — Structured Extraction
The system must extract data from the uploaded BRSR against a fixed indicator checklist covering all 9 NGRBC principles and their associated essential indicators. For each indicator, the system must assign one of three extraction states: Disclosed, Partially Disclosed, or Not Found in Uploaded BRSR Filing. The system must not infer the presence or content of a disclosure from indirect signals — every state assignment must be grounded in locatable text in the source document.

### FR-04 — Disclosure Completeness Assessment
The system must produce a principle-level completeness view for all 9 BRSR principles as defined in Section 12. Each principle must carry an overall state: Complete, Partial, or Not Found. The assessment must not produce a single aggregate score — it must present a per-principle breakdown.

### FR-05 — Scope 3 Readiness Assessment
The system must classify the supplier's Scope 3 readiness according to the four-level classification system plus the Materiality Claim special state, as defined in full in Section 11. The verdict must be accompanied by the specific evidence that drove the classification — the extracted text or the absence thereof — and a source citation where evidence was found.

### FR-06 — Gap Detection
The system must identify the top five most procurement-relevant disclosure gaps from the extracted data, following the priority framework defined in Section 13. Each gap must include: a gap name, the BRSR principle and indicator reference, a severity rating, a plain-English description, and a source citation or explicit "not found" language.

### FR-07 — Confidence Assessment
The system must produce a Confidence Indicator at the brief level, classified as High, Medium, or Low, following the rules defined in Section 14. The Confidence Indicator must drive a behavioural cue — a directive to the user on how to use the brief — not merely a number or label.

### FR-08 — Follow-Up Question Generation
The system must generate between three and five supplier-facing follow-up questions based on the detected gaps, following the rules defined in Section 15. Questions must be phrased for direct use in a supplier communication without requiring editing.

### FR-09 — Source Citation
Every factual claim in the output brief must carry a citation in the format: [BRSR Principle X — Indicator Y — Page/Section Z] or, where the finding is an absence, the citation must read: [Not found in uploaded BRSR filing — Principle X — Indicator Y checked].

### FR-10 — Output Delivery
The system must produce a structured Supplier ESG Intelligence Brief as defined in Section 10, containing all required sections in the specified order. The brief must be human-readable and require no additional processing before use.

### FR-11 — Disclaimer
Every brief must include a standard disclaimer as the first visible element: *"This assessment is based solely on the uploaded BRSR filing. Disclosures in separate sustainability reports, CDP submissions, GRI reports, or supplementary documents were not reviewed and are not reflected in this brief."*

---

## 8. Non-Functional Requirements

### NFR-01 — Processing Time
End-to-end processing from upload completion to brief delivery must complete within 90 seconds for a standard BRSR filing (defined as a machine-readable PDF of up to 400 pages).

### NFR-02 — Accuracy Floor
The system must not produce fabricated or hallucinated factual claims. Every claim of the form "Supplier has disclosed X" or "Supplier has not disclosed X" must be verifiable against the source document. Where extraction uncertainty exists, the system must surface the uncertainty as a confidence signal, not suppress it.

### NFR-03 — Graceful Degradation
When extraction fails for a specific section or indicator, the system must return "Not Found in Uploaded BRSR Filing" for that indicator, not an inferred state. The system must never silently fall back to a model's pretrained knowledge about a company to fill a gap in the extraction.

### NFR-04 — Consistency
Two identical uploads of the same document must produce identical output briefs. The classification rules in Sections 11–15 must be applied deterministically, not probabilistically.

### NFR-05 — Traceability
The output data model must preserve the link between every output claim and the source text segment from which it was extracted, such that citations can be rendered in the brief and verified by a user.

### NFR-06 — Failure Transparency
When the system cannot produce a reliable brief — due to document quality failures, unreadable sections, or low extraction confidence — it must tell the user specifically what failed and what to do, rather than producing a low-quality brief without warning.

---

## 9. Input Specifications

### Accepted Input
- **File type:** PDF (.pdf)
- **Content:** A Business Responsibility and Sustainability Report (BRSR) filed under SEBI's BRSR mandate, either as a standalone document or as an embedded chapter within an annual report
- **Language:** English (primary); Hindi or regional language content within an otherwise English document is acceptable — such content will be flagged as non-extractable if it contains BRSR indicator data
- **Document size:** Up to 400 pages
- **Readability:** Machine-readable text required; scanned/image-only documents will be flagged with a Low Confidence signal and a Human Review directive before brief generation proceeds

### Validation Checks on Ingestion
The system must perform the following checks before proceeding to extraction:

| Check | Condition | Action on Failure |
|---|---|---|
| File type | Must be PDF | Reject with message: "Only PDF files are accepted." |
| File size | Must not exceed 50MB | Reject with message: "File exceeds 50MB limit." |
| Machine readability | Text layer must be extractable | Flag Low Confidence; surface Human Review directive |
| BRSR section detection | BRSR chapter must be locatable | Flag Medium or Low Confidence depending on partial vs total failure |
| Language | Primary language must be English | Proceed; flag any non-English indicator data as non-extractable |

### What the System Does Not Accept
- Scanned images submitted as PDFs without a text layer (will trigger Low Confidence and Human Review, not outright rejection)
- Non-BRSR documents (e.g., financial statements without ESG content) — the system will attempt extraction and surface a Low Confidence result; it will not pre-validate document type before ingestion
- Multiple files in a single submission — one document per brief

---

## 10. Output Specifications

The Supplier ESG Intelligence Brief is the sole output of the system. It must contain the following sections in the following order.

### Section A — Brief Header
| Field | Description |
|---|---|
| Document Disclaimer | Standard disclaimer text (verbatim as specified in FR-11) |
| Supplier Name | Extracted from document cover page or heading |
| Filing Year | Extracted BRSR reporting year |
| Document Source | File name of the uploaded document |
| Brief Generated | Timestamp of brief generation |
| Confidence Indicator | High / Medium / Low, with associated behavioural directive |

### Section B — Disclosure Completeness Assessment
A table presenting all 9 BRSR principles with their completeness state.

| Column | Content |
|---|---|
| Principle Number | 1 through 9 |
| Principle Name | As defined in NGRBC |
| Completeness State | Complete / Partial / Not Found |
| Source Citation | BRSR section reference |
| Note | Optional: specific essential indicators that drove a Partial rating |

### Section C — Scope 3 Readiness Verdict
| Field | Content |
|---|---|
| Readiness Level | Not Found / Claim Only / Partial / Scope 3 Ready / Materiality Claim |
| Level Label | Short descriptor as defined in Section 11 |
| Evidence | Extracted text or absence statement that drove the classification |
| Source Citation | Page/section reference, or "Not found in uploaded BRSR filing" |
| Maturity Signals | Separately listed: assurance status, category boundary, SBTi, significant partners, year-on-year trend |

### Section D — Top 5 Disclosure Gaps
An ordered list of the five highest-priority disclosure gaps.

| Field | Content |
|---|---|
| Gap Number | 1 (highest priority) through 5 |
| Gap Name | Short descriptive label |
| BRSR Reference | Principle and indicator number |
| Severity | Critical / Notable / Minor |
| Description | Plain-English explanation of what is missing and why it matters |
| Citation | "Not found in uploaded BRSR filing — [Principle X — Indicator Y checked]" |

### Section E — Suggested Follow-Up Questions
An ordered list of three to five questions.

| Field | Content |
|---|---|
| Question Number | 1 (highest priority) through 5 |
| Question Text | Supplier-facing, ready-to-use phrasing |
| Linked Gap | Reference to the Gap Number from Section D that this question addresses |

---

## 11. Scope 3 Readiness Classification Rules

### Overview

The Scope 3 Readiness verdict is the most procurement-critical output of the brief. Every classification decision must follow the rules below deterministically and produce a citable evidence statement. No classification may be made on inferred, assumed, or general knowledge — only on text present in the uploaded document.

### Classification System

The system uses four named levels plus one special state.

---

#### Level 0 — Not Found in Uploaded BRSR Filing

**Definition:** No mention of Scope 3 emissions, Scope 3 categories, or value-chain emissions appears in the uploaded document, OR Scope 3 is mentioned only in a definitional or framework context without any company-specific disclosure.

**Trigger conditions (any one of the following):**
- The term "Scope 3" does not appear in the document
- "Scope 3" appears only in a definition of what Scope 3 means, with no company-specific data attached
- The Principle 6 environment tables are present but the Scope 3 row is blank, contains a dash, or contains "N/A" with no accompanying explanation

**Output language:** *"Scope 3 emissions data was not found in the uploaded BRSR filing. This does not confirm that no disclosure exists — separate sustainability reports or CDP submissions were not reviewed."*

**Evidence statement:** Must cite the Principle 6 section reference and state that the indicator row was checked and found blank or absent.

---

#### Materiality Claim — Special State

**Definition:** The company has made an explicit, company-specific written statement that Scope 3 emissions are not applicable, not material, not relevant, or not assessed for its operations. This is a disclosure, not an absence.

**Trigger conditions (all of the following):**
- An explicit company statement uses one of these phrases or a functional equivalent: "not applicable," "not material," "not assessed," "not relevant," "not required for our operations," in the context of Scope 3
- The statement is company-specific (not a generic definition of materiality)
- No quantified Scope 3 figure is provided

**Output language:** *"Supplier has formally stated that Scope 3 emissions are not material to its operations. No quantified Scope 3 data is provided in this filing. The basis for this materiality determination has not been independently verified from the uploaded document. Suggested follow-up: request the supplier's materiality assessment documentation."*

**Important distinction from Level 0:** Level 0 is silence. Materiality Claim is an explicit position. The output language and follow-up question must reflect this distinction.

**Evidence statement:** Must quote or closely paraphrase the specific sentence in the filing that contains the materiality claim, with page/section citation.

---

#### Level 1 — Claim Only

**Definition:** The company acknowledges Scope 3 in a qualitative or non-quantified form. No usable absolute emissions figure is provided.

**Trigger conditions (any one of the following qualifies as Claim Only):**

1. A qualitative acknowledgment without a number: *"We are in the process of assessing our Scope 3 emissions."*
2. A statement that Scope 3 is under evaluation or planned: *"Scope 3 will be measured in the next reporting cycle."*
3. A description of Scope 3 categories that are relevant without quantification: *"Our primary Scope 3 categories are purchased goods and services and employee commuting."*
4. A Scope 3 reduction target or commitment without a baseline figure: *"We aim to reduce our Scope 3 emissions by 30% by 2030."*
5. A reference to Scope 3 only in the context of a certification or standard without associated data: *"Our GHG inventory is prepared in accordance with the GHG Protocol, including Scope 3."*
6. **Intensity-only disclosure** (critical rule, Decision 2): A ratio expressed as emissions per unit of revenue, production, or activity (e.g., tCO₂e per ₹ crore of revenue, tCO₂e per tonne of product) without an accompanying absolute figure. Intensity ratios are not usable for supply chain Scope 3 accounting and must be classified as Claim Only, not Partial. The intensity figure must be extracted and displayed as context, but it does not elevate the classification.

**Output language:** *"Supplier acknowledges Scope 3 emissions but does not provide a quantified absolute figure usable for supply chain carbon accounting. Classification: Claim Only."*

**Evidence statement:** Must extract the specific sentence or phrase that constitutes the claim, with section/page citation.

---

#### Level 2 — Partial

**Definition:** The company provides either a quantified absolute Scope 3 figure OR a named methodology, but not both.

**Trigger conditions:**

Condition A — Number without methodology:
- An absolute Scope 3 figure in tCO₂e (or mtCO₂e, ktCO₂e) is present in the document
- AND no accounting methodology is named (GHG Protocol, ISO 14064-1, or equivalent)
- Classification: Partial

Condition B — Methodology without number:
- A named accounting methodology is stated for Scope 3 (e.g., GHG Protocol Corporate Value Chain Standard, ISO 14064-1, Scope 3 Evaluator)
- AND no absolute Scope 3 figure in tCO₂e appears in the document
- Classification: Partial

**Boundary rules:**
- A figure in a unit other than absolute mass of CO₂e (i.e., ratios, indices, percentages) does not qualify as an "absolute figure." See Intensity-only rule in Level 1.
- A statement that the company "follows the GHG Protocol" without specifically applying it to Scope 3 does not qualify as a named Scope 3 methodology.
- Prior-year Scope 3 figures with no current-year figure classify as Partial.

**Output language:** *"Supplier has partially disclosed Scope 3 emissions — [either: a quantified figure is provided without a named methodology / a methodology is named but no absolute figure is provided]. Classification: Partial."*

**Evidence statement:** Must extract the specific figure or methodology reference present, note what is absent, and provide page/section citation.

---

#### Level 3 — Scope 3 Ready

**Definition:** The company provides both a quantified absolute Scope 3 figure AND a named accounting methodology in the uploaded filing.

**Trigger conditions (ALL must be true):**
1. An absolute Scope 3 figure is present in tCO₂e (or mtCO₂e, ktCO₂e)
2. A named accounting methodology is explicitly associated with the Scope 3 figure (GHG Protocol Corporate Value Chain Standard, ISO 14064-1, or a formally recognised equivalent)

**Output language:** *"Supplier has disclosed quantified Scope 3 emissions with a named accounting methodology. Classification: Scope 3 Ready."*

**Evidence statement:** Must extract both the figure and the methodology name, confirm both are present in the document, and provide section/page citation for each.

---

### Maturity Signals — Displayed Separately, Do Not Affect Level

The following signals are extracted and displayed in Section C of the brief as supplementary context. They do not change the Scope 3 readiness level assignment.

| Signal | What to Extract | Display Label |
|---|---|---|
| Third-party assurance | Whether a named assurance provider has assured the Scope 3 figure | Assurance: [Provider name] / Not assured |
| Category boundary | Whether the filing states which of the 15 GHG Protocol Scope 3 categories are included | Category boundary: Stated / Not stated |
| SBTi commitment | Whether the company has an active or committed SBTi target covering Scope 3 | SBTi: Committed / Validated / Not found |
| Significant value-chain partners | Whether the filing identifies significant suppliers/customers for Scope 3 purposes | Significant partners: Identified / Not identified |
| Year-on-year trend | Whether prior-year Scope 3 figures are provided alongside current-year data | Trend data: Available / Not available |

**SBTi Rule (Decision 4):** The presence of an SBTi commitment does not upgrade the Scope 3 readiness level. If the BRSR states an SBTi commitment or validation, extract and display it as a Maturity Signal. Do not infer from the SBTi commitment that Scope 3 data infrastructure exists.

---

### Scope 3 Classification Decision Tree

```
Does the filing contain any mention of Scope 3?
│
├─ NO → Level 0: Not Found in Uploaded BRSR Filing
│
└─ YES → Does the company explicitly state Scope 3 is not applicable/material?
         │
         ├─ YES → Materiality Claim (Special State)
         │
         └─ NO → Is a quantified ABSOLUTE Scope 3 figure in tCO₂e present?
                  │
                  ├─ NO (only intensity ratio, qualitative claim, or target)
                  │   └─ Level 1: Claim Only
                  │
                  └─ YES (absolute figure in tCO₂e present)
                      │
                      └─ Is a named accounting methodology also present?
                          │
                          ├─ NO → Level 2: Partial
                          │
                          └─ YES → Level 3: Scope 3 Ready
```

---

## 12. Disclosure Completeness Assessment Rules

### Overview

The Disclosure Completeness Assessment evaluates how fully the supplier has addressed each of the nine BRSR principles across its essential indicators. It does not produce a single aggregate score. It produces a per-principle state and, where a Partial state is assigned, it names which specific indicators drove that rating.

### The Nine BRSR Principles

| # | Principle Name |
|---|---|
| 1 | Ethics, Transparency, and Accountability |
| 2 | Sustainable and Safe Products and Services |
| 3 | Employee Well-being |
| 4 | Stakeholder Responsiveness |
| 5 | Human Rights |
| 6 | Environment |
| 7 | Public Policy Advocacy |
| 8 | Inclusive Growth and Equitable Development |
| 9 | Consumer Responsibility |

### Per-Indicator State Definitions

For each essential indicator within a principle, the system assigns one of three states:

**Disclosed:** The indicator is addressed with specific, company-relevant information. A quantitative indicator contains a figure. A qualitative indicator contains a company-specific response (not a generic statement or a definition of the concept).

**Partially Disclosed:** The indicator is addressed but the response is vague, incomplete, or unquantified where quantification is expected. Examples include: an environmental target stated without a baseline, a policy referenced without describing its scope, a number provided without a unit, or a prior-year figure provided without a current-year update.

**Not Found in Uploaded BRSR Filing:** The indicator is not addressed in the uploaded document, or the row/field is blank, contains only a dash, or contains "N/A" without an explanatory statement.

### Principle-Level State Rules

| Principle State | Condition |
|---|---|
| Complete | All essential indicators for this principle are Disclosed |
| Partial | At least one essential indicator is Disclosed AND at least one is Partially Disclosed or Not Found |
| Not Found | All essential indicators checked for this principle are Not Found in Uploaded BRSR Filing |

### Priority Principles for MVP

While all nine principles are assessed, Principle 6 (Environment) receives the deepest extraction attention in the MVP, as it contains the GHG emissions data most critical to procurement decisions. The system must locate and extract: Scope 1 emissions, Scope 2 emissions, Scope 3 status, energy intensity, renewable energy share, water intensity, and waste generation — and must cite each finding individually.

### Citation Rule for Completeness Assessment

Every per-principle state assignment must reference the specific BRSR section heading and, where possible, the page number from which the assessment was drawn. A Not Found assignment must state: "Not found in uploaded BRSR filing — [Principle X essential indicators checked]."

---

## 13. Gap Detection Rules

### Overview

The Gap Detection module identifies the five highest-priority procurement-relevant disclosure gaps from the extracted data. Gaps are drawn from a priority-ranked indicator list. The system selects the top five gaps by priority, resolves ties by severity, and presents them in ranked order in Section D of the brief.

### Gap Priority Framework

#### Critical Gaps — Always surfaced first if present

| Gap ID | Gap Name | BRSR Reference | Trigger Condition |
|---|---|---|---|
| G-01 | Scope 3 not disclosed | Principle 6, Environment | Scope 3 Readiness Level 0 or Level 1 (Claim Only) |
| G-02 | No GHG accounting methodology named | Principle 6, Environment | Scope 3 is Level 2 or below; no methodology named for Scope 1/2 either |
| G-03 | Principle 6 environmental data absent or severely incomplete | Principle 6, Essential Indicators | Principle 6 completeness state is Not Found |
| G-04 | BRSR Core indicators not disclosed | BRSR Core (SEBI mandate) | No BRSR Core section found in the document |
| G-05 | No climate targets disclosed | Principle 6, Leadership Indicators | No emissions reduction target of any kind found |

#### Notable Gaps — Surfaced if no more than three Critical gaps are present

| Gap ID | Gap Name | BRSR Reference | Trigger Condition |
|---|---|---|---|
| G-06 | Value-chain comply-or-explain not completed | Principle 2 / Principle 8 | Comply-or-explain disclosures for value chain answered with explain or absent |
| G-07 | Human rights policy not disclosed | Principle 5, Essential Indicators | No human rights policy found |
| G-08 | Third-party assurance absent on BRSR Core | BRSR Core assurance | BRSR Core present but assurance statement not found |
| G-09 | No significant supplier identification | Principle 6 / Principle 8 | No identification of significant value-chain partners for ESG purposes |
| G-10 | Scope 1 or Scope 2 intensity metrics absent | Principle 6, Essential Indicators | Scope 1 or 2 absolute figures present but intensity metrics not found |

#### Minor Gaps — Surfaced only when fewer than five gaps from above categories are present

| Gap ID | Gap Name | BRSR Reference | Trigger Condition |
|---|---|---|---|
| G-11 | Leadership indicators not addressed | Across all principles | No leadership indicators answered across all nine principles |
| G-12 | Year-on-year comparison data absent | Principle 6 | Current-year emissions data present but no prior-year comparison |
| G-13 | Anti-corruption policy not disclosed | Principle 1, Essential Indicators | No anti-corruption or anti-bribery policy found |
| G-14 | Health and safety performance data absent | Principle 3, Essential Indicators | No LTIFR or equivalent safety metric found |

### Gap Selection Rules

1. Select all Critical gaps that are triggered. If five or more Critical gaps are triggered, output the five highest-ranked Critical gaps (G-01 through G-04 take precedence in that order).
2. If fewer than five Critical gaps are triggered, fill remaining slots with Notable gaps in the order listed.
3. If fewer than five Critical and Notable gaps combined are triggered, fill remaining slots with Minor gaps.
4. The output must always contain exactly five gaps unless fewer than five total gaps are triggered across all categories, in which case the system outputs all triggered gaps and states: "No additional gaps were detected in the uploaded filing."

### Gap Output Format

Each gap in Section D must contain:
- **Gap number:** 1 (highest priority) through 5
- **Gap name:** Short label from the table above
- **BRSR reference:** Principle and indicator identifier
- **Severity:** Critical / Notable / Minor
- **Description:** One to three plain-English sentences explaining what is missing and why it matters for a procurement decision
- **Citation:** "Not found in uploaded BRSR filing — [Principle X — Indicator Y checked]" or, where the gap is a quality issue rather than an absence, the specific section reference

---

## 14. Confidence Indicator Rules

### Overview

The Confidence Indicator reflects the system's confidence in the extraction quality of the uploaded document. It is not an evaluation of the supplier's ESG performance. It drives a behavioural directive to the user about how to use the brief.

### Confidence Levels and Trigger Conditions

#### High Confidence

**All of the following must be true:**
- Document is machine-readable (text layer extractable without OCR)
- BRSR section was located within the document without ambiguity
- 80% or more of checked essential indicator fields were locatable in the document
- Principle 6 (Environment) section was fully extracted, including GHG tables
- No significant table parsing failures were detected

**Behavioural directive:** *"Extraction quality is high. This brief can be used as the basis for procurement decision-making. Verify any specific claim by cross-referencing the cited section in the source document before acting on it."*

#### Medium Confidence

**Applies when High Confidence conditions are not all met, and any of the following is true:**
- 50–79% of checked essential indicator fields were locatable
- One or more tables had partial parsing failures (e.g., merged cells, image-embedded tables)
- The BRSR section required heuristic location within a larger document
- Principle 6 was found but one or more GHG sub-tables had formatting issues
- The document contains mixed machine-readable and scanned sections, with the BRSR section falling in a machine-readable portion

**Behavioural directive:** *"Some sections had extraction uncertainty. Fields marked [⚠] in this brief should be manually verified against the source document before acting on them. The Scope 3 readiness verdict and Completeness Assessment are reliable for principles where extraction was clean."*

**Implementation note:** Fields where extraction uncertainty was detected must be individually marked with a [⚠] indicator in the output.

#### Low Confidence

**Applies when any of the following is true:**
- Document is fully or predominantly scanned / image-based
- Fewer than 50% of checked essential indicator fields were locatable
- The BRSR section could not be identified within the document
- Principle 6 (Environment) could not be extracted

**Behavioural directive:** *"Significant extraction limitations were detected in the uploaded document. This brief must not be used for procurement decisions without full human review of the source BRSR filing. The findings below are indicative only."*

**Pipeline rule:** When Low Confidence is triggered during the initial Quality Check (FR-02), the system must surface the Confidence Indicator and directive before proceeding. The brief is still generated, but the Low Confidence banner and directive must appear as the first element of the output — before the completeness assessment, Scope 3 verdict, or any other section.

### What the Confidence Indicator Does Not Reflect

- The supplier's ESG performance (a poor ESG discloser can have a High Confidence brief)
- The materiality or importance of missing disclosures (Gap Detection handles this)
- Whether the BRSR filing is accurate or truthful (this product does not perform assurance)

---

## 15. Follow-Up Question Generation Rules

### Overview

The system generates between three and five supplier-facing follow-up questions based on the gaps detected in Section D. Questions must be ready to paste into a supplier communication without requiring editing by the analyst.

### Question Generation Rules

**Rule 1 — Source from gaps only.** Questions must be derived exclusively from the gaps identified in Section D. The system must not generate questions about topics not covered by a detected gap.

**Rule 2 — Priority order.** Generate questions in this sequence:
1. Questions addressing Critical gaps (G-01 through G-05) first
2. Questions addressing Notable gaps second
3. Questions addressing Minor gaps only if fewer than three questions have been generated

**Rule 3 — One question per gap.** Each generated question must map to exactly one gap in Section D. Multiple questions about the same gap are not permitted.

**Rule 4 — Supplier-facing language.** Questions must be written as if addressed directly to the supplier. They must name the specific missing item. They must not use internal classification terminology (do not use "Level 1," "Critical gap," or "G-01" in the question text).

**Rule 5 — Minimum three, maximum five.** If fewer than three gaps are detected, generate one question per gap (minimum output is one question). If more than five gaps are detected, generate questions for the five highest-priority gaps only.

**Rule 6 — Cite the reporting year.** Where the question concerns a quantitative disclosure, it must reference the relevant reporting year extracted from the document.

### Question Phrasing Templates

The following templates must guide question phrasing. They are starting patterns, not fixed scripts — the system must produce natural, supplier-appropriate language.

| Gap Type | Template Pattern |
|---|---|
| Scope 3 not disclosed | "Your [FY] BRSR does not include quantified Scope 3 emissions. Can you share your absolute Scope 3 figure in tCO₂e for [FY], along with the methodology used to calculate it?" |
| Methodology absent | "Your BRSR does not name the accounting methodology used for your GHG inventory. Can you confirm which standard governs your emissions calculations (e.g., GHG Protocol, ISO 14064)?" |
| Value-chain section incomplete | "The value-chain section of your BRSR indicates [specific gap]. Can you provide details on [specific missing item] or direct us to where this is disclosed?" |
| Policy not found | "We were unable to locate your [human rights / anti-corruption / responsible sourcing] policy in the uploaded filing. Can you share this policy or confirm where it is disclosed?" |
| Target not found | "Your BRSR does not include an emissions reduction target. Does your organisation have a climate target, and if so, can you share the target, baseline year, and scope of coverage?" |
| Assurance absent | "Your BRSR Core indicators do not appear to carry third-party assurance. Can you confirm whether limited or reasonable assurance has been obtained, and if so, share the assurance statement?" |

### Question Output Format

Each question in Section E must contain:
- **Question number:** 1 (highest priority) through maximum 5
- **Question text:** Ready-to-use supplier-facing sentence(s)
- **Linked gap:** Reference to the Gap Number from Section D (e.g., "Addresses Gap 1 — Scope 3 not disclosed")

---

## 16. MVP Scope

### In Scope — MVP

| Feature | Description |
|---|---|
| Single document ingestion | Upload one BRSR PDF per assessment session |
| Document quality check | Assess machine readability and extraction confidence before analysis |
| Structured extraction | Extract data against the BRSR essential indicator checklist (all 9 principles) |
| Disclosure completeness assessment | Per-principle state: Complete / Partial / Not Found |
| Scope 3 readiness classification | Four-level classification plus Materiality Claim state, as defined in Section 11 |
| Maturity signals | Extracted and displayed as supplementary context; do not affect classification |
| Gap detection | Top 5 gaps, priority-ranked, severity-rated, with citations |
| Confidence indicator | Three-level indicator with behavioural directive |
| Follow-up question generation | 3–5 supplier-facing questions derived from detected gaps |
| Source citations | Every claim linked to a BRSR section/page reference |
| Standard disclaimer | Applied to every brief without exception |

### Out of Scope — MVP (see Section 17 for full list)

Risk scoring, supplier comparison, annual report ingestion beyond BRSR chapter, GRI/CSRD/ISSB framework mapping, automated email drafting, web search enrichment, numeric Scope 3 estimation, Supplier ESG Program Signals.

---

## 17. Explicit Out-of-Scope Items

The following are confirmed exclusions from the MVP. None may be implemented or partially implemented as part of the MVP build. Each is assigned to V2, V3, or permanently excluded.

| Feature | Assignment | Reason |
|---|---|---|
| Risk scoring / escalation level recommendation | V2 | Requires judgment beyond disclosure analysis; hallucination risk high in v1 |
| Supplier ESG Program Signals (supplier's own supplier management disclosures) | V2 | Adds interpretive complexity before core loop is validated |
| Multi-supplier comparison | V2 | Requires data persistence not in MVP scope |
| Sector-adjusted gap weighting | V2 | Valid but adds configuration that delays launch |
| Annual report ingestion (beyond BRSR chapter) | V2 | Document parsing scope expansion after core is proven |
| Separate sustainability report ingestion | V2 | Widens data source scope |
| GRI framework mapping | V3 | Multi-framework translation is a separate product pillar |
| CSRD / ISSB framework mapping | V3 | Multi-framework translation is a separate product pillar |
| BRSR ↔ GRI indicator concordance | V3 | Complex mapping task; requires separate knowledge base validation |
| Web search for supplementary supplier data | V2 | Adds source reliability questions before core extraction is validated |
| CDP database lookup | V2 | External data source integration |
| Automated supplier email drafting | V2 | Follow-up questions are generated; sending them is a workflow feature |
| Supplier engagement workflow | V3 | Builds on the intelligence layer established in MVP and V2 |
| Numeric Scope 3 estimation | Never in any version | Methodology risk; estimation without disclosed data would require explicit methodology validation beyond product scope |
| Generic ESG dashboard | Permanently excluded | Not the product |
| Carbon accounting calculations | Permanently excluded | Not the product |
| Questionnaire management | Permanently excluded | Not the product |

---

## 18. Risks and Mitigations

| Risk | Likelihood | Severity | Mitigation |
|---|---|---|---|
| BRSR tables are embedded as scanned images within otherwise machine-readable documents | High | High | Document quality check (FR-02) must specifically test Principle 6 tables for machine readability. If tables fail, trigger Medium or Low confidence and surface the specific section as extraction-uncertain with a [⚠] flag. |
| Agent produces "Not Found" for disclosures that exist but are in an unexpected location or format within the document | High | High | Extraction must search the full document, not only the formally labelled BRSR section. Multiple heuristic search strategies should be applied before assigning Not Found. The Not Found language always specifies "in uploaded BRSR filing" — not "not disclosed" — to bound the claim accurately. |
| Scope 3 figure appears in text narrative rather than in the Principle 6 table | Medium | Medium | Extraction must not be limited to table cells. The full text of Principle 6 — and surrounding sections — must be searched for Scope 3 figures in numerical form. |
| Intensity-only Scope 3 figures misclassified as absolute figures (Level 2 instead of Level 1) | Medium | High | The system must apply a unit check to any Scope 3 figure candidate. Figures expressed as ratios (per crore, per tonne of output, per employee) must be classified as intensity-only and assigned Level 1 per Decision 2. |
| Materiality Claim state missed — company statement classified as Level 0 | Medium | Medium | The extraction must specifically search for materiality language ("not applicable," "not material," "not relevant," "not assessed") in the context of Scope 3. A positive match must route to Materiality Claim state, not Level 0. |
| User acts on a Low Confidence brief without reading the directive | Low | High | Low Confidence directive must be the first visible element in the output. The body of the brief must carry a persistent banner. The directive must use unambiguous language: "must not be used for procurement decisions without human review." |
| BRSR framework is updated by SEBI, invalidating the indicator checklist | Low | Medium | The indicator checklist must be maintained as a structured, versioned reference document — not hardcoded into prompts. Framework updates should trigger a checklist review, not a full product rebuild. |
| The system extracts a Scope 3 figure from a footnote disclaimer (e.g., "Scope 3 is estimated at X, but this figure is not verified") and classifies it as Level 3 | Low | High | The classification must check not only that a figure is present, but that it is presented as a primary disclosure — not as a disclaimer, estimate under review, or illustrative figure. Any figure qualified with "estimated," "approximate," or "unverified" must be classified as Level 2 (Partial) at most. |

---

## 19. Acceptance Criteria

The MVP is considered implementation-complete and ready for user testing when ALL of the following acceptance criteria pass.

### AC-01 — Upload and Processing
- [ ] A machine-readable BRSR PDF of up to 400 pages is accepted and processed without error
- [ ] Processing completes within 90 seconds of upload completion
- [ ] A structured Supplier ESG Intelligence Brief is returned as output

### AC-02 — Document Disclaimer
- [ ] The standard disclaimer (FR-11) appears as the first visible element in every brief, without exception

### AC-03 — Confidence Indicator
- [ ] Every brief carries a Confidence Indicator of High, Medium, or Low
- [ ] The Confidence Indicator is accompanied by the correct behavioural directive for its level
- [ ] A Low Confidence brief displays the directive before any analysis content
- [ ] Fields with extraction uncertainty at Medium Confidence are individually marked [⚠]

### AC-04 — Disclosure Completeness Assessment
- [ ] All nine BRSR principles appear in the completeness table
- [ ] Each principle carries a state of Complete, Partial, or Not Found
- [ ] Each state assignment carries a source citation
- [ ] Partial states name the specific indicators that drove the rating

### AC-05 — Scope 3 Readiness Classification
- [ ] Every brief contains a Scope 3 readiness verdict
- [ ] The verdict is one of: Not Found / Claim Only / Partial / Scope 3 Ready / Materiality Claim
- [ ] An intensity-only Scope 3 figure is classified as Level 1 (Claim Only), not Level 2
- [ ] A Materiality Claim state is triggered by explicit company language only, not by silence
- [ ] A Level 3 (Scope 3 Ready) classification requires both an absolute figure AND a named methodology — neither alone qualifies
- [ ] The verdict is accompanied by an evidence statement and a source citation
- [ ] Maturity signals (assurance, category boundary, SBTi, significant partners, trend data) are displayed separately and do not affect the level assignment

### AC-06 — Gap Detection
- [ ] Between one and five gaps are present in Section D of every brief
- [ ] If five or more gaps are triggered, exactly five are output in priority order
- [ ] Each gap contains: gap name, BRSR reference, severity, plain-English description, and citation
- [ ] No gap is output without a triggered condition from the gap priority framework
- [ ] The absence of a Scope 3 disclosure (Level 0 or Level 1) always triggers G-01 as the first gap

### AC-07 — Follow-Up Questions
- [ ] Between three and five questions appear in Section E, except when fewer than three gaps are detected
- [ ] Each question maps to exactly one gap from Section D
- [ ] Questions use supplier-facing language and do not contain internal classification terminology
- [ ] The highest-priority questions address Critical gaps first

### AC-08 — Source Citations
- [ ] Every factual claim of the form "supplier has disclosed X" carries a source citation referencing the BRSR section and page
- [ ] Every Not Found finding carries the standard language: "Not found in uploaded BRSR filing — [Principle X — Indicator Y checked]"
- [ ] No brief contains an uncited factual claim

### AC-09 — Graceful Failure
- [ ] When a file type other than PDF is uploaded, the system returns a clear rejection message
- [ ] When a Low Confidence condition is triggered during Quality Check, the system generates the brief with the Low Confidence banner as the first element — it does not halt silently
- [ ] When extraction fails for a specific indicator, the system returns "Not Found in Uploaded BRSR Filing" — it does not infer a state from pretrained knowledge

### AC-10 — Accuracy Validation (Domain Expert Review)
- [ ] The Scope 3 readiness classification matches the assessment of a domain expert (with BRSR knowledge) in ≥ 85% of a test set of 10 varied BRSR filings
- [ ] The completeness state per principle matches expert review in ≥ 85% of the same test set
- [ ] A domain expert rates ≥ 4 of 5 gaps as procurement-relevant in ≥ 80% of test cases
- [ ] A domain expert rates ≥ 3 of 5 follow-up questions as ready-to-use without editing in ≥ 80% of test cases

---

## 20. Future Roadmap — V2 and V3

### Version 2 — Intelligence Depth

**Theme:** Expand data sources, add maturity depth, enable comparison.

| Feature | Description |
|---|---|
| Supplier ESG Program Signals | Extract and summarise what the supplier discloses about managing its own supply chain's ESG performance (supplier audits, responsible sourcing programs, Scope 3 engagement). Displayed as a dedicated "Supplier Maturity Signals" section in the brief. |
| Multi-supplier comparison | Allow a user to assess three to five suppliers in a single session and view side-by-side completeness and Scope 3 readiness across all of them |
| Sector-adjusted gap weighting | Weight gaps by sector relevance — e.g., water disclosure absence is more severe for a manufacturing supplier than a software supplier |
| Annual report ingestion | Accept full annual reports and automatically locate the BRSR chapter without user pre-extraction |
| Separate sustainability report ingestion | Accept supplementary sustainability reports alongside the BRSR upload for cross-document validation |
| Web search enrichment | When key disclosures are absent from the uploaded BRSR, search for CDP submissions, separate sustainability reports, or GRI disclosures and surface findings as supplementary context — clearly distinguished from BRSR-derived findings |
| Year-on-year change tracking | Compare the current brief against a prior-year brief for the same supplier and flag improvements or regressions |
| Export to PDF | Generate a formatted PDF version of the brief for sharing or filing |

### Version 3 — Platform Capabilities

**Theme:** Multi-framework coverage, supplier engagement, procurement system integration.

| Feature | Description |
|---|---|
| GRI framework mapping | Map BRSR disclosures to GRI Standards indicators and identify which GRI disclosures are satisfied by existing BRSR content |
| ISSB / CSRD mapping | Map BRSR content to IFRS S1/S2 and ESRS indicators for multi-framework reporting |
| Risk scoring model | Assign a procurement risk level (Low / Medium / High / Critical) to a supplier based on completeness, Scope 3 readiness, and gap severity — calibrated by sector |
| Escalation recommendations | Recommend an escalation level (Operational / Strategic / Executive) based on risk score, with specific recommended procurement actions |
| Supplier engagement workflow | Draft and track follow-up communications to suppliers; log responses; reassess supplier status when updated documents are provided |
| Portfolio dashboard | View ESG status across an entire supplier portfolio; filter by completeness state, Scope 3 readiness, sector, and risk level |
| API for procurement system integration | Expose brief generation as an API endpoint for integration into procurement platforms (SAP, Coupa, Oracle, etc.) |
| Multi-document cross-validation | Cross-reference findings across BRSR, CDP submission, GRI report, and sustainability report for the same supplier — flag contradictions |

---

*End of Document*

**Document Status:** Approved for Implementation
**Next Step:** Architecture and Technical Design (Phase 5)
