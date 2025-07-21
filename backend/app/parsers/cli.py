import argparse
import glob
import os
import json
import pathlib
import asyncio

from .xml_parser import XMLParser
from ..db.mongodb import init_mongodb, close_mongodb_connection

async def process_file(file_path: str, out_file: str):
    parser = XMLParser()
    all_nodes_dict = await parser.parse_xml(file_path)
    pathlib.Path(out_file).parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w") as write:
        json.dump(all_nodes_dict, write)

async def main():
    parser = argparse.ArgumentParser(description="Parse legislation XML files")
    parser.add_argument("leg_paths", nargs="+", help="Paths to legislation files/directories")
    parser.add_argument("--data-path", default="../../data", help="Base data directory path")
    args = parser.parse_args()

    data_path = args.data_path
    leg_paths = args.leg_paths

    # Initialize MongoDB connection
    mongodb_client = await init_mongodb()

    try:
        leg_subdir = "latest/subscriber"
        out_folder = "data/legislation"

        tasks = []
        for leg_path in leg_paths:
            files = glob.glob('*.xml', root_dir=os.path.join(data_path, leg_path, leg_subdir))
            for file in files:
                file_path = os.path.join(data_path, leg_path, leg_subdir, file)
                out_file = os.path.join(out_folder, leg_path, file.replace(".xml", ".json"))
                tasks.append(process_file(file_path, out_file))

        # Process all files concurrently
        await asyncio.gather(*tasks)
    finally:
        # Clean up MongoDB connection
        await close_mongodb_connection(mongodb_client)

def run():
    """Synchronous wrapper for the async main function"""
    asyncio.run(main())

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"Error: {e}")
        raise