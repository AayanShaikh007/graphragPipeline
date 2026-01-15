import asyncio
import pandas as pd
from pathlib import Path
from datetime import datetime
import json

import graphrag.api as api
from graphrag.config.load_config import load_config

path = Path(r"C:\Coding\graphrag")
config = load_config(path)

# load parquet files (indexed data) 
text_units = pd.read_parquet(path/"output"/"text_units.parquet")
entities = pd.read_parquet(path/"output"/"entities.parquet")
relationships = pd.read_parquet(path/"output"/"relationships.parquet")
communities = pd.read_parquet(path/"output"/"communities.parquet")
community_reports = pd.read_parquet(path/"output"/"community_reports.parquet")



# function to save the query results 
async def save_results(search_type, query, response, context):
    
    # Save query results to a timestamped folder named by date and search type
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    query_folder = path / "queries" / f"query_{timestamp}_{search_type}"
    query_folder.mkdir(parents=True, exist_ok=True)
    
    # Save the query text to a file called query.txt
    (query_folder / "query.txt").write_text(query, encoding="utf-8")
    
    # Save the final answer to a file called final_answer.txt
    (query_folder / "final_answer.txt").write_text(str(response), encoding="utf-8")
    
    # Save context data in context files
    if isinstance(context, dict):
        for key, value in context.items():
            if isinstance(value, pd.DataFrame):
                # I saved the identical data to a csv for easy viewing within VSCode, otherwise this line is redundant
                value.to_csv(query_folder / f"context_{key}.csv", index=False)
                value.to_json(query_folder / f"context_{key}.json", orient="records", indent=2)
            else:
                with open(query_folder / f"context_{key}.json", "w", encoding="utf-8") as f:
                    json.dump(value, f, indent=2, default=str)
    
    # save nodes from the "entities" file, in csv(redundant) and json 
    entities.to_csv(query_folder / "nodes.csv", index=False)
    entities.to_json(query_folder / "nodes.json", orient="records", indent=2)
    
    # save edges from the "relationships" file, in csv(redundant) and json 
    relationships.to_csv(query_folder / "edges.csv", index=False)
    relationships.to_json(query_folder / "edges.json", orient="records", indent=2)
    
    print(f"results: {search_type} saved in {query_folder.name}")

async def main():
    query = "What is H2@home used for?"
    
    print(f"\n running query: '{query}'\n")
    
    # run all search methods for each query, using a try case.
    try:
        response, context = await api.basic_search(
            config=config,
            text_units=text_units,
            query=query
        )
        await save_results("basic", query, response, context)
    except Exception:
        print("basic search failed")
    

    try:
        response, context = await api.local_search(
            config=config,
            entities=entities,
            communities=communities,
            community_reports=community_reports,
            text_units=text_units,
            relationships=relationships,
            covariates=None,
            community_level=2,
            response_type="Multiple Paragraphs",
            query=query
        )
        await save_results("local", query, response, context)
    except Exception:
        print("local search failed")
    
    
    try:
        response, context = await api.global_search(
            config=config,
            entities=entities,
            communities=communities,
            community_reports=community_reports,
            community_level=2,
            dynamic_community_selection=False,
            response_type="Multiple Paragraphs",
            query=query
        )
        await save_results("global", query, response, context)
    except Exception:
        print("global search failed")
    
    # Drift search is more complex and seems to have issues with JSON responses in the primer
    
    # try:
    #     response, context = await api.drift_search(
    #         config=config,
    #         entities=entities,
    #         communities=communities,
    #         community_reports=community_reports,
    #         text_units=text_units,
    #         relationships=relationships,
    #         community_level=1,
    #         response_type="Single Paragraph",
    #         query=query
    #     )
    #     await save_results("drift", query, response, context)
    # except Exception as e:
    #     print(f"drift search failed: {e}")
    #     import traceback
    #     traceback.print_exc()
    
    print()

asyncio.run(main())