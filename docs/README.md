# Design Documentation

Diagrams produced during Phase 1 (Planning), as required by the project spec.
Source `.mmd` files (Mermaid syntax) are included alongside rendered `.png`
images — edit the `.mmd` and re-render with:

```bash
npm install -g @mermaid-js/mermaid-cli
mmdc -i diagrams/architecture.mmd -o diagrams/architecture.png -b white
```

| Diagram | File | Description |
|---|---|---|
| System architecture | `diagrams/architecture.png` | Component-level view: frontend, API, services, AST/ML engines, storage |
| Use-case diagram | `diagrams/use_case.png` | Student and Administrator actors and their actions |
| ER diagram | `diagrams/er_diagram.png` | Users, Submissions, Comparisons, Reports and their relationships |
| Data-flow diagram | `diagrams/data_flow.png` | Upload → parse → normalize → compare → score → report pipeline |
| Sequence diagram | `diagrams/sequence_analyze.png` | Request/response flow for `POST /api/comparisons/analyze` |

See the [database schema section](../README.md#project-structure) in the root
README for the SQLAlchemy model definitions that back the ER diagram.
