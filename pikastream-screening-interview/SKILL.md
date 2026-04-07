| | |
|---|---|
| name | pikastream-screening-interview |
| description | Run structured first-round screening interviews at scale via PikaStreaming. Trigger: user provides a candidate list, rubric, and Google Meet or Zoom links, or says "screen these candidates." |
| metadata | ---  openclaw   ---  requires  primaryEnv   ---  env  bins   PIKA_DEV_KEY  python3  PIKA_DEV_KEY |

# PikaStream Screening Interview

Script: `SKILL_DIR=skills/pikastream-screening-interview`

## First-Time Setup

Run once when the skill is first loaded:

```
pip install -r $SKILL_DIR/requirements.txt
```

### 1. Avatar

Check if `identity/videomeeting-avatar.png` exists and is larger than 1 KB. If it does NOT exist (or is too small):

- 1. Ask the user: `I need an avatar image for the interviewer bot (a headshot or portrait). Send me an image, or say "generate" and I'll create one for you.`
- 2. **Do not proceed until the user responds.** Do not auto-generate.
- 3. **User sends an image:** save it to `identity/videomeeting-avatar.png`.
- 4. **User says "generate":** run:
  ```
  python $SKILL_DIR/scripts/pikastreaming_screening_interview.py generate-avatar \
    --output identity/videomeeting-avatar.png
  ```
  If the user describes what they want (e.g. "a professional recruiter"), pass `--prompt "<description>, portrait headshot suitable for video calls"`. Show the generated image. Ask: `Want to keep this avatar or regenerate?` Wait for reply.
- 5. **Anything else:** repeat the question from step 1.

The bot must have an avatar before joining any interview.

### 2. Voice

Check if `life/voice_id.txt` exists and is non-empty.

**If it exists:** read `life/voice_config.json`. If readable, check `cloned_at` -- if 6+ days ago, warn the user: `Your voice clone was created on {date} and may have expired (cloned voices are deleted after 7 days of non-use). Want to re-clone with a new recording, or try the existing one?`

- Re-clone: go to "If it does not exist" below.
- Keep it: use the existing voice ID.

If `life/voice_config.json` is missing or unreadable, use the voice ID from `life/voice_id.txt` as-is.

**If it does not exist** (or user chose to re-clone):

- 1. Ask the user: `I don't have a voice clone yet. You can: (a) send me a voice recording (10s-5min, clear speech) and I'll clone it, or (b) say "skip" to use a default voice.`
- 2. **Do not proceed until the user responds.**
- 3. **User says "skip":** use `English_radiant_girl`.
- 4. **User sends an audio file:** run:
  ```
  python $SKILL_DIR/scripts/pikastreaming_screening_interview.py clone-voice \
    --audio <path> --name <voice_name> --noise-reduction
  ```
  - Exit 0: read `life/voice_id.txt`. Tell user: `Voice cloned. Using {voice_id} for interviews.`
  - Exit non-zero: tell user cloning failed (include stderr). Ask: `Try again with a different file, or skip and use the default voice?`
- 5. **Invalid file (not audio):** respond `That doesn't look like a supported audio file. Send an mp3, m4a, wav, ogg, flac, or aac file (10s-5min of clear speech).` Wait for retry or "skip".

## Interview Plan Setup

Before running interviews, create an interview plan:

### Step 1 -- Gather Role Info

Ask the user:
- `What role are you hiring for?` (e.g. SDR, Customer Support, Software Engineer)
- `How many questions should each interview have?` (default: 8)
- `Any specific topics or skills to assess?` (optional)
- `Do you have a rubric file, or should I use a default?` (check `$SKILL_DIR/assets/rubrics/` for built-in rubrics)

### Step 2 -- Create the Plan

```
python $SKILL_DIR/scripts/pikastreaming_screening_interview.py create-plan \
  --role <role_title> \
  --num-questions <n> \
  --rubric <path_to_rubric.json> \
  --topics "<comma,separated,topics>" \
  --output /tmp/interview_plan.json
```

This generates:
- A structured question list with follow-up prompts
- Scoring criteria per question mapped to the rubric
- A system prompt tailored for the interviewer role

Show the user a summary: `Created interview plan for {role} with {n} questions. Topics: {topics}. Ready to start interviewing.`

## Candidate Batch Setup

To screen candidates at scale, the user provides a CSV or JSON file with candidate info:

```
python $SKILL_DIR/scripts/pikastreaming_screening_interview.py load-candidates \
  --file <candidates.csv> \
  --output /tmp/candidate_queue.json
```

Expected CSV columns: `name, email, meet_url` (optional: `resume_url, notes`)

Show the user: `Loaded {n} candidates. Ready to begin screening interviews.`

## Interview Flow

### Step 1 -- Validate & Prepare

**Avatar:** check `identity/videomeeting-avatar.png` exists and is > 1 KB. If not, run First-Time Setup above.

**Voice:** check `life/voice_id.txt` exists. If not, run the Voice section of First-Time Setup above.

**Plan:** check `/tmp/interview_plan.json` exists. If not, run Interview Plan Setup above.

**Context:** Build the interviewer system prompt:

- 1. Read the interview plan from `/tmp/interview_plan.json`.
- 2. Read any workspace context (MEMORY.md, role description files, etc.).
- 3. Synthesize to `/tmp/interview_system_prompt.txt`:

```
Synthesize the interview plan below into a concise interviewer persona for {bot_name}.
Use third-person ("{bot_name}") throughout.

INTERVIEW RULES:
1. Greet the candidate warmly and introduce yourself as {bot_name}, an AI screening interviewer for {company_name}.
2. Explain this is a structured first-round screening that will take about {duration} minutes.
3. Ask each question from the plan in order. Listen to the full answer before moving on.
4. Ask ONE follow-up per question if the answer is vague or incomplete.
5. Do NOT ask about: age, race, religion, marital status, disability, pregnancy, national origin, or any legally protected characteristic.
6. Do NOT make hiring decisions or promises. Say: "Our team will review and follow up."
7. End by thanking the candidate and explaining next steps.
8. Keep a professional, warm, and encouraging tone throughout.

QUESTION PLAN:
{questions_from_plan}

SCORING CRITERIA:
{rubric_criteria}

ROLE CONTEXT:
{role_description}
```

### Step 2 -- Join Interview

For each candidate (or a single candidate if user provides one meet URL):

```
python $SKILL_DIR/scripts/pikastreaming_screening_interview.py join \
  --meet-url <url> \
  --bot-name <interviewer_name> \
  --image identity/videomeeting-avatar.png \
  --system-prompt-file /tmp/interview_system_prompt.txt \
  --voice-id <voice_id> \
  --candidate-name <name> \
  --session-tag <candidate_id> \
  [--meeting-password <pw>]
```

Tell the user: `Joined interview with {candidate_name}. Say "leave" to end, or "next" to end and move to the next candidate.`

**Exit codes:** 0 = joined. 6 = insufficient credits (stdout JSON has `checkout_url` -- show it).

### Step 3 -- Leave & Score

```
python $SKILL_DIR/scripts/pikastreaming_screening_interview.py leave \
  --session-id <id>
```

Then immediately score:

```
python $SKILL_DIR/scripts/pikastreaming_screening_interview.py score \
  --session-id <id> \
  --rubric <path_to_rubric.json> \
  --output /tmp/scorecard_<candidate_id>.json
```

This produces a scorecard with:
- Per-question scores (1-5)
- Overall weighted score
- Strengths and weaknesses
- Recommendation: ADVANCE / MAYBE / PASS
- Key quotes from the candidate

Show the user a brief summary: `{candidate_name}: {overall_score}/5 -- {recommendation}. Top strength: {strength}. Area of concern: {weakness}.`

## Batch Run

To run through all loaded candidates sequentially:

```
python $SKILL_DIR/scripts/pikastreaming_screening_interview.py batch-run \
  --queue /tmp/candidate_queue.json \
  --plan /tmp/interview_plan.json \
  --image identity/videomeeting-avatar.png \
  --voice-id <voice_id> \
  --bot-name <interviewer_name> \
  --output-dir /tmp/scorecards/
```

This will:
1. Join each candidate's meeting link in order
2. Run the structured interview
3. Leave and score each candidate
4. Write individual scorecards to the output directory
5. Print progress: `[3/100] Completed interview with {name} -- {score}/5 {recommendation}`

## Export Results

After interviews are complete:

```
python $SKILL_DIR/scripts/pikastreaming_screening_interview.py export \
  --input-dir /tmp/scorecards/ \
  --format <csv|json|markdown> \
  --sort-by score \
  --output /tmp/screening_results.<ext>
```

This produces a ranked summary of all candidates with:
- Name, score, recommendation, key strengths, concerns
- Sorted by score (descending) by default
- CSV format is ATS-import ready

Show the user: `Exported {n} candidate results to {output_path}. Top candidates: {top_3_names}.`

## Built-in Rubrics

Available in `$SKILL_DIR/assets/rubrics/`:

- `sdr.json` -- Sales Development Representative
- `customer_support.json` -- Customer Support / Success
- `general.json` -- General screening (communication, problem-solving, culture fit)

Users can also provide custom rubric JSON files with the structure:
```json
{
  "role": "Role Title",
  "categories": [
    {
      "name": "Category Name",
      "weight": 0.3,
      "criteria": [
        {
          "name": "Criterion",
          "description": "What to look for",
          "scores": {
            "1": "Poor - description",
            "3": "Adequate - description",
            "5": "Excellent - description"
          }
        }
      ]
    }
  ],
  "pass_threshold": 3.0,
  "advance_threshold": 4.0
}
```

## Safety & Compliance

- The interviewer bot MUST NOT ask about legally protected characteristics
- All questions must be job-relevant
- The bot does not make hiring decisions -- it provides structured data for humans
- Candidates should be informed they are speaking with an AI interviewer
- Interview data should be handled according to applicable data protection regulations
