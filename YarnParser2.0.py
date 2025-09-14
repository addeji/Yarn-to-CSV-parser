import csv
import argparse
import sys
import os
import re

def parse_yarn_to_csv(input_path, output_path):
    """
    Parses a raw Yarn Spinner (.yarn) file and converts it to a CSV format.

    This MODIFIED version exports ALL dialogue and choices, creating a numeric
    line ID if a #line: tag is not present.

    Args:
        input_path (str): The file path for the input .yarn file.
        output_path (str): The file path for the output CSV file.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Input file not found at '{input_path}'")
        sys.exit(1)

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        csv_writer = csv.writer(f)
        header = ['line_id', 'node_title', 'character_name', 'text', 'tags']
        csv_writer.writerow(header)

        current_node_title = "NO_TITLE"
        in_body = False
        line_counter = 0  # To generate simple numeric IDs

        for line in lines:
            line = line.strip()

            if not line:
                continue

            # --- Node Header Parsing ---
            if line.startswith('title:'):
                current_node_title = line.split(':', 1)[1].strip()
                in_body = False
            elif line.strip() == '---':
                in_body = True
            elif line.strip() == '===':
                in_body = False
                current_node_title = "NO_TITLE"

            # --- Node Body Parsing ---
            elif in_body:
                # Ignore comments and commands
                if line.startswith('//') or line.startswith('<<'):
                    continue

                # --- Line Component Extraction ---
                text = line
                tags = re.findall(r'#(\S+)', text)
                text = re.sub(r'#\S+', '', text).strip()

                line_id = ''
                other_tags = []
                for tag in tags:
                    if tag.lower().startswith('line:'):
                        line_id = tag
                    else:
                        other_tags.append(tag)

                # --- If no line_id, generate one ---
                if not line_id:
                    line_id = f"auto_id_{line_counter}"
                    line_counter += 1

                # Skips empty lines that might result from tag removal
                if not text:
                    continue

                character_name = ''
                # Handle choices
                is_choice = text.startswith('->')
                if is_choice:
                    text = text.lstrip('->').strip()
                    # Choices might have conditions, remove them
                    text = re.sub(r'<<.*>>', '', text).strip()

                # Handle character name (e.g., "Character: text")
                match = re.match(r'([^:]+):\s*(.*)', text)
                if match and not is_choice:
                    character_name = match.group(1).strip()
                    text = match.group(2).strip()

                # Writes the processed data to the CSV
                csv_writer.writerow([line_id, current_node_title, character_name, text, '; '.join(other_tags)])

    print(f"Successfully parsed |:) '{input_path}' and created/updated '{output_path}'")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="A tool to parse raw .yarn files into a CSV. Automatically handles choices and file discovery.",
        epilog="Example usage:\n"
               "1. Run with specific files: python yarn_parser.py my_dialogue.yarn my_dialogue.csv\n"
               "2. Run automatically: python yarn_parser.py (searches for a .yarn file and creates a corresponding .csv)"
    )

    parser.add_argument(
        "input_file",
        nargs='?',
        default=None,
        help="Path to the input .yarn file. If omitted, the script searches for one in the current directory."
    )
    parser.add_argument(
        "output_file",
        nargs='?',
        default=None,
        help="Path for the output .csv file. If omitted, it will be named after the input file."
    )

    args = parser.parse_args()
    input_path = args.input_file
    output_path = args.output_file

    if not input_path:
        print("No input file provided. Searching current directory for a .yarn file...")
        try:
            yarn_files = [f for f in os.listdir('.') if f.endswith('.yarn')]
            if not yarn_files:
                print("Error: No .yarn file found in the current directory.", file=sys.stderr)
                sys.exit(1)
            input_path = yarn_files[0]
            print(f"Found '{input_path}'. Using it as input.")
        except Exception as e:
            print(f"Error while searching for file: {e}", file=sys.stderr)
            sys.exit(1)

    if not output_path:
        base_name = os.path.splitext(input_path)[0]
        output_path = f"{base_name}.csv"

    parse_yarn_to_csv(input_path, output_path)