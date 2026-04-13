# Architecture Diagrams

All diagrams use [Mermaid](https://mermaid.js.org) and render automatically on GitHub.

| # | Diagram | What it shows |
|---|---|---|
| 01 | [Full Workflow](01_workflow.md) | All project phases from data collection to mobile deployment |
| 02 | [ETL Data Flow](02_dataflow.md) | How raw Lichess PGN data flows into PostgreSQL |
| 03 | [Database ERD](03_database_erd.md) | Entity relationship diagram for the PostgreSQL schema |
| 04 | [ETL Process Detail](04_etl_process.md) | Step-by-step Extract → Transform → Load pipeline |
| 05 | [Gameplay Flow](05_gameplay_flow.md) | Runtime data flow during a live game (user tap → API → model → board) |

To view locally: open any `.md` file in VS Code with the Mermaid extension, or paste diagrams into [mermaid.live](https://mermaid.live).
