# Logos

Logos is an experimental logic and semantics engine — a programmable framework for expressing meaning through structured syntax.
Its goal is to explore how entities, relations, temporal conditions, and inference can form the foundation of a computational model of thought.

🔹 Features (Planned & In Progress)
Entity & Relation System — Model knowledge as interconnected logical components, including temporal relations and context-sensitive truth evaluation.
Truth System — Supports multiple truth states (TRUE, FALSE, UNKNOWN, SUPERPOSITION) with probabilistic and default handling.
Temporal Relations — Track truth over time intervals with flexible defaults and overlapping interval prevention.
Reasoning Engine — Evaluate truth conditions, propagate context, and infer relationships between propositions.
Interactive REPL — Experiment with Logos expressions directly from the command line.
Extensible Core — Modular Python architecture for future semantic and symbolic extensions.

🧩 Project Structure

logos/
├── __init__.py
│
├── core/
│   ├── __init__.py
│   ├── truth.py           # Truth states, modalities, and probabilistic evaluation
│   ├── entity.py          # Core entity and relation classes
│   ├── relation.py        # Handles links between entities
│   ├── context.py         # Logical contexts and compound relation evaluation
│   ├── temporal.py        # Temporal relations and time interval management
│   ├── quantifier.py      # QuantifiedRelation logic
│   ├── ontology.py        # Data model that stores all entities/relations
│   └── save_load.py       # Save/load ontology and quantified relations to JSON
│
├── syntax/
│   ├── __init__.py
│   ├── syntax.txt           # Reference of Logos syntax rules (human-readable)
│   ├── lexer.py             # Tokenizes raw Logos code into lexemes
│   ├── parser.py            # Converts tokens into abstract syntax trees (ASTs)
│   ├── validator.py         # Checks ASTs for structural correctness and local contradictions
│   ├── transformer.py       # Optional: transforms or simplifies ASTs for reasoning engine
│   ├── interpreter.py       # Optional: executes/evaluates simple Logos expressions directly
│   ├── reasoning/
│   ├── __init__.py
│   ├── semantics.py       # Meaning resolution, truth evaluation
│   └── inference.py       # Logical inference and deduction
│
├── actions/
│   ├── __init__.py
│   └── actions.py         # Defines actions / transformations (optional)
│
├── interface/
│   ├── __init__.py
│   ├── repl.py            # Command-line REPL (read-eval-print loop)
│   └── api.py             # (optional) API or web interface
│
├── tests/
│   ├── __init__.py
│   ├── core_test_context.py
│   ├── core_test_temporal.py
│   ├── test_parser.py
│   ├── test_reasoning.py
│   └── test_repl.py
│
├── requirements.txt
├── setup.py
└── README.md

📜 License

MIT License © 2025 Dex Karchner
