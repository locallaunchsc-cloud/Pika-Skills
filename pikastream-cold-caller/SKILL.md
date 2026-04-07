# pikastream-cold-caller

> **Skill Type:** Autonomous Outbound Voice Agent
> **Version:** 1.0.0
> **Author:** Local Launch SC
> **Target:** Local SMBs — brick-and-mortar businesses, service providers, trades
> **Status:** Production-Ready

---

## Overview

`pikastream-cold-caller` turns Pika into a fully autonomous outbound sales rep for Local Launch. It dials leads from a list, runs a real conversation using a configurable script, qualifies prospects, handles objections, books appointments, and exports structured results — all without a human on the line.

This is not a call transcript tool. This is not an analytics layer. Pika **is** the caller.

---

## How It Works

```
[Lead List Input]
       ↓
[Campaign Config — niche, opener, offer, rubric]
       ↓
[Pika Dials Lead — AI Voice, no human needed]
       ↓
[Live Conversation — opener → discovery → objection handling → close]
       ↓
[Post-Call Scoring — qualification rubric applied automatically]
       ↓
[Output — appointment booked | CRM row | follow-up queued]
```

---

## Inputs

### 1. Lead List (`leads.json`)

```json
[
  {
    "id": "lead_001",
    "business_name": "Sunrise Plumbing",
    "owner_name": "Marcus",
    "phone": "+18038880001",
    "niche": "plumbing",
    "city": "Columbia",
    "state": "SC",
    "notes": "No website found, Google listing only"
  }
]
```

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | Unique lead identifier |
| `business_name` | string | yes | Name of the business |
| `owner_name` | string | no | Owner first name for personalization |
| `phone` | string | yes | E.164 formatted phone number |
| `niche`` | string | yes | Business category (plumbing, roofing, salon, etc.) |
| `city` | string | yes | City for local relevance |
| `state` | string | yes | State abbreviation |
| `notes` | string | no | Pre-call research notes |

---

### 2. Campaign Config (`campaign.json`)

```json
{
  "campaign_id": "local-launch-apr-2026",
  "agent_name": "Jordan",
  "company_name": "Local Launch",
  "offer": "AI-powered website + Google rankings for local businesses",
  "goal": "book_appointment",
  "appointment_link": "https://cal.com/locallaunch/discovery",
  "max_call_duration_seconds": 180,
  "retry_attempts": 2,
  "retry_delay_hours": 24,
  "voice_id": "professional_us_male_01",
  "niche_openers": {
    "plumbing": "Hey {owner_name}, this is Jordan with Local Launch — we help plumbing companies in {city} get more calls from Google without paying for ads.",
    "roofing": "Hey {owner_name}, Jordan here from Local Launch — we're helping roofing contractors in {city} show up on Google before storm season.",
    "salon": "Hey {owner_name}, this is Jordan from Local Launch — we help salons in {city} get fully booked using their Google listing.",
    "default": "Hey {owner_name}, this is Jordan from Local Launch — we help local businesses in {city} get more customers from Google, completely done-for-you."
  }
}
```

---

## Conversation Flow

### Stage 1 — Opener
- Pika introduces itself as a human rep named after `agent_name`
- Uses niche-specific opener from config
- Tone: warm, local, not salesy
- If no answer → voicemail drop (pre-recorded message) → log as `voicemail`

### Stage 2 — Pattern Interrupt / Permission
- "Did I catch you at a bad time?"
- If no → proceed to Stage 3
- If yes → "Totally get it — when's a better time to reach you?" → schedule callback → log as `callback_requested`

### Stage 3 — Discovery (3 Questions Max)

| # | Question | Purpose |
|---|---|---|
| 1 | "How are you currently getting new customers?" | Identify gap |
| 2 | "Are you showing up on Google when people search for [niche] in [city]?" | Pain dial |
| 3 | "If I could show you exactly how we'd fix that in 30 minutes, would you be open to a quick call?" | Soft close |

### Stage 4 — Objection Handling

| Objection | Response |
|---|---|
| "I'm not interested" | "Totally fair — can I ask what's working best for you right now to get customers?" |
| "I already have a website" | "That's great — our clients usually have one too, the issue is it's not showing up when people search. Is that the case for you?" |
| "How much does it cost?" | "Depends on the scope — that's exactly what we'd cover on the call so you're not guessing. Takes 20 minutes." |
| "I'm busy" | "Respect that completely — I can send you a link and you pick the time. Would that work?" |
| "Send me an email" | "For sure — I'll send it right after. But real quick, are you at least open to seeing results from businesses like yours in [city]?" |

### Stage 5 — Close / Booking
- If qualified: "Awesome, let me send you a link right now — you just pick a time that works." → SMS/email appointment link
- If not qualified: Log reason, add to nurture queue
- Confirm booking verbally on call before hanging up

---

## Lead Qualification Rubric

Applied automatically after each call. Scores 0–100.

```json
{
  "rubric_id": "local-launch-lead-v1",
  "dimensions": [
    {
      "name": "Engagement Quality",
      "weight": 25,
      "signals": [
        "Stayed on call past opener",
        "Asked questions back",
        "Tone was warm or curious"
      ]
    },
    {
      "name": "Pain Confirmation",
      "weight": 30,
      "signals": [
        "Admitted low Google visibility",
        "Mentioned struggling to get new customers",
        "No current digital marketing strategy"
      ]
    },
    {
      "name": "Budget Signal",
      "weight": 20,
      "signals": [
        "Business has been operating 1+ years",
        "Mentioned spending on ads or marketing before",
        "Did not immediately cite cost as blocker"
      ]
    },
    {
      "name": "Decision Authority",
      "weight": 15,
      "signals": [
        "Owner or decision maker confirmed on call",
        "Did not defer to a partner or accountant"
      ]
    },
    {
      "name": "Appointment Readiness",
      "weight": 10,
      "signals": [
        "Agreed to see the calendar link",
        "Asked about timing or next steps",
        "Confirmed a time slot on the call"
      ]
    }
  ],
  "thresholds": {
    "hot": 75,
    "warm": 50,
    "cold": 25,
    "disqualified": 0
  }
}
```

---

## Outputs

### Per-Call Record (`call_result.json`)

```json
{
  "lead_id": "lead_001",
  "campaign_id": "local-launch-apr-2026",
  "timestamp": "2026-04-03T14:32:00Z",
  "duration_seconds": 97,
  "outcome": "appointment_booked",
  "qualification_score": 82,
  "qualification_tier": "hot",
  "appointment_time": "2026-04-05T10:00:00Z",
  "objections_raised": ["cost"],
  "objections_handled": ["cost"],
  "transcript_url": "https://storage.pika.ai/calls/lead_001_transcript.txt",
  "recording_url": "https://storage.pika.ai/calls/lead_001_recording.mp3",
  "follow_up_action": "none",
  "notes": "Owner Marcus was engaged, confirmed no Google presence, booked discovery call."
}
```

### Outcome Types

| Outcome | Description |
|---|---|
| `appointment_booked` | Lead agreed and booked a time slot |
| `callback_requested` | Lead asked to be called back at a specific time |
| `follow_up_queued` | Warm lead, not ready now — added to nurture sequence |
| `voicemail` | No answer — voicemail drop delivered |
| `not_interested` | Hard no — removed from active pipeline |
| `disqualified` | Wrong number, out of business, or not a fit |
| `no_answer` | No answer, no voicemail left (retry scheduled) |

---

### Campaign Summary Report (`campaign_report.json`)

```json
{
  "campaign_id": "local-launch-apr-2026",
  "run_date": "2026-04-03",
  "total_leads": 100,
  "calls_completed": 93,
  "appointments_booked": 11,
  "hot_leads": 18,
  "warm_leads": 24,
  "cold_leads": 31,
  "disqualified": 9,
  "voicemails": 14,
  "no_answer": 7,
  "booking_rate_pct": 11.8,
  "avg_call_duration_seconds": 84,
  "top_objections": ["cost", "already_has_website", "busy"],
  "top_niches_by_booking": ["plumbing", "roofing", "landscaping"]
}
```

---

## Skill Execution

### CLI

```bash
# Run full campaign
pika run pikastream-cold-caller \
  --leads leads.json \
  --config campaign.json \
  --output ./results

# Single test call
pika run pikastream-cold-caller \
  --leads leads.json \
  --config campaign.json \
  --lead-id lead_001 \
  --dry-run

# Export campaign report
pika export pikastream-cold-caller \
  --campaign local-launch-apr-2026 \
  --format csv \
  --output ./exports
```

### Batch Mode

```bash
# Run 50 calls in parallel with 5 concurrent agents
pika run pikastream-cold-caller \
  --leads leads.json \
  --config campaign.json \
  --concurrency 5 \
  --limit 50
```

---

## Integrations

| Platform | Action | Trigger |
|---|---|---|
| **Airtable** | Create/update lead row with outcome + score | After every call |
| **Google Calendar** | Auto-create appointment block | On `appointment_booked` |
| **Twilio** | Outbound dial + SMS for calendar link | Runtime |
| **ElevenLabs** | AI voice synthesis for agent persona | Runtime |
| **Beehiiv** | Add `follow_up_queued` leads to nurture sequence | After call |
| **Slack / Discord** | Push hot lead alerts in real time | On score ≥ 75 |

---

## Local Launch Use Case — Quick Start

```bash
# 1. Export leads from Apollo / Google Maps scraper
# 2. Format as leads.json per schema above
# 3. Configure your campaign
cp examples/campaign.local-launch.json campaign.json

# 4. Fire the campaign
pika run pikastream-cold-caller --leads leads.json --config campaign.json

# 5. Check results in real time
pika status pikastream-cold-caller --campaign local-launch-apr-2026

# 6. Export booked appointments
pika export pikastream-cold-caller \
  --campaign local-launch-apr-2026 \
  --filter outcome=appointment_booked \
  --format csv
```

---

## Why This Skill Exists

Local businesses are invisible online and no one is calling them. Human SDRs are expensive, inconsistent, and don't work at 2am.

`pikastream-cold-caller` gives Local Launch a 24/7 outbound engine that:
- Calls 100 leads while you sleep
- Sounds human, stays on script, never has a bad day
- Books appointments directly into your calendar
- Exports clean CRM data after every campaign

This is Pika working as a **revenue teammate**, not a reporting tool.

---

## Related Skills

- [`pikastream-screening-interview`](../pikastream-screening-interview) — AI interviews candidates and exports scorecards
- [`pikastream-video-meeting`](../pikastream-video-meeting) — AI joins and summarizes video meetings

---

## License

Apache 2.0 — See [LICENSE](../LICENSE)
