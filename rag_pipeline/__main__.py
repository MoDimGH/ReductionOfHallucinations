import argparse
from rag_pipeline import query_rag
from rag_pipeline import populate_database
from scraping import scrape
from benchmarking import gather_usecase_groups, create_ragas_dataset
import subprocess


def main():
    parser = argparse.ArgumentParser()
    # parser.add_argument("--query_text", type=str, help="The query text. If omitted, a chat instance will be started.")
    parser.add_argument('-c', '--chat', action='store_true', help="Mode: command line chat interface")
    parser.add_argument('-a', '--api', action='store_true', help="Mode: run web api")
    parser.add_argument('-r', '--reset', action='store_true', help="Mode: rebuild database from scraped files")
    parser.add_argument('-d', '--create_dataset', action='store_true', help="Mode: rescrape all files")
    parser.add_argument('-t', '--create_testset', action='store_true', help="Mode: run web api")
    
    args = parser.parse_args()
    chat_mode = args.chat
    resetDB_mode = args.reset
    scrape_mode = args.create_dataset
    api_mode = args.api
    createTestset_mode = args.create_testset

    if len(list(filter(bool, [chat_mode, resetDB_mode, scrape_mode, api_mode, createTestset_mode]))) != 1:
        raise Exception("Please specify one and only one execution mode.")
    elif chat_mode:
        query_rag.main()
    elif resetDB_mode:
        populate_database.main(True)
    elif scrape_mode:
        scrape.main()
    elif api_mode:
        subprocess.Popen(['uvicorn', 'web.backend.endpoints:app', '--reload', '--host', '0.0.0.0', '--port', '8000'])
    elif createTestset_mode:
        gather_usecase_groups.main()
        create_ragas_dataset.main()

    # TODO: besser aufteilen mit befehlen build und exec nach step/mode und ggf. optimization


if __name__ == "__main__":
    main()