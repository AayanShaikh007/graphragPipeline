# Microsoft GraphRAG Pipeline Implementation

## Project Overview

This project acheives detailed and comphreehensive logging of the Microsoft GraphRAG Pipeline during each of its intermediate steps.
GraphRAG has four different search modes: Basic Search, Local Search, Global Search, and Drift Search - the logging task is performed for each of the different search types. 

## Task Objective:
There are a number of operations that occur when a query is made to GraphRAG- the objective is to log the outputs during each of these intermediate steps. This implementation captures and saves all intermediate outputs generated during these steps in a easy-to-view format for analysis and debugging purposes.

## Installation Steps

### 1. Setup
- Clone the Github Repo
- Install Microsoft GraphRAG library (`graphrag`)
- Configure Azure OpenAI API credentials in `settings.yaml`
- Index source data in `data/` to generate knowledge graph entities, relationships, and community reports

### 2. Data Loading
The pipeline loads pre-indexed parquet files to pass to the api:
- `text_units.parquet` - Chunked text segments
- `entities.parquet` - Extracted entities (nodes)
- `relationships.parquet` - Entity relationships (edges)
- `communities.parquet` - Community clusters
- `community_reports.parquet` - Summarized community information

### 3. Logging Implementation
Created an function `save_results()` function that captures:
- **Query text** - The original question, saved as `query.txt`
- **Final answer** - LLM-generated response, saved as `final_answer.txt`
- **Context data** - Intermediate retrieval results (varies by search mode), saved as `context_reports.csv` (or .json)
- **Nodes (entities)** - Complete entity graph, saved as `nodes.csv` (or .json)
- **Edges (relationships)** - Complete relationship graph, saved as `edges.csv` (or .json)

### 4. Search Mode Execution
Implemented all four search modes with error handling:
-  **Basic Search** - Very simple text unit retrieval
- **Local Search** - Entity-based contextual search
- **Global Search** - Community-level hierarchical search
- **DRIFT Search** - Adaptive search **(this mode has known JSON parsing issues)**

## Directory Structure

```
graphrag/
├── main.py                          # Main query execution script
├── settings.yaml                    # GraphRAG configuration (API keys via env vars)
├── .gitignore                       # Excludes cache, output, API keys
├── data/                            # Source documents for indexing
│   └── resume.txt
├── output/                          # Indexed graph data (parquet files)
│   ├── text_units.parquet
│   ├── entities.parquet
│   ├── relationships.parquet
│   ├── communities.parquet
│   ├── community_reports.parquet
│   └── lancedb/                     # Vector embeddings database
├── cache/                           # LLM response cache
├── logs/                            # Indexing logs
├── prompts/                         # Custom prompt templates
└── queries/                         # Query results (timestamped folders) 
    ├── query_YYYYMMDD_HHMMSS_basic/
    │   ├── query.txt                # Original query
    │   ├── final_answer.txt         # Generated answer
    │   ├── context_*.json/csv       # Retrieved context (search-specific)
    │   ├── nodes.json/csv           # All entities
    │   └── edges.json/csv           # All relationships
    ├── query_YYYYMMDD_HHMMSS_local/
    ├── query_YYYYMMDD_HHMMSS_global/
    └── query_YYYYMMDD_HHMMSS_drift/
```

## Saved Output Files

Each query execution creates a timestamped folder containing:

| File | Description | Format |
|------|-------------|--------|
| `query.txt` | Original query prompt | Plain text |
| `final_answer.txt` | LLM generated response | Plain text |
| `context_*.json` | Retrieved context (entities, reports, text units) | JSON |
| `context_*.csv` | Same as JSON but CSV format for easy viewing | CSV |
| `nodes.json/csv` | Complete entity graph with descriptions | JSON/CSV |
| `edges.json/csv` | Complete relationship graph with weights | JSON/CSV |

### Context Data by Search Type
- **Basic**: `context_text_units` - Retrieved text chunks
- **Local**: `context_entities`, `context_relationships`, `context_reports`, `context_text_units`
- **Global**: `context_reports` - Community-level summaries
- **DRIFT**: Similar to local search with adaptive routing

## Example Query Results

**Query**: "What is H2@home used for?"

**Search Results**:
- Basic Search: Successfully retrieved relevant text units
- Local Search: Retrieved 47 entities, 23 relationships, 5 community reports
- Global Search: Generated comprehensive answer from 8 high-level community reports
- **DRIFT Search**: Failed with `JSONDecodeError` (known issue #2163)

**Sample Output Structure** (Local Search):
```json
{
  "context_entities": [...],      // Relevant entities with descriptions
  "context_relationships": [...], // Entity connections with strengths
  "context_reports": [...],       // Community summaries
  "context_text_units": [...]     // Source text chunks
}
```

## Observations & Challenges

### Observed successes
1. **Comprehensive Logging**: All intermediate outputs successfully captured for basic, local, and global searches
2. **Structured Storage**: Timestamped folders prevent overwriting and enable historical analysis
3. **Multiple Formats**: Both JSON (programmatic access) and CSV (human viewing) provided
4. **Full Graph Context**: Complete entity and relationship graphs saved for each query

### Challenges

#### DRIFT Search JSON Parsing Issue
- DRIFT search consistently fails with `JSONDecodeError: Expecting value: line 1 column 1 (char 0)`
- Root Cause: Known bug (GitHub Issue #2163) where LLM returns malformed JSON during parallel query decomposition
- I am currently troubleshooting a new GraphRAG version that ensures the LLM returns expected data


### Technical Notes
- Pydantic warnings from LiteLLM provider were observed (non-breaking)
- Model configuration: `model_supports_json: true` enables structured LLM outputs
- API Keys are stored as environment variables (`${AZURE_OPENAI_API_KEY}`) for security
- Caching: GraphRAG caches LLM responses in `cache/` to reduce API costs

## Usage

```bash
# Activate venv
.venv\Scripts\Activate.ps1

# Run program after specifing a query to prompt (query="")
python main.py

```

Results are automatically saved to `queries/query_<timestamp>_<search_type>/`

## Configuration

Key settings in `settings.yaml`:
- LLM Model: Azure OpenAI GPT-4o
- Embeddings: Azure text-embedding-ada-002
- Community Level: 2 (hierarchical clustering depth)
- Response Type: "Multiple Paragraphs" for detailed answers

## Future Improvements

1. Update GraphRAG: Install latest version with DRIFT search fix
2. Parallel Execution: Run all search modes concurrently using `asyncio.gather()`
3. Query Batching: Process multiple queries in one execution
4. Visualization: Add graph visualization for nodes/edges
5. Metrics: Track retrieval latency, token usage, and answer quality scores

## References

- [Microsoft GraphRAG Documentation](https://microsoft.github.io/graphrag/)
- [GitHub Issue #2163](https://github.com/microsoft/graphrag/issues/2163) - DRIFT Search JSON Bug
- [GraphRAG Python API](https://github.com/microsoft/graphrag/discussions/2099)
