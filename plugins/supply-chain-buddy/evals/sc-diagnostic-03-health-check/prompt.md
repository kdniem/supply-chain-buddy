---
description: Health check request without data. Should run a structured, SCOR-based assessment dialogue.
tags: [sc-diagnostic, advisory]
expected_outcome: Proposes a structured health check across process areas, asks a manageable first set of questions and KPI requests, explains how scores and priorities will be derived; does not invent scores.
max_turns: 10
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
---

I just started as head of supply chain at a mid-sized industrial manufacturer (about 300 million in revenue, two plants, one central warehouse). I want a quick, structured health check of where we stand before I set priorities for my first 100 days. Can you help me run it?
