# Meeting Minutes Agent

A local, deterministic prototype for producing executive minutes from explicitly tagged notes. It separates decisions, actions, risks and open questions, preserves source lines and makes missing responsibilities visible. An optional prompt describes how an LLM might propose tagged notes for human review. No LLM API is invoked by the executable, and it does not automatically understand unstructured transcripts.

## Quick start

Python 3.10+, no dependencies, no API keys. From repository root:

```sh
python minutes.py examples/synthetic_notes.txt
python minutes.py examples/synthetic_notes.txt --format json
python -m unittest discover -s tests -v
```

## Input format

One explicit tag per line: TITLE, DATE, ATTENDEES, SUMMARY, DECISION, ACTION, OPEN or RISK, followed by `: `. Use `ACTION: task description | owner=Name | due=2030-01-01` with optional owner and due segments; pipes are reserved for these segments. Free text or malformed lines are retained for review rather than silently classified. Dates should be explicit ISO dates. Blank notes produce an empty draft. The Markdown renderer marks missing ownership and dates; JSON retains original tagged lines and line numbers.

## Optional AI-assisted workflow

Use [the extraction prompt](prompts/llm_extraction.md) as a starting point with a separately configured model, then verify every output against the original notes. Do not share sensitive notes with external services without permission. The local parser is a formatting and validation tool, not a factual verifier or model evaluator. No model quality results or commercial time savings have been measured. No external actions are taken.

See [architecture](docs/architecture.md) and [test results](docs/test_results.md). Portfolio prototype by Ignacio Imperatrice. No open-source license is granted by this repository.
