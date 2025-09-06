import os
import json
import argparse
import logging # Import the logging module
from openai import OpenAI

# Configure logging for console output only (global configuration)
# All logging messages (INFO, DEBUG, ERROR) will go to the console (stdout).
# DEBUG messages will only be visible if level is set to logging.DEBUG.
logging.basicConfig(
    level=logging.INFO, # Set the default logging level to INFO for console
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def make_openrouter_api_call(client: OpenAI, payload: dict) -> str:
    """
    Makes an API call to OpenRouter based on the provided payload.

    Args:
        client: An initialized OpenAI client configured for OpenRouter.
        payload: A dictionary containing the API request payload (e.g., with 'messages' or 'prompt').

    Returns:
        The content of the API response as a string.

    Raises:
        Exception: If an error occurs during the API call or if the payload is invalid.
    """
    logging.debug("Entering make_openrouter_api_call function.")
    api_response_content = "" # To store the extracted content

    if "messages" in payload:
        model_name = payload.get('model', 'Unknown Model (Chat)')
        logging.info(f"Sending chat completion request to model: {model_name}")
        logging.debug(f"Chat completion payload being sent: {json.dumps(payload, indent=2)}")
        chat_completion = client.chat.completions.create(**payload)
        api_response_content = chat_completion.choices[0].message.content
        logging.info("API Response (Chat Completion) received.")
        logging.debug(f"Full chat completion response: {chat_completion.model_dump_json(indent=2)}")
    elif "prompt" in payload:
        model_name = payload.get('model', 'Unknown Model (Text)')
        logging.info(f"Sending text completion request to model: {model_name}")
        logging.debug(f"Text completion payload being sent: {json.dumps(payload, indent=2)}")
        text_completion = client.completions.create(**payload)
        api_response_content = text_completion.choices[0].text
        logging.info("API Response (Text Completion) received.")
        logging.debug(f"Full text completion response: {text_completion.model_dump_json(indent=2)}")
    else:
        # Raise an exception if the payload is invalid, as this is a reusable function
        raise ValueError("Payload must contain either 'messages' (for chat) or 'prompt' (for text completion).")

    logging.debug("Exiting make_openrouter_api_call function successfully.")
    return api_response_content


def main():
    logging.info("Starting OpenRouter API client script.")
    logging.info("All logging output will be displayed on the console.")
    logging.info("API response content will be streamed to a file with a '.output' extension.")
    logging.debug("Detailed debug logging enabled (visible if console level is set to DEBUG).")


    # 2. Set up argument parsing
    parser = argparse.ArgumentParser(
        description="Make an OpenRouter API call using a JSON payload from a file."
    )
    parser.add_argument(
        "payload_file",
        type=str,
        help="Path to the JSON file containing the API request payload."
    )
    args = parser.parse_args()
    logging.debug(f"Command-line arguments parsed. Payload file: {args.payload_file}")

    # 3. Get API Key from environment variable
    api_key = os.getenv("OPENROUTER_API_KEY")
    logging.debug(f"Attempting to retrieve OPENROUTER_API_KEY from environment.")

    if not api_key:
        logging.error("Error: OPENROUTER_API_KEY environment variable not set.")
        logging.info("Please set it using: export OPENROUTER_API_KEY='your_key_here'")
        return
    logging.info("OPENROUTER_API_KEY successfully retrieved.")

    # 4. Load payload from the specified JSON file
    payload = {} # Initialize payload to an empty dict
    try:
        logging.debug(f"Attempting to open and load JSON from: {args.payload_file}")
        with open(args.payload_file, 'r') as f:
            payload = json.load(f)
        logging.info(f"Successfully loaded payload from {args.payload_file}")
        logging.debug(f"Loaded payload content: {json.dumps(payload, indent=2)}")
    except FileNotFoundError:
        logging.error(f"Error: Payload file '{args.payload_file}' not found.")
        return
    except json.JSONDecodeError as e:
        logging.error(f"Error: Could not decode JSON from '{args.payload_file}'. "
                      f"Please ensure it's a valid JSON file. Details: {e}")
        return
    except Exception as e:
        logging.error(f"An unexpected error occurred while reading the payload file: {e}")
        return

    # 5. Initialize the OpenRouter client
    logging.debug("Initializing OpenAI client for OpenRouter.")
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1/"
        )
        logging.info("OpenAI client initialized successfully with OpenRouter base URL.")
    except Exception as e:
        logging.error(f"Failed to initialize OpenAI client: {e}")
        return

    # 6. Make the API call and stream response to file
    try:
        # Call the new function to make the API request
        api_response_content = make_openrouter_api_call(client, payload)

        # Determine the output filename
        base_name = os.path.splitext(args.payload_file)[0] # Get filename without extension
        output_filename = base_name + ".output"
        logging.debug(f"Determined output filename: {output_filename}")

        # Write only the API response content to the determined output file
        logging.debug(f"Writing API response content to '{output_filename}'. Content length: {len(api_response_content)} characters.")
        with open(output_filename, 'w') as outfile:
            outfile.write(api_response_content)
        logging.info(f"API response content successfully written to '{output_filename}'.")

    except ValueError as e: # Catch specific ValueError from make_openrouter_api_call
        logging.error(f"Invalid payload for API call: {e}")
    except Exception as e:
        logging.error(f"An error occurred during the OpenRouter API call or file writing: {e}", exc_info=True) # exc_info=True logs traceback

    logging.info("Script execution finished.")

if __name__ == "__main__":
    main()
