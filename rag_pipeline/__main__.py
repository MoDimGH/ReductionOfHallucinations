import argparse

from benchmarking import generate_ragas_dataset


def main():
    parser = argparse.ArgumentParser(description="RAG-Pipeline CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # SETUP -------------------------------
    setup_parser = subparsers.add_parser("setup", help="Setup steps")
    setup_subparsers = setup_parser.add_subparsers(dest="step", required=True)

    setup_subparsers.add_parser("create_dataset", help="Rescrape all files and create dataset")
    setup_subparsers.add_parser("create_testset", help="Create testset")

    update_db_parser = setup_subparsers.add_parser("update_database", help="Populate vector DB")
    update_db_parser.add_argument("--reset", action="store_true", help="Rebuild database from scratch")

    qa_opt_parser = setup_subparsers.add_parser("qa_optimization", help="QA optimization setup")
    qa_opt_parser.add_argument("--reset", action="store_true")

    hybrid_opt_parser = setup_subparsers.add_parser("hybrid_search_optimization", help="Hybrid search optimization setup")
    hybrid_opt_parser.add_argument("--reset", action="store_true")

    setup_subparsers.add_parser("score_thresholding_optimization", help="Score thresholding setup")
    setup_subparsers.add_parser("prompt_engineering_optimization", help="Prompt engineering setup")

    # RUN ----------------------------------
    run_parser = subparsers.add_parser("run", help="Run modes")
    run_parser.add_argument("mode", choices=["cli_chat", "web_api"], help="Choose the run mode")
    run_parser.add_argument("--optimization", choices=["qa", "hybrid_search", "score_thresholding", "prompt_engineering"],
                            help="Optional optimization to use during run")

    # EVALUATE ------------------------------
    evaluate_parser = subparsers.add_parser("evaluate", help="Evaluate current model setup")

    args = parser.parse_args()

    # Handle setup commands
    if args.command == "setup":
        if args.step == "create_dataset":
            from scraping import scrape
            scrape.main()
        elif args.step == "create_testset":
            from benchmarking import gather_usecase_groups
            gather_usecase_groups.main()
            generate_ragas_dataset.main()
        elif args.step == "update_database":
            from rag_pipeline import populate_database
            populate_database.main(reset=args.reset)
        elif args.step == "qa_optimization":
            from optimizations.qa import generate_qa_documents, populate_optimized_db
            print("Setting up QA optimization...", "(reset)" if args.reset else "")
            generate_qa_documents.main(reset=args.reset)
            populate_optimized_db.main(reset=args.reset)
        elif args.step == "hybrid_search_optimization":
            from optimizations.hybrid_search import populate_bm25_index
            print("Setting up Hybrid Search optimization...", "(reset)" if args.reset else "")
            populate_bm25_index.main(reset=args.reset)
        elif args.step == "score_thresholding_optimization":
            print("Setting up score thresholding optimization...")
            # ...
        elif args.step == "prompt_engineering_optimization":
            print("Setting up prompt engineering optimization...")
            # ...

    # Handle run commands
    elif args.command == "run":
        retriever = None
        if args.optimization == "qa_optimization":
            from rag_pipeline.constants import OPTIMIZED_DB_PATH
            from rag_pipeline.utilities import create_chroma_retriever
            retriever = create_chroma_retriever(OPTIMIZED_DB_PATH)
        elif args.optimization == "hybrid_search_optimization":
            from optimizations.hybrid_search.hybrid_retriever import HybridRetriever
            HybridRetriever.init()
            retriever = HybridRetriever.getRetriever()

        if args.mode == "cli_chat":
            from rag_pipeline import query_rag
            print(f"Running CLI chat mode {'with optimization: ' + args.optimization if args.optimization else ''}")
            query_rag.main(retriever=retriever)

        elif args.mode == "web_api":
            import uvicorn
            from web.backend.api import API
            print(f"Starting web API {'with optimization: ' + args.optimization if args.optimization else ''}")
            API.init(rag_retriever=retriever)
            app = API.getApp()
            uvicorn.run(app, host="0.0.0.0", port=8000)


    # Handle evaluate command
    elif args.command == "evaluate":
        print("Not set up yet")

    # TODO: integrate optimizations

if __name__ == "__main__":
    main()