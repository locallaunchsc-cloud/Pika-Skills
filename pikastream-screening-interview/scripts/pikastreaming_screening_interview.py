#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path
from datetime import datetime


def ensure_key():
    key = os.getenv("PIKA_DEV_KEY")
    if not key:
        raise SystemExit("PIKA_DEV_KEY is not set")
    return key


def load_text(path):
    if not path:
        return ""
    return Path(path).read_text(encoding="utf-8")


def load_json(path):
    if not path:
        return {}
    return json.loads(Path(path).read_text(encoding="utf-8"))


def create_plan(args):
    plan = {
        "created_at": datetime.utcnow().isoformat() + "Z",
        "role_title": args.role_title,
        "role_context": load_text(args.role_context),
        "rubric": load_json(args.rubric),
        "default_style": args.style,
        "question_strategy": [
            "opening_intro",
            "experience_validation",
            "scenario_question",
            "motivation_check",
            "availability_and_logistics",
            "candidate_questions",
            "close_and_human_review_notice",
        ],
    }
    Path(args.output).write_text(json.dumps(plan, indent=2), encoding="utf-8")


def build_prompt(args):
    role_context = load_text(args.role_context)
    candidate_context = load_text(args.candidate_context)
    rubric = load_json(args.rubric)
    prompt = {
        "bot_name": args.bot_name,
        "style": args.style,
        "role_title": args.role_title,
        "candidate_name": args.candidate_name,
        "instructions": [
            "You are conducting a first-round screening interview.",
            "Stay professional, concise, and warm.",
            "Ask only job-relevant questions.",
            "Do not make hiring promises.",
            "Tell the candidate a human team will review the interview.",
            "Use short follow-up questions to clarify vague answers.",
        ],
        "role_context": role_context,
        "candidate_context": candidate_context,
        "rubric": rubric,
    }
    return json.dumps(prompt, indent=2)


def join_interview(args):
    ensure_key()
    payload = {
        "meet_url": args.meet_url,
        "candidate_name": args.candidate_name,
        "bot_name": args.bot_name,
        "image": args.image,
        "voice_id": args.voice_id,
        "system_prompt": build_prompt(args),
        "status": "stub_ready_for_pika_api",
    }
    out = Path(args.output or f"session-{args.candidate_name.lower().replace(' ', '-')}.json")
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def leave_interview(args):
    ensure_key()
    result = {
        "session_id": args.session_id,
        "action": "leave",
        "status": "stub_ready_for_pika_api",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    print(json.dumps(result))


def summarize_interview(args):
    summary = {
        "session_id": args.session_id,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "recommendation": "review",
        "notes": [
            "Replace this stub with Pika meeting notes retrieval and rubric scoring.",
            "Map answers to rubric categories and compute a weighted score.",
            "Return recruiter-facing strengths, risks, and next-step recommendation.",
        ],
        "rubric": load_json(args.rubric),
    }
    Path(args.output).write_text(json.dumps(summary, indent=2), encoding="utf-8")


def export_results(args):
    input_dir = Path(args.input_dir)
    files = sorted(input_dir.glob("*.json")) if input_dir.exists() else []
    rows = []
    for file in files:
        try:
            rows.append(json.loads(file.read_text(encoding="utf-8")))
        except Exception:
            continue
    if args.format == "json":
        Path(args.output).write_text(json.dumps(rows, indent=2), encoding="utf-8")
    else:
        lines = ["# Ranked candidates", ""]
        for i, row in enumerate(rows, 1):
            name = row.get("candidate_name") or row.get("session_id") or f"Candidate {i}"
            lines.append(f"## {i}. {name}")
            lines.append("")
            lines.append(f"- Status: {row.get('status', 'unknown')}")
            lines.append("")
        Path(args.output).write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    p1 = sub.add_parser("create-plan")
    p1.add_argument("--role-title", required=True)
    p1.add_argument("--role-context", required=True)
    p1.add_argument("--rubric", required=True)
    p1.add_argument("--style", default="friendly_recruiter")
    p1.add_argument("--output", required=True)
    p1.set_defaults(func=create_plan)

    p2 = sub.add_parser("join")
    p2.add_argument("--meet-url", required=True)
    p2.add_argument("--candidate-name", required=True)
    p2.add_argument("--role-title", required=True)
    p2.add_argument("--role-context", required=True)
    p2.add_argument("--rubric", required=True)
    p2.add_argument("--bot-name", required=True)
    p2.add_argument("--image", required=True)
    p2.add_argument("--voice-id")
    p2.add_argument("--candidate-context")
    p2.add_argument("--style", default="friendly_recruiter")
    p2.add_argument("--output")
    p2.set_defaults(func=join_interview)

    p3 = sub.add_parser("leave")
    p3.add_argument("--session-id", required=True)
    p3.set_defaults(func=leave_interview)

    p4 = sub.add_parser("summarize")
    p4.add_argument("--session-id", required=True)
    p4.add_argument("--rubric", required=True)
    p4.add_argument("--output", required=True)
    p4.set_defaults(func=summarize_interview)

    p5 = sub.add_parser("export")
    p5.add_argument("--input-dir", required=True)
    p5.add_argument("--format", choices=["json", "markdown"], default="markdown")
    p5.add_argument("--output", required=True)
    p5.set_defaults(func=export_results)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
