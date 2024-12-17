import requests
import os
from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime
from dotenv import load_dotenv
from tinybird import TinybirdClient, QueryResult
from collections import defaultdict
from prettytable import PrettyTable

# Load environment variables
load_dotenv()

@dataclass
class SqlQuery:
    namespace: str
    benchmark: str
    name: str
    path: str
    content: str

def discover_benchmarks(root_dir: str = "benchmarks") -> List[SqlQuery]:
    queries = []
    
    # Walk through all directories under benchmarks
    for namespace in os.listdir(root_dir):
        namespace_path = os.path.join(root_dir, namespace)
        if not os.path.isdir(namespace_path):
            continue
            
        # For each benchmark directory in the namespace
        for benchmark in os.listdir(namespace_path):
            benchmark_path = os.path.join(namespace_path, benchmark)
            if not os.path.isdir(benchmark_path):
                continue
                
            # Find all SQL files in the benchmark directory
            for sql_file in os.listdir(benchmark_path):
                if not sql_file.endswith('.sql'):
                    continue
                    
                file_path = os.path.join(benchmark_path, sql_file)
                with open(file_path, 'r') as f:
                    content = f.read()
                
                name = f"{namespace}.{benchmark}.{os.path.splitext(sql_file)[0]}"
                queries.append(SqlQuery(
                    namespace=namespace,
                    benchmark=benchmark,
                    name=name,
                    path=file_path,
                    content=content
                ))
    
    return queries

def run_benchmark(query: SqlQuery, token: str) -> QueryResult:
    """
    Run a benchmark query using the Tinybird API
    
    Args:
        query: The SQL query to benchmark
        token: Tinybird API token
        
    Returns:
        QueryResult containing timing and result data
    """
    client = TinybirdClient(token)
    return client.query(query.content)

if __name__ == "__main__":
    token = os.getenv("TINYBIRD_TOKEN")
    if not token:
        print("Error: TINYBIRD_TOKEN not found in .env file")
        print("Please copy .env.template to .env and set your token")
        exit(1)
        
    queries = discover_benchmarks()
    
    # Group queries by namespace and benchmark
    benchmarks = defaultdict(lambda: defaultdict(list))
    for query in queries:
        benchmarks[query.namespace][query.benchmark].append(query)
    
    # Run benchmarks and display results
    for namespace, ns_benchmarks in benchmarks.items():
        print(f"\nNamespace: {namespace}")
        
        # Sort benchmarks by name
        sorted_benchmarks = dict(sorted(ns_benchmarks.items()))
        
        for benchmark_name, benchmark_queries in sorted_benchmarks.items():
            print(f"\nBenchmark: {benchmark_name}")
            
            # Create table
            table = PrettyTable()
            table.field_names = ["Metric"] + [os.path.splitext(os.path.basename(q.path))[0] for q in benchmark_queries]
            
            # Run queries and collect results
            results = []
            for query in benchmark_queries:
                # print(f"\nRunning {query.name}...")
                result = run_benchmark(query, token)
                results.append(result)
            
            # Add rows for each statistic
            table.add_row(["Status"] + [r.status.value for r in results])
            table.add_row(["Elapsed (s)"] + [r.statistics.elapsed for r in results])
            table.add_row(["Rows Read"] + [r.statistics.rows_read for r in results])
            table.add_row(["Bytes Read"] + [r.statistics.bytes_read for r in results])
            table.add_row(["Duration (s)"] + [(r.end_time - r.start_time).total_seconds() for r in results])
            
            print(table)
