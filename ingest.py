from ingestion.log_parser import parse_logs, preview_parsed_logs
from ingestion.chunker import chunk_logs
from ingestion.indexer import run_ingestion

if __name__ == "__main__":
    documents = parse_logs("data/logs/daily_logs.txt")
    preview_parsed_logs(documents)
    chunks = chunk_logs(documents)
    run_ingestion(chunks)
