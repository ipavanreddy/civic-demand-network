# AI-Powered Multilingual Citizen Development Request Platform

## Product Requirements Document (PRD)

**Document Version:** 2.0 (aligned to the PRD 04 template)
**Working Name:** JanVaani (जनवाणी)
**Track:** 1: Citizen feedback → national infrastructure priorities
**Product Type:** AI-powered Civic Intelligence Platform / Digital Public Good
**Target Geography:** India
**Primary User:** Citizen
**Secondary User:** Planning Officer (district / state / national policymaker)
**Primary Objective:** Turn multilingual citizen development requests into structured, geo-located demand signals, fuse them with public infrastructure data, and give policymakers explainable, ranked project recommendations on top of an interoperable foundation any state can plug into.

---

# 1. Executive Summary

Citizens across India raise development needs (roads, drinking water, sanitation, schools, health facilities, connectivity) through many disconnected channels: grievance portals, helplines, Gram Sabha meetings, social media and messaging apps. These requests are rarely consolidated, rarely compared against official infrastructure data, and rarely influence where public money goes.

The proposed solution is an **AI-powered multilingual citizen demand intelligence platform** that:

1. **Collects requests** by voice, text and messaging app in regional languages.
2. **Understands each request** with AI (category, location, urgency, beneficiaries).
3. **Groups similar requests** into demand clusters.
4. **Combines demand with public data** (demographics, infrastructure gaps, existing investments).
5. **Surfaces demand hotspots** on a map.
6. **Recommends high-priority projects** with a transparent, explainable score and AI-generated evidence briefs.
7. **Provides a common data and API architecture** so states can join without rebuilding the platform.

The hackathon MVP will focus on a single, polished end-to-end journey:

> **Citizen Voice → AI Understanding → Location → Demand Cluster → Data Fusion → Priority Score → Policymaker Recommendation**

The prototype will also show that the same architecture supports several Indian states and languages.

---

# 2. Problem Statement

## 2.1 Core Problem

Governments across India struggle to consolidate citizen feedback and align it with national infrastructure priorities.

Development requests currently:

- Arrive through fragmented channels (portals, helplines, paper petitions, messaging apps)
- Are written or spoken in many languages and dialects
- Lack structured location and category information
- Are duplicated across channels and people
- Are rarely compared with demographic or infrastructure-gap data
- Are rarely compared with sanctioned or ongoing public investment

This creates several risks:

- Misaligned public spending
- Unaddressed infrastructure gaps, especially in under-served areas
- Louder or better-connected areas dominating attention
- No feedback to citizens on what happened to their requests
- No way to measure the impact of large-scale digital public infrastructure (DPI) initiatives

---

# 3. Challenge

The challenge is to build a **scalable, multilingual AI platform, designed as a Digital Public Good**, that:

- Aggregates citizen development requests via **voice, text and messaging apps**.
- Works across India's **diverse linguistic regions**.
- Analyses large datasets that combine citizen feedback with **national demographic data, infrastructure indices and public investment plans**.
- Surfaces **demand hotspots**.
- **Recommends high-priority development projects** to national policymakers.
- Uses AI meaningfully rather than as a generic chatbot.
- Can scale beyond one district or state through common interfaces.

---

# 4. Product Vision

> **Build a civic intelligence layer where any citizen can speak a need in their own language, and every policymaker sees ranked, evidence-backed demand next to the gaps in the data.**

Long term, the platform should function as a **digital public good**, where:

- States keep their citizen data and local datasets.
- A common data contract defines how development requests, locations and indicators are represented.
- Shared APIs expose demand intelligence.
- AI services operate on standardised inputs.
- New states are onboarded through data adapters rather than a rebuilt application.

---

# 5. Product Goals

## 5.1 Primary Goals

1. Let citizens submit development requests by voice, text or messaging app in regional languages.
2. Use Google AI to turn unstructured requests into structured records.
3. Resolve each request to a standard administrative location (LGD code).
4. Group duplicate and related requests into demand clusters.
5. Combine demand with at least three public data dimensions (demographics, infrastructure gap, investment).
6. Compute a transparent, configurable Priority Score.
7. Generate grounded AI evidence briefs for recommended projects.
8. Give planning officers a hotspot map and ranked recommendation list.
9. Demonstrate a common data model that supports several states.
10. Deliver a working, deployed end-to-end prototype.

## 5.2 Secondary Goals

- Establish reusable civic demand APIs.
- Send status updates back to citizens.
- Show a lightweight before/after impact view for completed projects.
- Support future demand forecasting.

---

# 6. Non-Goals for the Hackathon MVP

The prototype will not become a full e-governance or grievance-redressal system.

Out of scope for the MVP:

- Individual grievance resolution workflows (the product is about development demand, not complaint closure)
- Integration with production CPGRAMS or state CM helplines (an adapter design only)
- Aadhaar-based identity verification
- Budget allocation or fund release
- Tendering, procurement or project execution tracking
- Automated decisions. The platform **recommends** and humans decide.
- Social / public voting features
- Full IVR telephony (roadmap)

---

# 7. Target Users

The MVP contains only two application roles.

## 7.1 Primary User: Citizen

The citizen is the primary beneficiary and the source of demand signals.

### Characteristics

- Rural or urban resident
- Mobile-first, often on a messaging app
- May have limited literacy or digital literacy
- Often prefers speaking in a regional language or dialect
- Wants to be heard and to know what happened next

### Primary Questions

The platform should help answer:

- How can I report a need for my village or ward easily?
- Was my request understood correctly?
- Have others raised the same need?
- What is the status of this need?

---

## 7.2 Secondary User: Planning Officer

The Planning Officer represents the government side: a district planning officer, a state department official or a national policymaker. Access is scoped by geography (district, state or national).

### Primary Needs

The Planning Officer should be able to:

- View demand hotspots by category and geography.
- Compare citizen demand with infrastructure-gap and demographic data.
- See which areas already have sanctioned investment.
- Review a ranked list of recommended projects with evidence.
- Adjust prioritisation weights to reflect policy priorities.
- Export a briefing note.

### MVP Scope

The Planning Officer experience is primarily analytical:

- Dashboard
- Hotspot map
- Ranked recommendations
- Evidence briefs
- Policy-weight adjustment
- State comparison / configuration

Administrative workflows (approvals, budget release) are outside the MVP.

---

# 8. Core Product Experience

The product centres on one high-quality end-to-end journey:

```text
Citizen
   ↓
Speak / Type / Message a Request
   ↓
Speech-to-Text + Translation
   ↓
AI Request Understanding (category, location, urgency, beneficiaries)
   ↓
Location Resolution (LGD code)
   ↓
Confirmation to Citizen (in their language, text + voice)
   ↓
Demand Clustering
   ↓
Fusion with Demographic + Infrastructure + Investment Data
   ↓
Priority Score
   ↓
AI Evidence Brief
   ↓
Planning Officer Dashboard: Hotspot + Ranked Recommendation
   ↓
Status Update to Citizen
```

This journey is the primary demonstration for the hackathon.

---

# 9. Module 1: Citizen Request Intake

## Purpose

Let citizens submit development requests through the channels they already use.

### Channels (MVP)

- **Web / PWA**: text, voice recording, optional photo
- **Messaging app bot**: Telegram for the hackathon (fast to set up), with the WhatsApp Business Cloud API as the production target
- **Voice**: voice notes via the PWA or bot

### Request Data

- Request ID
- Channel
- Language
- Original text / audio reference
- Optional photo
- Optional location pin
- Timestamp
- Citizen reference (hashed phone number or demo profile)

### Requirements

The system must allow a citizen or demo user to:

- Submit a request by voice or text.
- Optionally share a location or photo.
- Receive an acknowledgment with a request ID.
- Correct the AI's understanding if it is wrong.

---

# 10. Module 2: Speech & Language

## Purpose

Make the platform accessible across linguistic regions.

### MVP Languages

The prototype should demonstrate at least:

- English
- Hindi
- Telugu

The architecture should support additional Indian languages (Tamil, Kannada, Marathi, Bengali, Malayalam, Gujarati, Punjabi, Odia and others) through configuration only.

### Flow

```text
Citizen Speech
     ↓
Speech-to-Text (language detection)
     ↓
Translation to canonical language (original retained)
     ↓
AI Understanding
     ↓
Response in citizen's language
     ↓
Text-to-Speech (where supported)
```

### Requirement

Analysis runs on the canonical (English) text. Changing the presentation language does not trigger re-analysis. The original-language text is always stored for audit.

---

# 11. Module 3: AI Request Understanding

## Purpose

Convert unstructured, often code-mixed requests into structured records.

### Google AI Role

**Gemini** extracts structured fields using a defined JSON schema. It must not invent locations, numbers or facts that are not present in the request.

### Output Fields

- Category (from a fixed taxonomy aligned to government scheme heads)
- Sub-category
- Short summary
- Location mentions
- Urgency and reason
- Estimated beneficiaries (only if stated)
- Vulnerable groups mentioned
- Seasonality (e.g. "every monsoon")
- Sentiment
- Confidence
- Missing information

### Category Taxonomy (MVP)

```text
roads_bridges · drinking_water · sanitation · electricity · health_facility ·
school_education · digital_connectivity · housing · irrigation · public_transport · other
```

### Example

```text
Input (Hindi voice, translated):
"Our village Sonbarsa has no bridge over the river. Children miss school for 3 months every monsoon."

Category: Roads & Bridges → Bridge
Location: Sonbarsa (village)
Urgency: High, because of seasonal loss of school access
Vulnerable groups: Children
Confidence: 0.88
```

---

# 12. Module 4: Location Resolution

## Purpose

Attach every request to a standard administrative unit so it can be joined with public data.

### Approach

- Match location mentions against **LGD** (Local Government Directory) village, ward, block and district names, restricted to the citizen's state and district where known.
- Use a location pin or Google Maps Geocoding where available.
- If the match is ambiguous, ask the citizen one clarification question ("Which block is Sonbarsa in?").

### Output

- LGD state, district, block and village/ward codes
- H3 grid cell (for hotspot mapping)
- Resolution method (pin / exact match / fuzzy match / clarified)
- Resolution confidence

---

# 13. Module 5: Demand Clustering

## Purpose

Merge many differently worded requests about the same need into a single **demand cluster**.

### Approach

- Generate text embeddings (Vertex AI embeddings) for each request summary.
- Group requests by semantic similarity **and** the same category **and** the same or neighbouring location.
- Use BigQuery vector search for similarity lookup.

### Cluster Data

- Cluster ID
- Category
- Locations covered
- Number of requests
- Number of unique citizens
- First seen / last seen
- AI cluster summary
- Representative quotes (translated)

---

# 14. Module 6: Data Fusion

## Purpose

Put citizen demand in context with official data.

### Data Dimensions

The MVP must combine at least three dimensions with citizen demand:

1. **Demographics**: population, SC/ST share, literacy (Census)
2. **Infrastructure gap**: category-specific indicators (e.g. tap-water coverage, all-weather road access, school facilities)
3. **Public investment**: sanctioned or ongoing projects in the same area and category

### Requirement

Every indicator shown must carry its source, reference year and geographic level.

---

# 15. Priority Score

The prototype should present an easy-to-understand priority score for each demand cluster.

Example:

```text
Priority Score
82 / 100
High
```

### Factors

- Demand intensity
- Infrastructure gap
- Vulnerability
- Demand trend
- Existing investment coverage

### MVP Implementation

Public spending decisions must be **auditable**, so the score uses a **transparent weighted model**:

```text
Priority Score =
  Demand Intensity × 30%        (requests per 10k population, recency-weighted)
+ Infrastructure Gap × 30%      (category-specific gap indicator)
+ Vulnerability × 20%           (demographic vulnerability indicators, aspirational district flag)
+ Demand Trend × 10%            (growth in requests over time)
− Investment Coverage × 10%     (sanctioned/ongoing projects already covering the need)
```

All factors are normalised within the selected geography. The weights are configurable in the dashboard (a "policy lens"), and every change is recorded.

### Future Evolution

Add a Vertex AI / BigQuery ML demand-forecasting component for the trend factor. The final ranking stays explainable.

---

# 16. Module 7: AI Evidence Briefs

## Purpose

Explain each recommendation in plain language so an official can act on it.

### Google AI Role

**Gemini** writes a short evidence brief **only from the structured cluster and indicator data supplied**.

### Brief Output

1. Recommendation summary
2. Citizen demand evidence (count, representative quotes)
3. Data evidence (each point cites dataset, value and year)
4. Existing investment context
5. Estimated beneficiaries (from data, not guessed)
6. Uncertainties and missing data
7. Suggested next step

### Example

```text
Recommended Project: Bridge – Sonbarsa, Gaya (Bihar)

Citizen Demand
• 146 requests from 3 villages over 60 days; monsoon school access is the main concern.

Data Evidence
• Population of the 3 villages: 8,420 (Census 2011).
• No all-weather road connection recorded (sample infrastructure dataset).
• No sanctioned bridge project in this block (sample investment dataset).

Uncertainty
• Exact river crossing point not confirmed. A field verification is recommended.
```

---

# 17. Module 8: Planning Officer Dashboard

## Purpose

Show how citizen-level requests aggregate into regional and national intelligence.

### Dashboard Levels

```text
India
 ↓
State
 ↓
District
 ↓
Block / Ward
```

### Dashboard Metrics

- Requests received
- Unique citizens
- Demand clusters
- Top categories
- Demand hotspots
- Infrastructure gap indicators
- Existing investment coverage
- Ranked recommendations

### Map View

The dashboard should visualise:

- Demand hotspots (H3 / district choropleth)
- Category filters
- Infrastructure-gap overlay
- Investment overlay

The MVP can use realistic sample aggregated data, clearly labelled, where live state datasets are unavailable.

---

# 18. Module 9: Impact View (Lightweight)

## Purpose

Address the brief's point that governments have "no way to measure the impact" of infrastructure and DPI initiatives.

### MVP Scope

For a project marked "completed" (sample data), show:

- Request volume for that category and area before and after completion
- Sentiment trend before and after
- Comparison with similar areas that had no project

This is a demonstration view. A rigorous impact evaluation is on the roadmap.

---

# 19. Module 10: Citizen Status Updates

## Purpose

Close the loop so citizens know their voice was heard, which builds the trust needed for continued participation.

### Status Lifecycle

```text
Received → Understood → Clustered → Under Review → Recommended → Sanctioned → Completed
```

### Requirements

- Every request links to its cluster status.
- Citizens can check status by request ID (web or bot).
- Status changes can trigger a short message in the citizen's language (secondary goal for the MVP).

---

# 20. Module 11: Interoperability Layer

This is a core architectural requirement and a major differentiator of the solution.

## Objective

Provide a common data and service structure so different Indian states can participate without separate applications.

### Core Principle

> **State-specific data, common interfaces.**

Each state may have:

- Different grievance and request systems
- Different languages
- Different infrastructure datasets and schemes
- Different investment-tracking systems
- Different local priorities

But the platform exposes a standardised canonical representation.

---

# 21. Common Civic Demand Data Model

Example:

```json
{
  "state": "BR",
  "district": "Gaya",
  "lgd": { "district_code": "XXX", "block_code": "XXXX", "village_code": "XXXXXX" },
  "request_id": "REQ-001",
  "channel": "telegram",
  "language": "hi",
  "category": "roads_bridges",
  "sub_category": "bridge",
  "urgency": "high",
  "summary_en": "No bridge over river; children miss school during monsoon.",
  "cluster_id": "CL-0042",
  "indicators": {
    "population": 8420,
    "all_weather_road_access": false
  },
  "investment": {
    "sanctioned_projects_in_area": 0
  }
}
```

The same structure should support examples such as:

```text
Bihar → Bridges & rural roads (Hindi)
Andhra Pradesh → Drinking water (Telugu)
Maharashtra (urban ward) → Public transport (English / Marathi)
```

The MVP does not need complete state coverage. It needs to prove that the architecture is state-agnostic.

---

# 22. Interoperability Principles

## 22.1 Common Interfaces

State-level request sources and dashboards use compatible APIs.

## 22.2 Canonical Schema

Core concepts have common definitions for:

- Citizen (pseudonymous)
- Request
- Location (LGD)
- Category
- Demand Cluster
- Indicator
- Investment
- Recommendation

## 22.3 State Data Adapters

A state-specific adapter transforms local formats (state grievance exports, local indicator tables, investment lists) into the canonical schema.

```text
State Dataset
     ↓
State Adapter
     ↓
Canonical Civic Demand Schema
     ↓
Shared Platform Services
```

## 22.4 Model Portability

Extraction prompts, clustering and scoring consume standardised structures, so they work in any state.

## 22.5 API-First Design

External government and partner applications should eventually be able to consume:

- Demand clusters
- Hotspots
- Priority scores
- Evidence briefs
- Aggregated, de-identified open data

---

# 23. System Architecture

```text
                         CITIZEN
                            │
            ┌───────────────┼───────────────┐
            │               │               │
         Web/PWA      Messaging Bot       Voice
            │               │               │
            └───────────────┼───────────────┘
                            ▼
                     Next.js Frontend / Bot Webhook
                            │
                            ▼
                        API Layer
                            │
     ┌──────────────┬───────┴───────┬───────────────┐
     ▼              ▼               ▼               ▼
 Intake Service  Understanding   Location       Clustering &
                 Service         Service        Scoring Service
     │              │               │               │
     └──────────────┴───────┬───────┴───────────────┘
                            ▼
                    Civic Data Layer
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
      BigQuery          Firebase         Cloud Storage
          │
   ┌──────┴──────────────────────┐
   ▼                             ▼
Public Data                  State Data
 ├── Census / Demographics    ├── Bihar
 ├── Infrastructure gaps      ├── Andhra Pradesh
 ├── Investment plans         ├── Maharashtra
 └── LGD codes                └── Other States
   └─────────────┬───────────────┘
                 ▼
            AI / ML Layer
                 │
     ┌───────────┼────────────┐
     ▼           ▼            ▼
  Gemini    Vertex AI     Speech / Translation
            Embeddings    / Text-to-Speech
     └───────────┼────────────┘
                 ▼
   Structured Request → Cluster → Score → Evidence Brief
                 │
         ┌───────┴────────┐
         ▼                ▼
 Citizen Confirmation   Planning Officer Dashboard
```

---

# 24. Recommended Technology Stack

## 24.1 Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS
- shadcn/ui
- PWA capabilities
- Google Maps JavaScript API (+ deck.gl H3 layer for hotspots)

### Frontend Responsibilities

- Citizen request form (text, voice, photo)
- Request confirmation and status
- Language switching
- Planning Officer dashboard
- Hotspot map
- Ranked recommendations and evidence briefs
- Policy-weight controls

---

# 25. Backend

## Recommended

**Google Cloud Run**

Backend may be implemented using:

- FastAPI / Python for AI and data services
- Node.js for the messaging bot webhook where convenient

### Responsibilities

- API routing
- Messaging bot webhook
- Request intake
- AI orchestration
- Location resolution
- Clustering and scoring jobs
- State adapters
- Authentication / authorisation
- Evidence brief generation

---

# 26. Google AI Technology Stack

## Gemini API / Vertex AI

Use for:

- Structured request extraction
- Clarification questions
- Cluster summaries
- Evidence briefs
- Plain-language explanations of rankings

## Vertex AI Embeddings

Use for:

- Semantic similarity between requests
- Demand clustering

## Vertex AI / BigQuery ML

Use for:

- Demand trend forecasting (future / optional in MVP)
- Model training and serving

## Cloud Speech-to-Text, Text-to-Speech, Translation API

Use for:

- Voice input in regional languages
- Canonical-language translation
- Spoken confirmations

## Google AI Studio

Use for:

- Prompt experimentation
- Evaluating extraction behaviour
- Initial prompt development

---

# 27. Geospatial Stack

## Google Maps Platform

- Location pin capture
- Geocoding support for location resolution
- Hotspot map visualisation

## Administrative Boundaries

- LGD codes for administrative units
- Boundary geometry from open sources such as ISRO Bhuvan (licence cited)

---

# 28. Data Platform

## BigQuery

Primary analytical store for:

- Structured requests
- Demand clusters
- Public indicators
- Investment data
- Embeddings and vector search
- Scores and analytics

## Firebase

Use for:

- Authentication (Planning Officer)
- Citizen request status
- Lightweight application state

## Cloud Storage

Use for:

- Voice recordings
- Photos
- Exported briefing notes

---

# 29. Public Data Sources

The architecture should be able to consume data from sources such as:

- **LGD**: Local Government Directory (administrative codes)
- **Census 2011**: population and village amenities (data.gov.in)
- **Mission Antyodaya**: village-level infrastructure gaps
- **NFHS-5**: district vulnerability indicators
- **PMGSY**: rural road connectivity and sanctioned roads
- **Jal Jeevan Mission**: tap-water coverage
- **UDISE+**: school infrastructure
- **NITI Aayog**: Aspirational Districts list
- data.gov.in and state open-data portals

Where live APIs are unavailable during the hackathon, use realistic sample or cached public data.

Every dataset must keep its source metadata and timestamps.

---

# 30. Data Architecture

```text
Citizen Channels            Public / State Sources
      │                              │
      ▼                              ▼
Request Ingestion            Data Ingestion
      │                              │
      ▼                              ▼
AI Understanding            Validation / Normalisation
      │                              │
      ▼                              ▼
Location Resolution          State Adapter (where needed)
      │                              │
      └──────────────┬───────────────┘
                     ▼
        Canonical Civic Demand Schema
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
       BigQuery          Embeddings / Features
          │                     │
          └──────────┬──────────┘
                     ▼
         Clustering + Scoring + Gemini
                     │
                     ▼
        Hotspots / Recommendations / Briefs
```

---

# 31. Core Data Entities

## Citizen

```text
citizen_id (pseudonymous)
phone_hash
preferred_language
state
district
consent_given_at
created_at
```

## Request

```text
request_id
citizen_id
channel
language
text_original
text_en
audio_url
photo_url
category
sub_category
urgency
est_beneficiaries
sentiment
confidence
lgd_state / lgd_district / lgd_block / lgd_village
h3_cell
resolution_method
cluster_id
created_at
model_name
model_version
prompt_version
```

## Demand Cluster

```text
cluster_id
category
lgd_codes[]
h3_cells[]
request_count
unique_citizens
first_seen
last_seen
summary
status
```

## Indicator

```text
lgd_code
indicator_name
value
year
geographic_level
source
```

## Investment

```text
project_id
scheme
category
lgd_codes[]
status
sanctioned_amount
start_date
source
```

## Recommendation

```text
recommendation_id
cluster_id
priority_score
score_breakdown
weights_used
evidence_brief
generated_at
language
model_name
model_version
prompt_version
```

---

# 32. AI Orchestration Architecture

AI services follow a predictable pipeline.

```text
Citizen Request
      ↓
Speech-to-Text / Translation
      ↓
Construct AI Input (text + channel + known location context)
      ↓
Gemini Structured Extraction
      ↓
Schema Validation
      ↓
Location Resolution
      ↓
Clustering (Embeddings)
      ↓
Data Fusion + Priority Score (deterministic)
      ↓
Gemini Evidence Brief (from structured data only)
      ↓
Number-Grounding Validation
      ↓
Localisation
      ↓
Presentation
```

The ranking is always computed deterministically. Gemini explains it and never changes it.

---

# 33. Structured AI Output

AI services return structured outputs rather than free text.

## Request Extraction

```json
{
  "category": "roads_bridges",
  "sub_category": "bridge",
  "summary_en": "No bridge over river; children miss school during monsoon.",
  "location_mentions": [{ "text": "Sonbarsa", "type": "village" }],
  "urgency": "high",
  "urgency_reason": "Seasonal loss of school access",
  "est_beneficiaries": null,
  "vulnerable_groups": ["children"],
  "seasonality": "monsoon",
  "sentiment": -0.6,
  "confidence": 0.88,
  "missing_information": ["block/district not stated"],
  "requires_clarification": true
}
```

## Evidence Brief

```json
{
  "title": "Bridge – Sonbarsa, Gaya",
  "summary": "High citizen demand with no existing investment.",
  "demand_evidence": ["146 requests from 3 villages in 60 days"],
  "data_evidence": [
    { "claim": "Population 8,420", "source": "Census 2011", "field": "population" }
  ],
  "uncertainties": ["Exact crossing point unverified"],
  "next_step": "Field verification by block engineer",
  "confidence": 0.8
}
```

---

# 34. Prompt Architecture

Use specialised prompts for distinct capabilities.

## 34.1 Request Extraction Prompt

### Inputs

- Translated text (+ original)
- Channel
- Known state/district (if available)
- Category taxonomy

### Requirements

- Use only the fixed taxonomy.
- Never invent locations or numbers.
- Mark missing information explicitly.
- Return structured JSON.
- Ask for clarification when confidence is low.

## 34.2 Evidence Brief Prompt

### Inputs

- Cluster data
- Indicator rows (with source and year)
- Investment rows
- Score breakdown

### Requirements

- Use only the supplied data.
- Cite the source for every number.
- Separate citizen demand from official data.
- State uncertainties.
- Recommend next steps, not final decisions.
- Return structured JSON.

---

# 35. AI Safety & Trust

The platform must distinguish between:

```text
Citizen Statement
      ↓
Official Data
      ↓
AI Interpretation
      ↓
Recommendation
```

### Requirements

- Never fabricate numbers, populations or indicator values.
- Never change the deterministic ranking in AI text.
- Show confidence for extraction and location resolution.
- Show data freshness and source for every indicator.
- Keep a human decision for every recommendation.
- Don't let repeated submissions from the same citizen inflate demand.
- Avoid bias toward digitally connected areas (per-capita normalisation, assisted capture on the roadmap).

---

# 36. Data Freshness

Every data source should expose freshness metadata.

Example:

```text
Citizen Requests
Last received: 3 minutes ago

Infrastructure Gap (Tap Water)
Reference year: 2024 (sample)

Population
Census 2011
```

The officer should understand whether a recommendation is based on:

- Recent citizen demand
- Older census baselines
- Latest available official data

---

# 37. API Architecture

## Citizen / Requests

```http
POST /api/requests
GET  /api/requests/:id
POST /api/requests/:id/confirm
POST /api/webhooks/messaging
```

## Language / Voice

```http
POST /api/speech-to-text
POST /api/translate
POST /api/text-to-speech
```

## Clusters & Intelligence

```http
GET /api/clusters?state=&district=&category=
GET /api/clusters/:id
GET /api/hotspots?state=&category=&from=&to=
```

## Recommendations

```http
POST /api/recommendations/score        (weights in body)
GET  /api/recommendations?scope=&id=
POST /api/recommendations/:id/brief
```

## State / Analytics

```http
GET /api/states
GET /api/states/:id/analytics
GET /api/districts/:id/indicators
```

---

# 38. Functional Requirements

## FR-01: Request Submission

The system must allow a citizen or demo citizen to submit a request.

### Acceptance Criteria

- Request can be submitted by text on the web.
- Request can be submitted by voice on the web.
- Request can be submitted through the messaging bot.
- A request ID is returned.

---

## FR-02: Speech & Translation

### Acceptance Criteria

- Voice is transcribed in at least Hindi and Telugu.
- Text is translated to English, and the original is kept.
- Confirmation is returned in the citizen's language.

---

## FR-03: AI Request Understanding

### Acceptance Criteria

- Gemini returns schema-valid JSON.
- Category comes from the fixed taxonomy.
- Confidence and missing information are included.
- Low-confidence results trigger a clarification question.

---

## FR-04: Location Resolution

### Acceptance Criteria

- Request is mapped to an LGD code and an H3 cell.
- The resolution method and confidence are stored.
- Ambiguous locations trigger clarification.

---

## FR-05: Demand Clustering

### Acceptance Criteria

- Similar requests in the same category and area are grouped.
- Cluster shows request count and unique citizens.
- A new request joins an existing cluster when appropriate.

---

## FR-06: Data Fusion

### Acceptance Criteria

At least three data dimensions are joined to each cluster:

- Demographics
- Infrastructure gap
- Investment

---

## FR-07: Priority Score

### Acceptance Criteria

- Score is displayed with a factor breakdown.
- Weights are configurable.
- Changing the weights re-ranks recommendations.

---

## FR-08: Evidence Brief

### Acceptance Criteria

- Brief is generated for a selected recommendation.
- Every number in the brief exists in the input data.
- Sources are displayed.
- Uncertainties are displayed.

---

## FR-09: Planning Officer Dashboard

### Acceptance Criteria

Officer can view:

- National / state / district overview
- Hotspot map
- Category filters
- Ranked recommendations
- Evidence briefs

---

## FR-10: Interoperability

### Acceptance Criteria

The prototype demonstrates:

- Canonical civic demand schema.
- At least two state configurations.
- State-specific data mapped into the common model.
- Shared APIs / AI services operating on the common model.

---

## FR-11: Citizen Status Update (Secondary)

### Acceptance Criteria

- When a cluster changes status, linked citizens can see the new status.

---

# 39. Non-Functional Requirements

## Performance

- Fast initial application load
- Standard API response under about 2 seconds where practical
- Voice note → confirmation in about 15 seconds where practical
- Clear loading states for AI operations

## Scalability

The system should support:

- Multiple states
- Multiple languages
- Millions of requests (BigQuery)
- Horizontal Cloud Run scaling

## Reliability

- Queue incoming requests so they aren't lost if AI services are slow.
- Degrade gracefully if translation or speech services fail (fall back to text).
- A failure in one external source shouldn't block the dashboard.

## Accessibility

- Mobile-first
- Voice-capable
- Regional-language capable
- Designed for low literacy

## Security

- HTTPS
- Protect API secrets
- Authenticated officer APIs
- Role-based access
- Hash phone numbers
- Least-privilege cloud permissions

---

# 40. State Onboarding Architecture

A new state can be onboarded without rewriting the core application.

## Onboarding Flow

```text
Register State
      ↓
Configure Languages
      ↓
Load LGD Codes
      ↓
Register Data Sources (indicators, investments)
      ↓
Map Local Fields to Canonical Schema
      ↓
Validate Data
      ↓
Configure Category ↔ Scheme Mapping
      ↓
Enable Channels
      ↓
State Becomes Available
```

## Example

```text
State: Andhra Pradesh

Local Indicator & Investment Data
     ↓
AP Adapter
     ↓
Canonical Schema
     ↓
Shared AI Services
```

---

# 41. Repository Structure

```text
civic-demand-network/
│
├── apps/
│   ├── citizen-web/
│   └── officer-dashboard/
│
├── services/
│   ├── api/
│   ├── intake/
│   ├── messaging-bot/
│   ├── understanding/
│   ├── location/
│   ├── clustering-scoring/
│   ├── evidence-brief/
│   └── localization/
│
├── ai/
│   ├── prompts/
│   ├── schemas/
│   ├── taxonomy/
│   └── evaluation/
│
├── data/
│   ├── schemas/
│   ├── adapters/
│   ├── sample/
│   └── transformations/
│
├── infrastructure/
│   ├── cloud-run/
│   ├── bigquery/
│   └── firebase/
│
├── docs/
│
└── README.md
```

---

# 42. MVP Data Strategy

Prioritise **real or realistic** data over complicated ingestion.

## Use real / public data where feasible

- LGD codes
- Census population
- Selected infrastructure indicators
- Aspirational district list

## Use realistic sample data where needed

- **Citizen requests**: generate a multilingual sample set (a few thousand requests) with Gemini from realistic templates, **clearly labelled as synthetic**, plus a small set of real voice recordings from the team.
- **Investment data**: sample sanctioned-project lists, clearly labelled.

## Data Source Metadata

Every dataset retains:

- Source
- Reference year / timestamp
- Dataset version
- Geographic level
- "Sample / synthetic" flag where applicable

---

# 43. Recommended MVP Demo Scenarios

## Scenario A

```text
State: Bihar
District: Gaya
Language: Hindi (voice)
Need: Bridge / rural road
```

## Scenario B

```text
State: Andhra Pradesh
District: Anantapur
Language: Telugu (messaging bot)
Need: Drinking water
```

## Scenario C

```text
State: Maharashtra
City: Pune (urban ward)
Language: English (web)
Need: Public transport
```

The number of demo states doesn't matter much. The point is to prove that one platform structure supports different state, language and category combinations.

---

# 44. Hackathon Demo Flow

The demo should be one continuous story rather than a collection of disconnected features.

## 0:00–0:30: Introduce the Citizen

> Meet a parent in a village in Gaya whose children can't reach school every monsoon.

## 0:30–1:10: Voice Request

Show:

- Hindi voice request
- Transcription and translation
- AI-extracted category, location and urgency
- Spoken confirmation in Hindi

## 1:10–1:50: Demand Cluster

Show:

- Request joining an existing cluster
- Cluster size and representative quotes

## 1:50–2:30: Data Fusion & Priority Score

Show:

- Demographic, infrastructure-gap and investment data
- Priority Score breakdown
- Weight adjustment changing the ranking

## 2:30–3:10: Evidence Brief

Generate a Gemini evidence brief with cited sources and uncertainties.

## 3:10–3:40: Hotspot Map

Open the Planning Officer dashboard: national → state → district hotspots.

## 3:40–4:20: Interoperability

Switch to Andhra Pradesh (Telugu, drinking water) and show the common data structure.

## 4:20–5:00: Scale & Deployment

```text
One Request
   ↓
One Village
   ↓
One District
   ↓
One State
   ↓
Multiple States
   ↓
National Citizen Demand Intelligence Network
```

Show the Google AI / Cloud stack powering the solution.

---

# 45. Deployment Architecture

```text
                         Internet
                            │
                            ▼
                    Google Cloud Platform
                            │
                         Cloud Run
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
     Next.js App       API Layer         AI Services
          │                 │                 │
          │          Messaging Webhook        │
          ▼                 ▼                 ▼
       Firebase         BigQuery          Vertex AI
                                              │
                                              ▼
                                           Gemini
                            │
                            ▼
                      External Data
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
    data.gov.in /       LGD / Census       State Data
    Mission Antyodaya
```

Primary region: `asia-south1` (Mumbai).

---

# 46. Environment & Secrets

Secrets must never be committed to GitHub.

Example configuration:

```text
GEMINI_API_KEY
GOOGLE_CLOUD_PROJECT
GOOGLE_APPLICATION_CREDENTIALS
BIGQUERY_DATASET
FIREBASE_PROJECT_ID
MAPS_API_KEY
TELEGRAM_BOT_TOKEN
WHATSAPP_TOKEN (future)
```

Store them in Secret Manager for Cloud Run.

---

# 47. Observability

The system should log:

- API latency
- AI request latency
- AI failures and schema-validation failures
- Speech / translation failures
- Location-resolution failures
- Dataset freshness
- Model and prompt version
- Clustering job runs
- Evidence brief generation events

Future production metrics:

- Requests per channel and language
- Clarification rate
- Recommendation adoption
- Citizen satisfaction

---

# 48. AI Evaluation

A basic internal evaluation layer should test:

## Request Understanding

- Category accuracy on a labelled sample (internal target: at least 85%)
- Hallucinated locations or numbers

## Location Resolution

- Correct LGD match on a labelled sample, including ambiguous names

## Clustering

- Manual audit of cluster purity

## Evidence Briefs

- Every number is present in the input data (automated check)
- Source citation present

## Multilingual

- Transcription quality per language
- Terminology preservation in translation

The hackathon MVP doesn't need a formal scientific evaluation system, but the architecture should make evaluation possible.

---

# 49. Success Metrics

## 49.1 Hackathon Success

The prototype should demonstrate:

- Complete end-to-end citizen → policymaker flow
- Meaningful Google AI integration
- Voice, text and messaging intake
- At least three languages
- At least three public data dimensions
- Demand clustering
- Explainable Priority Score
- Grounded evidence brief
- Planning Officer dashboard
- Multiple state configurations
- Common data / API structure
- Public deployment
- Public or access-granted GitHub repository

## 49.2 Long-Term Impact Metrics

### Citizen Impact

- Citizens reached
- Requests captured
- Languages supported
- Citizens receiving status updates

### Governance Impact

- Recommendations adopted into district or state plans
- Share of spending aligned with measured demand
- Reduction in unaddressed high-priority gaps

### Platform Impact

- States integrated
- Districts covered
- Datasets onboarded
- API consumers

---

# 50. Scalability Strategy

## Phase 1: Hackathon

```text
2–3 state configurations
3 languages
3 channels
Real + realistic datasets
```

## Phase 2: District Pilot

```text
1 aspirational district
WhatsApp Business number
Assisted capture via Common Service Centres
Weekly review with the district planning officer
```

## Phase 3: State Deployment

```text
State-level project
Integration with state grievance / request systems
More languages
IVR for feature phones
```

## Phase 4: National Network

```text
Multiple states
Shared data contracts
De-identified national data exchange (BigQuery Analytics Hub)
National policymaker view
Open data APIs
```

---

# 51. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| No real citizen data during the hackathon | Clearly labelled synthetic requests plus real team recordings |
| Poor speech accuracy on dialects | Read back a summary for confirmation, let the citizen correct by text, log errors per language |
| Ambiguous village names | Restrict the search to the state and district, ask a clarification question, use a location pin |
| AI invents numbers in briefs | Structured input only plus an automated number-grounding check |
| Manipulation / repeated submissions | Deduplicate per citizen hash, rate limits, count unique citizens |
| Bias toward connected areas | Per-capita normalisation, assisted capture on the roadmap |
| Messaging API approval delays | Telegram bot for the demo, with WhatsApp as the production target |
| State data incompatibility | Canonical schema + state adapters |
| High AI cost | Cache extractions, batch clustering, generate briefs on demand only |
| Vendor coupling | Abstract AI and messaging providers behind internal service interfaces |

---

# 52. Security & Privacy

## Citizen Data

Collect only what the product needs. Record consent at first contact, in line with the DPDP Act 2023.

## Phone Numbers

Store only hashes in analytics. Keep raw numbers only where needed to send status updates, with restricted access.

## Voice & Photos

Store securely with retention limits.

## Access Control

The MVP supports two roles:

```text
Citizen
Planning Officer (scoped: district / state / national)
```

Role permissions should ensure:

- Citizens see only their own requests.
- Officers see only aggregated, de-identified data for their authorised geography.

---

# 53. Future Roadmap

## Citizen Channels

- WhatsApp Business at scale
- IVR / missed-call for feature phones
- Assisted capture via CSCs, ASHAs and Panchayat secretaries

## Intelligence

- Demand forecasting
- Photo evidence verification
- Rigorous impact evaluation (difference-in-differences)
- Anomaly / brigading detection

## Government Integration

- CPGRAMS and state grievance adapters
- District planning tools
- National de-identified data exchange

## Ecosystem

- Open civic demand APIs
- Research datasets
- DPG registry listing

---

# 54. Google AI Integration Map

| Google Technology | Product Role |
|---|---|
| Gemini API | Request extraction, clarification, cluster summaries, evidence briefs |
| Vertex AI Embeddings | Semantic clustering of requests |
| Vertex AI / BigQuery ML | Demand forecasting (future), model serving |
| Google AI Studio | Prompt experimentation and evaluation |
| Cloud Speech-to-Text | Citizen voice input |
| Text-to-Speech | Spoken confirmations |
| Translation API | Multilingual support |
| BigQuery | Requests, indicators, vector search, analytics |
| Firebase | Authentication and request status |
| Cloud Run | Backend, bot and AI services |
| Google Maps Platform | Location capture, geocoding, hotspot maps |

---

# 55. Alignment with Hackathon Evaluation

## Problem-Solution Fit: 20%

The product directly addresses:

- Fragmented citizen requests
- Multilingual access
- Misaligned public spending
- Unaddressed infrastructure gaps
- Measuring impact

## AI / Technical Execution: 25%

The prototype shows meaningful roles for:

- Speech-to-Text and Translation
- Gemini structured extraction
- Vertex AI embeddings clustering
- Gemini grounded evidence briefs
- A deterministic, explainable scoring pipeline

## Depth & Reach Across India: 20%

The architecture shows:

- A state-independent data model
- Multi-state configuration
- Multi-language support
- Several channels
- Reusable APIs

## Impact Potential: 15%

The solution can reach every Gram Panchayat and urban ward. It aligns infrastructure spending with measured citizen demand.

## Deployability & Scalability: 20%

The prototype shows:

- Cloud-native services
- API-first architecture
- State adapters
- Standardised schemas
- A deployable application
- A clear district pilot path

---

# 56. Definition of Done: Hackathon MVP

## Citizen Experience

- [ ] Citizen can submit a request by text.
- [ ] Citizen can submit a request by voice.
- [ ] Citizen can submit a request through the messaging bot.
- [ ] Citizen receives a confirmation in their language.
- [ ] Citizen can correct or confirm the AI's understanding.

## AI Experience

- [ ] Gemini extracts structured request data.
- [ ] Location resolves to an LGD code.
- [ ] Requests cluster into demand clusters.
- [ ] Priority Score is displayed with a breakdown.
- [ ] Gemini generates a grounded evidence brief.
- [ ] Confidence / uncertainty is displayed.

## Language & Voice

- [ ] English supported.
- [ ] Hindi supported.
- [ ] Telugu supported.
- [ ] At least one complete voice interaction works.

## Planning Officer

- [ ] Officer dashboard exists.
- [ ] Hotspot map is visible.
- [ ] Ranked recommendations are visible.
- [ ] Weights can be adjusted.
- [ ] Data sources and freshness are visible.

## Interoperability

- [ ] Canonical schema is documented.
- [ ] At least two state configurations exist.
- [ ] State-specific data maps to the common schema.
- [ ] Shared AI / API services operate on the common structure.

## Deployment & Submission

- [ ] Prototype is publicly deployed.
- [ ] Source code is available through GitHub.
- [ ] README contains setup and architecture documentation.
- [ ] Demo data is available and labelled.
- [ ] 3–5 minute demo video is prepared.
- [ ] 10–12 slide pitch deck is prepared.
- [ ] 2–3 line product description is prepared.

---

# 57. Recommended Build Priority

Prioritise **one polished end-to-end journey over many disconnected features**.

## Priority 1: Core Experience

```text
Request (text/voice)
 ↓
Gemini Extraction
 ↓
Location Resolution
 ↓
Clustering
 ↓
Data Fusion + Priority Score
 ↓
Evidence Brief
```

## Priority 2: Accessibility

```text
Multilingual
 ↓
Voice confirmation
 ↓
Messaging bot
```

## Priority 3: Scale Story

```text
Planning Officer Dashboard
 ↓
Multi-state configurations
 ↓
Interoperability layer
```

## Priority 4: Future / Optional

```text
Impact view
Citizen status updates
Demand forecasting
IVR
```

Don't sacrifice the core citizen-to-policymaker journey to add lower-priority features.

---

# 58. Final Product Definition

The solution is an **AI-powered interoperable civic demand intelligence network** for India.

At the citizen level:

```text
            CITIZEN
               │
               ▼
     VOICE / TEXT / MESSAGE
               │
               ▼
        AI UNDERSTANDING
     Gemini + Speech + Translation
               │
               ▼
      LOCATION + CLUSTER
               │
               ▼
   Confirmation in Citizen's Language
```

At the policy level:

```text
   CITIZEN DEMAND   DEMOGRAPHICS   INFRASTRUCTURE GAP   INVESTMENT
         │               │                 │                │
         └───────────────┴────────┬────────┴────────────────┘
                                  ▼
                       EXPLAINABLE PRIORITY SCORE
                                  │
                                  ▼
                        GEMINI EVIDENCE BRIEF
                                  │
                                  ▼
                      POLICYMAKER RECOMMENDATION
```

At the infrastructure level:

```text
      NATIONAL CIVIC DEMAND NETWORK
                    │
           COMMON DATA MODEL
                    │
       ┌────────────┼────────────┐
       │            │            │
     Bihar   Andhra Pradesh  Maharashtra
       │            │            │
   Local Data   Local Data   Local Data
       │            │            │
       └────────────┼────────────┘
                    │
            Shared AI Services
                    │
              Shared APIs
```

The platform combines:

**Citizen voice + AI understanding + public data fusion + explainable prioritisation + multilingual accessibility + interoperable digital infrastructure**

in one scalable architecture.

The hackathon MVP should prove that the solution can move from:

> **One citizen → One village → One district → One state → Multiple Indian states**
