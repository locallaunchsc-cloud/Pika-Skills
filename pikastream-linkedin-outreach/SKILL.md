# pikastream-linkedin-outreach

> **Skill Type:** Async Video Outreach Agent
> **Version:** 1.0.0
> **Author:** Local Launch SC
> **Target:** Agencies, founders, consultants, sales teams doing LinkedIn prospecting
> **Status:** Production-Ready

---

## Overview

`pikastream-linkedin-outreach` turns Pika into a personalized async video outreach engine for LinkedIn. It takes prospect data, generates a custom talking-head video message using your cloned voice and AI avatar, writes companion DM copy, and exports everything ready to send — all without recording a single video yourself.

This is not a LinkedIn automation bot. This is not a message template tool. Pika **is** the salesperson on camera.

---

## How It Works

```
[Prospect Data Input]
        |
[Campaign Config — voice, avatar, offer, CTA]
        |
[Script Generation — personalized per prospect]
        |
[Pika Renders Video — AI avatar + cloned voice]
        |
[DM Copy Generated — paired with video]
        |
[Output — video file + DM text ready to send]
```

---

## Inputs

### 1. Prospect List (`prospects.json`)

```json
[
  {
    "id": "prospect_001",
    "name": "Sarah Chen",
    "company": "Meridian Digital",
    "role": "Head of Growth",
    "linkedin_url": "https://linkedin.com/in/sarachen",
    "angle": "cold_intro",
    "notes": "Posted about scaling outbound last week. Company raised Series A in Jan.",
    "cta": "book_call"
  }
]
```

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | Unique prospect identifier |
| `name` | string | yes | Prospect full name |
| `company` | string | yes | Company name |
| `role` | string | no | Job title for personalization |
| `linkedin_url` | string | no | LinkedIn profile URL |
| `angle` | string | yes | Outreach type: `cold_intro`, `warm_follow_up`, `post_connection`, `event_follow_up` |
| `notes` | string | no | Research notes for personalization |
| `cta` | string | yes | Desired action: `book_call`, `visit_link`, `reply`, `watch_demo` |

---

### 2. Campaign Config (`campaign.json`)

```json
{
  "campaign_id": "linkedin-outreach-apr-2026",
  "sender_name": "Jay",
  "company_name": "Local Launch",
  "offer": "AI-powered outbound systems for agencies and founders",
  "appointment_link": "https://cal.com/locallaunch/discovery",
  "voice_id": "cloned_jay_v1",
  "avatar_image": "identity/videomeeting-avatar.png",
  "video_duration_seconds": 45,
  "video_resolution": "1080p",
  "video_aspect_ratio": "9:16",
  "tone": "warm, direct, founder-to-founder",
  "angle_templates": {
    "cold_intro": "Hey {name}, saw what you're building at {company} — {personalization_hook}. I help {role_type}s like you {value_prop}. {cta_line}",
    "warm_follow_up": "Hey {name}, we connected a few days ago and I wanted to put a face to the name. {personalization_hook}. {cta_line}",
    "post_connection": "Hey {name}, appreciate you connecting — wanted to send a quick intro instead of the usual wall of text. {personalization_hook}. {cta_line}",
    "event_follow_up": "Hey {name}, great meeting you at {event}. {personalization_hook}. {cta_line}"
  },
  "cta_lines": {
    "book_call": "If you're open to it, I'd love 15 minutes to show you how this works — link's in my profile.",
    "visit_link": "I put together a quick breakdown — dropping the link in the DM below.",
    "reply": "Would love to hear your take — just reply here if it resonates.",
    "watch_demo": "Recorded a 2-min demo showing exactly how it works — link below."
  }
}
```

---

## Video Generation Flow

### Stage 1 — Script Generation

For each prospect, Pika generates a personalized 30-60 second script:

| Rule | Detail |
|---|---|
| Length | 75-150 words (30-60 sec spoken) |
| Opening | Use their first name + specific hook from notes |
| Body | One clear value proposition sentence |
| Close | CTA from config — low friction, no pressure |
| Tone | Conversational, human, NOT salesy or robotic |
| Personalization | Must reference at least one detail from `notes` field |

Script is saved to `/tmp/outreach_scripts/{prospect_id}_script.txt`

### Stage 2 — Avatar Video Rendering

Pika renders a talking-head video using:
- **Avatar image** from `campaign.avatar_image`
- **Cloned voice** from `campaign.voice_id`
- **Script** from Stage 1
- **Duration** capped at `campaign.video_duration_seconds`
- **Format** 9:16 vertical (optimized for LinkedIn mobile)

### Stage 3 — DM Copy Generation

Pika generates a short companion DM to pair with the video:

| Rule | Detail |
|---|---|
| Length | 2-4 sentences max |
| Format | Plain text, no links in body (link goes in PS or separate message) |
| Tone | Match video tone — casual, direct |
| Must include | Reference to the attached video |
| Must NOT include | Generic "I'd love to pick your brain" or "hope this finds you well" |

DM saved to `/tmp/outreach_dms/{prospect_id}_dm.txt`

---

## Outputs

### Per-Prospect Record (`outreach_result.json`)

```json
{
  "prospect_id": "prospect_001",
  "campaign_id": "linkedin-outreach-apr-2026",
  "timestamp": "2026-04-03T15:20:00Z",
  "video_path": "outreach_videos/prospect_001_sarah-chen.mp4",
  "video_duration_seconds": 38,
  "video_size_mb": 4.2,
  "script_text": "Hey Sarah, saw your post about scaling outbound at Meridian...",
  "dm_text": "Hey Sarah — made you a quick video intro instead of the usual text wall. Take a look when you get a sec.",
  "angle": "cold_intro",
  "cta": "book_call",
  "status": "ready_to_send"
}
```

### Status Types

| Status | Description |
|---|---|
| `ready_to_send` | Video rendered + DM generated, ready for manual send |
| `script_review` | Script generated, awaiting user approval before rendering |
| `rendering` | Video currently being generated |
| `failed` | Generation failed — see error field |
| `sent` | User marked as sent (manual tracking) |

---

### Campaign Summary Report (`campaign_report.json`)

```json
{
  "campaign_id": "linkedin-outreach-apr-2026",
  "run_date": "2026-04-03",
  "total_prospects": 25,
  "videos_generated": 23,
  "videos_failed": 2,
  "avg_video_duration_seconds": 41,
  "total_render_time_minutes": 18,
  "total_credits_used": 230,
  "angles_breakdown": {
    "cold_intro": 15,
    "warm_follow_up": 5,
    "post_connection": 3
  },
  "ready_to_send": 23,
  "estimated_response_rate": "15-25% (industry avg for personalized video)"
}
```

---

## Skill Execution

### CLI

```bash
# Generate video + DM for a single prospect
pika run pikastream-linkedin-outreach \\
  --prospects prospects.json \\
  --config campaign.json \\
  --prospect-id prospect_001 \\
  --output ./outreach_videos

# Generate for all prospects in batch
pika run pikastream-linkedin-outreach \\
  --prospects prospects.json \\
  --config campaign.json \\
  --output ./outreach_videos

# Script-only mode (no video render — review scripts first)
pika run pikastream-linkedin-outreach \\
  --prospects prospects.json \\
  --config campaign.json \\
  --script-only \\
  --output ./outreach_scripts

# Regenerate video for a specific prospect with edited script
pika run pikastream-linkedin-outreach \\
  --prospect-id prospect_001 \\
  --script-file ./outreach_scripts/prospect_001_script.txt \\
  --config campaign.json \\
  --output ./outreach_videos
```

### Batch Mode

```bash
# Render 25 prospect videos with 3 concurrent renders
pika run pikastream-linkedin-outreach \\
  --prospects prospects.json \\
  --config campaign.json \\
  --concurrency 3 \\
  --output ./outreach_videos
```

---

## Integrations

| Platform | Action | Trigger |
|---|---|---|
| **Airtable** | Create/update prospect row with video URL + DM copy | After each render |
| **Google Drive** | Auto-upload rendered videos to shared folder | After each render |
| **Notion** | Log outreach activity to campaign tracker | After each render |
| **Clay** | Pull enriched prospect data as input | Pre-campaign |
| **Apollo** | Import prospect lists directly | Pre-campaign |
| **Slack / Discord** | Push notification when batch is complete | After batch |
| **Zapier / Make** | Trigger downstream workflows on `ready_to_send` | After each render |

---

## Outreach Best Practices

### Video Format
- **9:16 vertical** — LinkedIn mobile-first
- **30-45 seconds** — short enough to watch, long enough to convey value
- **Eye contact with camera** — avatar looks directly at viewer
- **Clean background** — professional but not corporate

### Script Rules
- Lead with their name + something specific to them
- Never open with "I hope this message finds you well"
- State what you do in ONE sentence
- End with ONE clear ask — not three
- Sound like a human voice memo, not a sales pitch

### DM Pairing Strategy
- Send DM with video attachment first
- Follow up 48 hours later with text-only nudge if no response
- Never send more than 2 follow-ups per prospect
- Track responses manually and mark status as `sent`

---

## Why This Skill Exists

LinkedIn outreach is broken. Everyone sends the same templated text walls. Connection requests with "I'd love to pick your brain" get ignored.

Personalized video cuts through because almost nobody does it — and nobody does it at scale because recording 25 custom videos takes hours.

`pikastream-linkedin-outreach` gives you a 24/7 video outreach engine that:
- Generates personalized talking-head videos for every prospect
- Uses your face and your voice — not generic AI
- Writes companion DMs that sound human
- Scales from 1 video to 100 in a single batch
- Exports everything ready to send

This is Pika working as a **revenue engine**, not a content tool.

---

## Related Skills

- [`pikastream-cold-caller`](../pikastream-cold-caller) — AI dials leads and books appointments autonomously
- [`pikastream-screening-interview`](../pikastream-screening-interview) — AI interviews candidates and exports scorecards
- [`pikastream-video-meeting`](../pikastream-video-meeting) — AI joins and participates in video meetings

---

## License

Apache 2.0 — See [LICENSE](../LICENSE)
