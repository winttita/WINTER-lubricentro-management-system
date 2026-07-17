# AGENTS.md - Lubricentro Project

## Auto-load Graphify Context on Session Start

**IMPORTANT**: On every new session, before doing anything else, read `graphify-out/GRAPH_REPORT.md` to get the full architecture context of this codebase.

```bash
cat graphify-out/GRAPH_REPORT.md
```

This gives you instant knowledge of:
- God nodes (core abstractions: `get_connection`, `_crear_producto_con_stock`, `get_productos`, `add_movimiento`)
- Community structure (19 communities, key ones: updater, test_database, database connection, movements, products, categories, providers)
- Cross-file connections and surprising links
- Architecture health (0 import cycles, 100% EXTRACTED edges)

## After Code Changes

The git hooks auto-rebuild the graph on every commit. If you make changes without committing:

```bash
graphify update .
```

Then re-read `graphify-out/GRAPH_REPORT.md` for fresh context.

## Quick Queries During Session

```bash
graphify explain "nombre_funcion"
graphify path "A" "B"
graphify query "pregunta en lenguaje natural"
graphify gods
```

## Project Structure

- `database.py` - Core DB operations (connection, CRUD for products, movements, categories, providers, clients, vehicles, orders)
- `updater.py` - Auto-update mechanism (low cohesion, consider splitting)
- `tests/test_database.py` - Comprehensive test suite
- `graphify.js` - OpenCode plugin for graphify