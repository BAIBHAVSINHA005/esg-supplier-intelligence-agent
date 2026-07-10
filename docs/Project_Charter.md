# PROJECT CHARTER
## Supplier ESG Intelligence Initiative
### Prakash Industries Limited

---

```
DOCUMENT CLASSIFICATION:  Confidential — Internal Use Only
PREPARED FOR:             Prakash Industries Limited, Pune
PREPARED BY:              Meridian ESG Advisory LLP — Digital ESG Practice
DOCUMENT REFERENCE:       PIL-ESG-CHARTER-001
VERSION:                  1.0 — Approved for Execution
DATE:                     July 2026
DOCUMENT OWNER:           Chief Sustainability Officer, Prakash Industries Limited
```

---

> *"The procurement decisions we make today will define our Scope 3 footprint for the next decade. We cannot manage what we cannot see, and we cannot see what we cannot assess at scale."*
>
> — Chief Sustainability Officer, Prakash Industries Limited

---

## Table of Contents

1. Executive Summary
2. Client Background
3. Business Problem Statement
4. Current-State Process and Pain Points
5. Desired Future State
6. Project Objectives
7. Business Outcomes
8. Stakeholders
9. User Personas
10. Scope of Work
11. Out of Scope
12. Key Assumptions
13. Risks and Constraints
14. Success Metrics and KPIs
15. Project Deliverables
16. High-Level Solution Overview
17. Expected Business Benefits
18. Future Roadmap Beyond MVP
19. Acceptance Criteria Summary
20. Project Timeline Overview
21. Conclusion

**Appendix:** Executive Sponsor Summary — One-Page Brief

---

## 1. Executive Summary

Prakash Industries Limited (PIL) is a top-500 NSE-listed industrial manufacturer with annual procurement spend exceeding ₹3,200 crore across a supplier base of more than 2,200 Tier-1 vendors. As a mandatory Business Responsibility and Sustainability Report (BRSR) filer under SEBI regulations, PIL is required to assess and disclose the ESG performance of its significant value-chain partners — those contributing 2% or more of total purchases or sales.

Today, PIL's sustainability team conducts supplier ESG assessments manually. Each assessment requires an analyst to locate a supplier's BRSR filing, read and interpret a 200–400 page annual report, extract relevant environmental and governance data, and produce a structured evaluation. This process takes between 45 and 90 minutes per supplier and produces inconsistent outputs that vary by analyst. Across the 200+ assessments PIL conducts annually, this represents approximately 300 analyst-hours of low-value, repetitive work — and the outputs remain difficult to audit, benchmark, or use as evidence in PIL's own regulatory disclosures.

This project will deliver a purpose-built AI-powered Supplier ESG Intelligence Tool that transforms a supplier's publicly available BRSR filing into a structured, cited ESG Intelligence Brief in under 90 seconds. The tool will assess disclosure completeness across all nine BRSR principles, classify the supplier's Scope 3 emissions readiness, identify the five most procurement-relevant disclosure gaps, and generate ready-to-use supplier follow-up questions — with every finding traceable to the source document.

The initiative is scoped as a four-week Minimum Viable Product (MVP) designed to demonstrate measurable value before a broader platform investment is considered. The MVP targets a 95% reduction in time-per-assessment for the ESG analyst team, a standardised and auditable assessment process, and materially improved input quality for PIL's own BRSR value-chain disclosures.

---

## 2. Client Background

**Organisation:** Prakash Industries Limited (PIL)
**Established:** 1987
**Headquarters:** Pune, Maharashtra
**Listing:** National Stock Exchange (NSE) and Bombay Stock Exchange (BSE)
**Annual Revenue:** ₹8,500 Crore (FY2025)
**Employees:** 14,200 (consolidated)
**BRSR Filing Status:** Mandatory filer since FY2022–23 (Top-500 listed company)

### Business Divisions

| Division | Revenue Contribution | Key Procurement Categories |
|---|---|---|
| Automotive Components | 40% | Steel, aluminium, specialty alloys, rubber compounds |
| Industrial Equipment | 35% | Precision machined parts, hydraulics, electronics |
| Specialty Chemicals | 25% | Petrochemical feedstocks, solvents, industrial gases |

### Procurement Profile

- **Total Procurement Spend:** ₹3,200+ Crore per annum
- **Tier-1 Supplier Base:** 2,200+ active vendors
- **Significant Value-Chain Partners (BRSR threshold ≥2% of spend):** 87 suppliers
- **Annual ESG Assessments Conducted:** 200+ (covering significant partners and high-risk vendors)
- **Export Revenue:** ~28% to EU and US markets, with growing CSRD supply-chain compliance requests from European customers

### Sustainability Context

PIL appointed its first Chief Sustainability Officer (CSO) in 2022 and established a Board-level ESG Committee in 2023. PIL has filed BRSR reports for three consecutive financial years and has committed to a Net Zero operational target by 2045. However, PIL's FY2025 BRSR value-chain disclosure section received a qualified assessment from its external ESG assurance provider, citing insufficient supplier data quality and incomplete Scope 3 inventory methodology — a material risk for PIL's own BRSR Core compliance status.

PIL receives ESG questionnaires from six major European OEM customers who cite CSRD supply-chain due diligence requirements. PIL cannot respond adequately to questions about its supply chain's emissions profile without first understanding what its suppliers have disclosed.

---

## 3. Business Problem Statement

**PIL cannot assess its supply chain's ESG performance at the speed, scale, or consistency that its regulatory obligations and customer requirements demand.**

The BRSR framework requires PIL to identify its significant value-chain partners, engage them on ESG topics, and report on their performance. PIL's EU-facing customers require evidence of Scope 3 supplier engagement as part of their own CSRD compliance programmes. The Securities and Exchange Board of India has signalled increased scrutiny of value-chain disclosure quality in BRSR filings.

The core problem is not a lack of data — India's top 1,000 listed companies file detailed BRSR reports annually, and this data is publicly available. The problem is the cost and inconsistency of extracting actionable intelligence from those filings at scale. A 250-page annual report contains the BRSR disclosure within it, but reading, interpreting, and structuring that disclosure against a standard assessment framework is skilled, time-consuming work that PIL's three-person ESG team cannot perform at the required scale without significant delays to procurement decisions.

The consequence is a cascading set of business risks:

- **Regulatory risk:** PIL's BRSR value-chain disclosures remain weak, creating reputational and compliance exposure
- **Commercial risk:** PIL cannot satisfy ESG due diligence requests from EU customers, threatening ₹240+ crore in export relationships
- **Procurement risk:** Suppliers with material ESG gaps — including undisclosed labour violations or absent Scope 3 data — are approved without timely detection
- **Strategic risk:** PIL's Scope 3 emissions inventory remains incomplete, undermining its Net Zero commitments and investor-facing climate disclosures

---

## 4. Current-State Process and Pain Points

### Current Assessment Workflow

```
Supplier Identified for Assessment
         ↓
Analyst Locates Annual Report PDF (NSE/BSE website)
         ↓
Analyst Reads 200–400 Pages to Locate BRSR Chapter
         ↓
Manual Data Extraction to Excel Checklist
         ↓
Analyst Scores Against Internal ESG Criteria
         ↓
Narrative Summary Drafted in Word Document
         ↓
Review by Head of Sustainability
         ↓
Output Shared with Procurement Team
```

**Average time per assessment:** 60–90 minutes (analyst) + 20 minutes (Head of Sustainability review)
**Annual assessments conducted:** ~200
**Total analyst time consumed:** 270–310 hours per year on extraction and structuring alone

### Documented Pain Points

**Pain Point 1 — Assessment Velocity**
PIL's quarterly procurement review cycle requires ESG inputs within 5 business days of a supplier assessment request. At the current rate of 2–3 assessments per analyst per day, the team cannot service peak demand periods — particularly at financial year-end when new supplier onboarding and annual re-assessments coincide.

**Pain Point 2 — Inconsistent Outputs**
PIL has three analysts performing assessments. A review of 30 historical assessments against the same supplier BRSR filings revealed scoring variance of up to 40% on environmental completeness ratings between analysts. There is no standardised interpretation of what constitutes a "disclosed" versus "partially disclosed" Scope 3 indicator. This inconsistency makes year-on-year comparison and portfolio-level analysis unreliable.

**Pain Point 3 — Scope 3 Blind Spot**
PIL's primary ESG concern — and the area receiving the most external scrutiny — is Scope 3 emissions from its supply chain. In FY2025, PIL's ESG team assessed 87 significant suppliers. Of these, the team could confirm meaningful Scope 3 disclosures in only 19 cases. However, the team acknowledges that the remaining 68 were marked "not assessed for Scope 3" due to time constraints, not because they had no disclosure. This is not an acceptable position for a company with a Board-level Net Zero commitment.

**Pain Point 4 — Weak Audit Trail**
When PIL's external assurance provider requested evidence for value-chain disclosures in the FY2025 BRSR, the sustainability team could not consistently link disclosure claims to source document citations. Assessments existed as analyst notes in Excel files without document references. This resulted in three value-chain disclosures being qualified.

**Pain Point 5 — Supplier Engagement Delays**
Identifying what follow-up information to request from suppliers currently depends on each analyst's domain knowledge. Supplier follow-up letters are drafted from scratch for each engagement. The process from gap identification to supplier outreach takes 3–5 additional business days after the assessment is complete.

**Pain Point 6 — External Consultant Dependency**
For high-value or complex supplier assessments, PIL engages external ESG consultants at ₹15,000–25,000 per assessment. In FY2025, PIL spent approximately ₹18 lakh on external ESG assessment support — a cost that is growing as the supplier base expands.

---

## 5. Desired Future State

PIL's sustainability and procurement teams should be able to assess a supplier's BRSR disclosure in under two minutes with outputs that are structured, consistent, cited, and immediately actionable.

The desired future state has the following characteristics:

- An analyst uploads a supplier's BRSR filing (or provides the supplier's name) and receives a complete ESG Intelligence Brief within 90 seconds
- Every finding in the brief is traceable to the exact page and section of the source document — creating an audit-ready evidence trail
- Scope 3 readiness is classified using a defined, consistent framework — every analyst receives the same verdict for the same document
- The five most procurement-relevant disclosure gaps are automatically identified and ranked by severity
- Ready-to-use supplier follow-up questions are generated from detected gaps, eliminating the drafting step
- Low-quality documents or high-uncertainty extractions are flagged for human review before being acted upon — ensuring the analyst remains in the loop for consequential decisions
- PIL's value-chain BRSR disclosures are supported by structured, cited supplier intelligence data rather than analyst notes

---

## 6. Project Objectives

| # | Objective | Measurement |
|---|---|---|
| O-1 | Reduce average ESG assessment time from 60–90 minutes to under 2 minutes per supplier | Time-per-assessment measured across first 20 live assessments |
| O-2 | Standardise Scope 3 readiness classification across all assessments using a defined, documented methodology | Assessment outputs consistent regardless of which analyst uses the tool |
| O-3 | Generate audit-ready briefs with source citations for every factual claim | Zero qualified disclosures in FY2026 BRSR value-chain section |
| O-4 | Enable PIL's ESG team to assess 2× the current number of suppliers annually without additional headcount | Increased coverage with existing team |
| O-5 | Provide structured Scope 3 data inputs for PIL's own BRSR Core and Net Zero reporting | Measurable improvement in Scope 3 inventory completeness |

---

## 7. Business Outcomes

The following business outcomes are expected within 12 months of MVP deployment:

| Outcome | Expected Value |
|---|---|
| Analyst time freed from manual document extraction | 250–280 hours per year redirected to value-added ESG strategy work |
| Reduction in external ESG consultant spend | ₹12–15 lakh annual saving as routine assessments are handled in-house |
| Supplier coverage expansion | From ~200 annual assessments to 400+ with the same team |
| BRSR value-chain disclosure quality | Shift from qualified to unqualified assessments |
| Scope 3 supplier data visibility | From 22% of significant suppliers assessed for Scope 3 to 90%+ |
| EU customer ESG response capability | Structured evidence available for CSRD-related supplier questionnaires |

---

## 8. Stakeholders

| Role | Name / Function | Interest in Project | Level of Engagement |
|---|---|---|---|
| **Executive Sponsor** | Chief Sustainability Officer | Owner of BRSR compliance and ESG strategy | Decision authority |
| **Business Owner** | Head of Sustainability | Day-to-day project oversight, acceptance sign-off | Active participant |
| **Primary User Group** | ESG Analysts (×3) | Tool users — assessment workflow | High — weekly engagement |
| **Secondary User Group** | Procurement Manager — Supplier Governance | Consumes brief outputs for supplier decisions | Medium — review and feedback |
| **Internal Stakeholder** | Chief Procurement Officer | Alignment of ESG with procurement policy | Informed — monthly update |
| **Internal Stakeholder** | Chief Financial Officer | Compliance risk, audit readiness, cost savings | Informed — milestone updates |
| **Internal Stakeholder** | Company Secretary / Legal | SEBI BRSR compliance, regulatory risk | Consulted at key milestones |
| **External Stakeholder** | BRSR Assurance Provider | Evidence quality, audit trail | Consulted during acceptance testing |

---

## 9. User Personas

### Persona 1 — The Primary User: ESG Analyst (Priya)

**Role:** ESG Analyst, Sustainability Function
**Experience:** 3 years in ESG reporting, NSE-certified, BRSR-literate
**Daily Reality:** Priya spends 40% of her working week reading supplier annual reports, extracting data into Excel, and drafting supplier correspondence. She is skilled and knowledgeable, but her domain expertise is being consumed by document extraction work that does not require it.
**What she needs:** A tool that handles the extraction and structuring, so she can spend her time on interpretation, supplier engagement, and strategic input.
**Key frustration:** "I know what to look for in a BRSR. I just can't read 200 reports a year."

---

### Persona 2 — The Consumer: Procurement Manager (Rajesh)

**Role:** Manager — Supplier Governance, Procurement
**Experience:** 12 years in procurement, recently accountable for ESG integration into sourcing decisions
**Daily Reality:** Rajesh receives ESG assessments as inputs to supplier approval, renewal, and risk-escalation decisions. He does not have ESG domain expertise and needs a brief he can act on without interpretation.
**What he needs:** A clear verdict — supplier risk level, what is missing, and what to ask for — without needing to understand BRSR terminology.
**Key frustration:** "The ESG reports I receive from the analysts are detailed but inconsistent. I can't compare two suppliers side-by-side with confidence."

---

### Persona 3 — The Sponsor: Chief Sustainability Officer (Anjali)

**Role:** Chief Sustainability Officer
**Experience:** 18 years in sustainability and corporate governance; Board-level reporting responsibility
**Daily Reality:** Anjali is accountable for PIL's BRSR filing, Net Zero commitments, and ESG-related customer relationships. She needs confidence that the supplier intelligence underlying PIL's own disclosures is accurate, auditable, and scalable.
**What she needs:** Reliable, board-presentable supplier ESG data that can withstand external assurance scrutiny and satisfy EU customer requirements.
**Key concern:** "If our value-chain disclosures are qualified again this year, it affects our ESG rating and our OEM relationships."

---

## 10. Scope of Work

The MVP delivers the following capabilities, defined in full detail in the approved Product Requirements Document (PIL-PRD-001):

### In Scope

| Capability | Description |
|---|---|
| **Single supplier assessment** | Upload one BRSR PDF per assessment session; receive a complete ESG Intelligence Brief |
| **Document quality assessment** | Automated check of document readability and section detection before analysis begins |
| **Disclosure completeness** | Structured assessment of all nine BRSR principles against the BRSR essential indicator checklist |
| **Scope 3 readiness classification** | Four-level classification (Not Found / Claim Only / Partial / Scope 3 Ready) plus Materiality Claim, applied using a defined, documented decision methodology |
| **Gap identification** | Top five procurement-relevant disclosure gaps, ranked by severity, each citing the specific BRSR indicator and source section |
| **Confidence indicator** | Assessment-level quality rating (High / Medium / Low) with a clear directive on whether human review is required before acting |
| **Follow-up question generation** | Three to five supplier-facing questions, ready for direct use in correspondence |
| **Source citations** | Every factual claim in the brief traced to the specific BRSR section and page from which it was extracted |
| **Document disclaimer** | Standard disclaimer on every brief confirming the assessment is based solely on the uploaded filing |

### Assessment Workflow Supported

```
Analyst uploads BRSR PDF
        ↓
System assesses document quality
        ↓
    [If poor quality] → Human review flag surfaced before analysis
        ↓
System extracts and analyses ESG indicators
        ↓
Scope 3 verdict + completeness assessment + gap ranking produced
        ↓
Follow-up questions generated from detected gaps
        ↓
Structured ESG Intelligence Brief delivered with full citations
```

---

## 11. Out of Scope

The following are explicitly excluded from the MVP and will be addressed in V2 or V3 as documented in the approved Implementation Roadmap:

| Excluded Item | Reason / Phase |
|---|---|
| Multi-supplier comparison and portfolio view | V2 — requires data persistence infrastructure |
| Risk scoring and escalation level recommendations | V2 — requires sector-calibrated judgement models |
| Annual report ingestion (beyond dedicated BRSR filings) | V2 — document parsing complexity beyond MVP scope |
| GRI, CSRD, ISSB framework mapping | V3 — multi-framework translation is a separate product pillar |
| Supplier engagement workflow (outreach tracking, response logging) | V3 — builds on intelligence layer established in MVP |
| Automated CDP or sustainability report retrieval | V2 — external data source integration |
| Multi-user access, role-based permissions, authentication | V2 — single-user tool in MVP |
| Integration with PIL's procurement systems (SAP, Oracle) | V3 — API integration phase |
| Numeric Scope 3 estimation for non-disclosing suppliers | Permanently excluded — methodology risk unacceptable |
| Carbon footprint calculation or accounting | Not within product scope at any phase |
| Any content not in the uploaded BRSR filing | The tool reads what is disclosed; it does not estimate or infer |

---

## 12. Key Assumptions

| # | Assumption |
|---|---|
| A-1 | BRSR filings from NSE/BSE-listed companies are publicly available and accessible by PIL's ESG team |
| A-2 | Suppliers assessed in MVP are listed companies that file BRSR reports; unlisted suppliers are out of MVP scope |
| A-3 | PIL's ESG analysts are available to participate in acceptance testing during the final project week |
| A-4 | PIL will provide 10 representative BRSR filings from its supplier base for use in system testing and validation |
| A-5 | A single-user tool is acceptable for MVP — multi-user access is a V2 requirement |
| A-6 | Outputs are decision-support tools, not final procurement decisions; human review remains the standard before acting on any finding |
| A-7 | PIL's BRSR assurance provider will be available for a 2-hour consultation during acceptance testing to validate classification accuracy |
| A-8 | The tool will be deployed for internal use within PIL's network for the MVP phase; public or external access is not required |

---

## 13. Risks and Constraints

### Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Supplier BRSR filings embedded in scanned/image-based annual reports produce low extraction quality | High | High | Document quality check built into every assessment; Low Confidence flag prevents unsafe outputs from being acted on |
| Scope 3 classification produces a finding that contradicts PIL's own prior assessment of a supplier | Medium | Medium | Every classification includes source citations; analyst review is required before any escalation decision is made |
| Regulatory changes to BRSR (new indicators, revised framework) require system updates | Low | Medium | Assessment logic is maintained as a structured, version-controlled framework schema; updates require configuration changes, not system rebuilds |
| Analyst team does not adopt the tool due to low trust in AI-generated outputs | Medium | High | Human review flag, explicit confidence indicator, and source citations are designed to build trust incrementally; training session included in delivery |
| BRSR filings for specific industrial suppliers are sparse on Scope 3, reducing tool output value | High | Low | Tool is designed to surface "not found" as a valid, actionable finding — absence of disclosure is itself a procurement signal |

### Constraints

| Constraint | Description |
|---|---|
| C-1 | Four-week delivery timeline — scope must remain tightly controlled to meet the deadline |
| C-2 | Tool will be operated by PIL's existing ESG team of three analysts — no additional headcount is assumed for MVP operation |
| C-3 | MVP assesses one supplier per session — batch processing is a V2 capability |
| C-4 | Tool outputs are in English — BRSR filings that contain significant content in Hindi or regional languages will receive a lower confidence rating |

---

## 14. Success Metrics and KPIs

### Primary KPIs — MVP Launch

| KPI | Baseline (Current) | Target (MVP) | Measurement Method |
|---|---|---|---|
| Time to produce one supplier ESG assessment | 60–90 minutes | < 2 minutes | Timed measurement across 20 live assessments |
| Scope 3 readiness classification accuracy | N/A (no consistent methodology) | ≥ 85% agreement with domain expert review | Side-by-side review of 10 test cases |
| Source citation coverage | 0% (no citations in current outputs) | 100% of factual claims cited | Audit of 10 brief outputs |
| Analyst-rated gap relevance | N/A | ≥ 4 of 5 gaps rated procurement-relevant | Post-assessment analyst feedback |
| Follow-up question usability | N/A | ≥ 3 of 5 questions rated ready-to-use without editing | Post-assessment analyst feedback |

### Secondary KPIs — 90 Days Post-Launch

| KPI | Target |
|---|---|
| Annual supplier assessment capacity | Increase from ~200 to 350+ with same team |
| Significant supplier Scope 3 coverage | From 22% assessed to 60%+ |
| BRSR value-chain disclosure audit finding | Zero qualified disclosures in FY2026 filing |
| External ESG consultant spend | 30% reduction in routine assessment outsourcing |

---

## 15. Project Deliverables

| # | Deliverable | Description | Recipient |
|---|---|---|---|
| D-1 | **Supplier ESG Intelligence Tool (MVP)** | Functioning AI-powered assessment tool, installed and operational within PIL's environment | Head of Sustainability |
| D-2 | **ESG Intelligence Brief Template** | Standardised output format used for all assessments, with sections aligned to PIL's BRSR reporting requirements | Head of Sustainability, Procurement |
| D-3 | **BRSR Assessment Framework** | Documented Scope 3 classification methodology, completeness criteria, and gap priority rules — the business logic underlying the tool | CSO, Compliance |
| D-4 | **User Guide** | Step-by-step instructions for ESG analysts covering upload, interpretation of outputs, and escalation procedures | ESG Analyst Team |
| D-5 | **Acceptance Test Results** | Documented results of 10-filing validation exercise, including classification accuracy, citation coverage, and processing time | CSO, Assurance Provider |
| D-6 | **V2 Roadmap Briefing** | Business-level brief on V2 capabilities and investment requirements for CSO and CPO review | CSO, CPO |

---

## 16. High-Level Solution Overview

The Supplier ESG Intelligence Tool is an AI-powered document intelligence system purpose-built for BRSR-based supplier assessment.

At its core, the tool automates the work that an experienced ESG analyst performs manually: reading a supplier's BRSR filing, locating the relevant disclosure sections, interpreting indicator-level data against a structured framework, identifying what is missing or insufficient, and producing a procurement-ready assessment with source evidence.

### How the Tool Works — Business View

```
1. UPLOAD
   ESG Analyst uploads the supplier's BRSR PDF through a
   simple web interface.

2. DOCUMENT ASSESSMENT
   The tool immediately assesses whether the document is
   processable and locates the BRSR chapter. If quality is
   insufficient for reliable analysis, the analyst is notified
   before any assessment is produced.

3. ANALYSIS
   The tool reads the BRSR disclosure against the full indicator
   framework — nine principles, essential indicators — and
   assesses:
   → Is this indicator disclosed, partially disclosed, or absent?
   → What is the Scope 3 emissions readiness level?
   → Which gaps are most material to a procurement decision?

4. BRIEF GENERATION
   Within 90 seconds, a structured ESG Intelligence Brief is
   produced containing:
   → Disclosure completeness across all nine BRSR principles
   → Scope 3 readiness verdict with supporting evidence
   → Top five disclosure gaps with BRSR citations
   → Three to five supplier follow-up questions
   → Confidence indicator with a human review directive

5. ACTION
   The analyst reviews the brief, acts on follow-up questions,
   and uses the output as input to procurement and BRSR
   reporting workflows.
```

### What Makes This Different from Existing Approaches

Unlike generic document summarisation tools, this system:
- Applies a structured, version-controlled BRSR assessment framework — not a generic AI summary
- Produces findings grounded in specific BRSR indicator references — not general observations
- Classifies Scope 3 readiness using a defined decision methodology aligned with the PRD's classification rules — not analyst interpretation
- Distinguishes between "not disclosed" and "disclosed but insufficient" — a distinction with real procurement consequences
- Flags its own uncertainty — the confidence indicator and human review directive mean the tool is calibrated not to overstate its reliability

The tool does not replace the ESG analyst. It eliminates the extraction and structuring work so the analyst can focus on interpretation, supplier engagement, and strategic decisions.

---

## 17. Expected Business Benefits

### Quantified Benefits (Annual, Post-MVP)

| Benefit Category | Estimated Annual Value |
|---|---|
| Analyst time saving (extraction and structuring) | 250 hours × ₹1,400/hour blended rate = **₹3.5 lakh** |
| Reduction in external consultant engagement | 60 assessments × ₹15,000 average = **₹9 lakh** |
| Avoided cost of BRSR qualified disclosure | Reputational and regulatory cost avoidance (not quantified) |
| Increased supplier coverage without headcount | Value of 150+ additional assessments per year at current consultant rate = **₹22.5 lakh** |

**Total Estimated Annual Benefit:** ₹35+ lakh in quantifiable value, excluding compliance risk avoidance and commercial benefit from improved EU customer satisfaction.

### Qualitative Benefits

- **Regulatory confidence:** PIL's BRSR value-chain disclosures are supported by a documented, auditable assessment methodology — directly addressing the qualified disclosure finding from FY2025
- **Commercial protection:** PIL can respond to EU customer CSRD supplier questionnaires with structured evidence rather than narrative summaries
- **Strategic enablement:** Scope 3 supply chain data becomes available at scale for the first time, enabling meaningful progress toward PIL's Net Zero commitments
- **Team capability:** PIL's ESG team shifts from document processing to analytical and strategic work — improving retention and career development for high-value talent

---

## 18. Future Roadmap Beyond MVP

The MVP establishes the core intelligence capability. Subsequent phases build toward a comprehensive Supplier ESG Intelligence Platform.

### V2 — Intelligence Depth (3–6 months post-MVP)

| Capability | Business Value |
|---|---|
| Multi-supplier comparison view | Side-by-side ESG assessment of shortlisted vendors for procurement decisions |
| Supplier ESG maturity signals | Detect and summarise what a supplier discloses about managing its own supply chain's ESG performance |
| Annual report ingestion | Accept full annual reports; automatically locate the BRSR chapter — no pre-extraction required |
| Sector-adjusted assessment | Gap severity weighted by sector — water disclosure absence is more critical for a chemical supplier than an IT services vendor |
| Peer benchmarking | Compare a supplier's BRSR disclosure quality against sector peers |
| Year-on-year trend tracking | Monitor whether a supplier's disclosure quality is improving or deteriorating across successive filings |

### V3 — Platform and Integration (12–18 months post-MVP)

| Capability | Business Value |
|---|---|
| GRI and ISSB framework mapping | PIL satisfies EU customer questionnaires using existing supplier BRSR data, mapped to the frameworks customers request |
| Supplier engagement workflow | Draft, send, and track follow-up requests to suppliers; log responses and reassess when updated disclosures are provided |
| Risk scoring and escalation | AI-generated procurement risk classification with recommended escalation action (Operational / Strategic / Executive) |
| Procurement system integration | ESG Intelligence Briefs accessible directly within PIL's procurement approval workflow |
| Portfolio-level ESG dashboard | Supply chain ESG exposure at a portfolio level — by category, geography, and risk tier |

---

## 19. Acceptance Criteria Summary

The MVP will be accepted as complete when the following criteria are met. Full acceptance criteria are documented in the Product Requirements Document (PIL-PRD-001, Section 19).

| Criteria Group | Summary Requirement |
|---|---|
| **Processing Performance** | Any standard BRSR PDF processed to a complete brief in under 90 seconds |
| **Disclaimer** | Standard document scope disclaimer appears on every brief, without exception |
| **Confidence Indicator** | Every brief carries a confidence rating; Low Confidence briefs display a human review directive before any analysis content |
| **Completeness Assessment** | All nine BRSR principles assessed and displayed with source citations |
| **Scope 3 Classification** | Verdict is one of five defined states; intensity-only disclosures classified as Claim Only (not Partial); Materiality Claims identified separately |
| **Gap Detection** | Minimum three, maximum five gaps produced per brief; each gap carries a BRSR indicator reference and source citation |
| **Follow-Up Questions** | Three to five supplier-facing questions generated; ready for direct use without editing in ≥ 3 of 5 cases |
| **Citation Coverage** | 100% of factual claims traceable to source section; no uncited claims in any brief |
| **Graceful Failure** | Scanned or unprocessable documents handled cleanly with a clear failure message — no silent failures, no misleading outputs |
| **Classification Accuracy** | Scope 3 verdict agrees with PIL domain expert review in ≥ 4 of 5 validation test cases |
| **Operational Readiness** | Tool runs from documented setup instructions; PIL ESG analysts can complete training within half a day |

---

## 20. Project Timeline Overview

The MVP will be delivered in four consecutive weeks from project commencement. Week-by-week milestones are as follows:

| Week | Milestone | Business Outcome |
|---|---|---|
| **Week 1** | Document Intelligence Foundation | System can ingest a BRSR PDF, assess its quality, and classify documents as processable or requiring human review |
| **Week 2** | ESG Analysis Engine | System produces Scope 3 readiness classification, BRSR completeness assessment, and top-five gap identification against validated test documents |
| **Week 3** | Knowledge Integration | System applies PIL's ESG knowledge base to contextualise extractions; all nine BRSR principles assessed with accurate gap detection |
| **Week 4** | User Interface, Validation, and Handover | Working user interface; end-to-end validation against 10 real supplier BRSR filings; acceptance test completion; user guide delivered |

**Go-Live Target:** End of Week 4

**Post-Go-Live:** Two weeks of supported usage with PIL's ESG analyst team, followed by a V2 planning session.

### Key Dates

| Date | Event |
|---|---|
| Week 1, Day 1 | Project kickoff; PIL provides 10 BRSR test filings |
| Week 2, Day 5 | Mid-point review with Head of Sustainability |
| Week 4, Day 3 | Acceptance testing with PIL ESG team and assurance provider consultation |
| Week 4, Day 5 | Final delivery, sign-off, and V2 roadmap briefing |

---

## 21. Conclusion

PIL operates at a critical inflection point in India's ESG disclosure landscape. SEBI's BRSR framework is maturing, value-chain disclosure requirements are tightening, and PIL's European customers are placing CSRD-driven compliance pressure on their Indian supply chains. PIL's internal ESG team has the knowledge and motivation to address these requirements — but is constrained by the manual, inconsistent, and time-intensive processes that currently define supplier ESG assessment.

The Supplier ESG Intelligence Initiative directly addresses this constraint. By deploying a purpose-built AI-powered assessment tool, PIL will transform its supplier ESG capability from a bottleneck into a competitive differentiator — assessing more suppliers, producing more reliable outputs, and supporting stronger regulatory disclosures, all with the same team.

The four-week MVP is deliberately scoped to demonstrate measurable value before requiring broader investment. Its success will be defined not by technical complexity but by one simple outcome: when an ESG analyst uploads a BRSR filing, they receive in under two minutes a structured, cited, and actionable brief that would have taken them 90 minutes to produce manually.

The foundation built in this MVP is designed to support a three-phase platform roadmap. The ESG intelligence capability developed here — reading supplier disclosures, extracting structured findings, and identifying actionable gaps — becomes the core of a broader Supplier ESG Platform that will eventually support multi-framework reporting, supplier engagement workflows, and procurement system integration.

Meridian ESG Advisory LLP is committed to delivering a product that serves PIL's ESG analysts today and scales with PIL's ambitions over the coming three years.

---

*Approved for Execution*

| Role | Name | Signature | Date |
|---|---|---|---|
| Chief Sustainability Officer | *To be signed* | | |
| Head of Sustainability | *To be signed* | | |
| Project Lead, Meridian ESG Advisory | *To be signed* | | |

---
---

# APPENDIX — EXECUTIVE SPONSOR SUMMARY
## One-Page Brief for Senior Leadership Review

```
PREPARED FOR:   CFO / Chief Procurement Officer / Chief Sustainability Officer / Board ESG Committee
CLASSIFICATION: Confidential
DATE:           July 2026
```

---

### THE PROBLEM IN ONE PARAGRAPH

PIL assesses 200+ supplier BRSR filings every year to meet its own BRSR value-chain disclosure obligations and satisfy ESG due diligence requests from European OEM customers. Today, each assessment takes a skilled ESG analyst 60 to 90 minutes of manual document reading, data extraction, and report writing. The outputs are inconsistent, uncited, and difficult to audit. PIL's FY2025 BRSR value-chain disclosures received a qualified assessment as a direct result. PIL cannot currently tell its Board, its assurance provider, or its EU customers what its supply chain's Scope 3 emissions profile looks like — not because the data does not exist, but because extracting and structuring it manually is beyond the capacity of a three-person team.

---

### WHAT WE ARE BUILDING

A purpose-built AI-powered tool that reads a supplier's BRSR filing and produces a structured, cited ESG Intelligence Brief in under 90 seconds. The brief tells the analyst: how complete the supplier's ESG disclosure is across all nine BRSR principles, whether the supplier's Scope 3 emissions data is usable for PIL's own reporting, the five most important gaps in the disclosure, and the exact questions to send the supplier to close those gaps. Every finding references the specific page and section from which it was extracted.

---

### WHAT THIS COSTS AND WHAT IT DELIVERS

| Item | Detail |
|---|---|
| **Delivery timeline** | Four weeks |
| **Estimated annual benefit** | ₹35+ lakh in analyst time saving and reduced external consultant spend |
| **Compliance impact** | Eliminates the conditions that produced PIL's qualified BRSR disclosure in FY2025 |
| **Commercial impact** | Enables structured responses to CSRD supplier due diligence requests from EU customers |
| **Capacity impact** | PIL's ESG team assesses 350+ suppliers per year instead of 200, with no additional headcount |

---

### THE THREE NUMBERS THAT MATTER

> **90 seconds** — time to produce an assessment that currently takes 90 minutes
>
> **₹35 lakh** — estimated annual value of time and cost savings
>
> **87 significant suppliers** — PIL's BRSR-mandated value-chain partners; currently assessed inconsistently; all will be assessed systematically and auditability within 90 days of go-live

---

### WHAT WE ARE NOT BUILDING

This is not a carbon accounting platform. It is not a procurement system replacement. It does not estimate emissions or generate data that does not exist in supplier filings. It reads what suppliers have disclosed and produces a structured, traceable, and consistent assessment of that disclosure. The analyst and the procurement manager remain the decision-makers.

---

### THE ASK

**Approve the four-week MVP.** Provide 10 representative supplier BRSR filings for validation testing. Make the ESG analyst team available for a half-day acceptance testing session in Week 4. The investment is one person's focused effort over four weeks. The return is a permanently transformed supplier ESG assessment capability and materially reduced regulatory exposure in PIL's FY2026 BRSR filing.

---

*For full detail, refer to: PIL-ESG-CHARTER-001 — Project Charter v1.0*
*Contact: Head of Sustainability, Prakash Industries Limited*
