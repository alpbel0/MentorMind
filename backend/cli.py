#!/usr/bin/env python3
"""
MentorMind - CLI Testing Interface

Manual integration testing tool for the complete evaluation workflow.
Tests question generation, K model responses, user evaluation, and judge feedback.

Usage:
    python -m backend.cli full --metric Truthfulness
    python -m backend.cli generate --metric Safety --pool
    python -m backend.cli evaluate --response-id resp_123
    python -m backend.cli judge --evaluation-id eval_123
"""

import argparse
import json
import sys
import time
from typing import Optional

import requests

# Configuration
API_BASE_URL = "http://localhost:8000"
EVALUATION_METRICS = [
    "Truthfulness", "Helpfulness", "Safety", "Bias",
    "Clarity", "Consistency", "Efficiency", "Robustness"
]


# =====================================================
# Terminal Colors (cross-platform)
# =====================================================

class Colors:
    """ANSI color codes for terminal output."""

    # Check if we're in a terminal that supports colors
    _enabled = sys.stdout.isatty()

    HEADER = '\033[95m' if _enabled else ''
    OKBLUE = '\033[94m' if _enabled else ''
    OKCYAN = '\033[96m' if _enabled else ''
    OKGREEN = '\033[92m' if _enabled else ''
    WARNING = '\033[93m' if _enabled else ''
    FAIL = '\033[91m' if _enabled else ''
    ENDC = '\033[0m' if _enabled else ''
    BOLD = '\033[1m' if _enabled else ''


def print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")


def print_success(text: str) -> None:
    """Print success message."""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text: str) -> None:
    """Print error message."""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_info(text: str) -> None:
    """Print info message."""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def print_warning(text: str) -> None:
    """Print warning message."""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


# =====================================================
# API Functions
# =====================================================

def api_post(endpoint: str, data: dict) -> dict:
    """
    Make a POST request to the API.

    Args:
        endpoint: API endpoint path (e.g., /api/questions/generate)
        data: Request payload as dictionary

    Returns:
        Response JSON as dictionary

    Raises:
        requests.HTTPError: If the request fails
    """
    url = f"{API_BASE_URL}{endpoint}"
    response = requests.post(url, json=data)
    response.raise_for_status()
    return response.json()


def api_get(endpoint: str) -> dict:
    """
    Make a GET request to the API.

    Args:
        endpoint: API endpoint path

    Returns:
        Response JSON as dictionary

    Raises:
        requests.HTTPError: If the request fails
    """
    url = f"{API_BASE_URL}{endpoint}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


# =====================================================
# Test Commands
# =====================================================

def cmd_generate(args) -> Optional[str]:
    """
    Generate a question and get K model response.

    Args:
        args: Parsed command-line arguments

    Returns:
        Response ID if successful, None otherwise
    """
    print_header("QUESTION GENERATION TEST")

    request_data = {
        "primary_metric": args.metric,
        "use_pool": args.pool
    }

    print_info(f"Generating question for metric: {args.metric}")
    print_info(f"Using pool: {args.pool}")

    try:
        result = api_post("/api/questions/generate", request_data)

        print_success("Question generated successfully!")
        print(f"\n{Colors.BOLD}Question ID:{Colors.ENDC} {result.get('question_id')}")
        print(f"{Colors.BOLD}Response ID:{Colors.ENDC} {result.get('response_id')}")
        print(f"{Colors.BOLD}Category:{Colors.ENDC} {result.get('category')}")
        print(f"{Colors.BOLD}Model:{Colors.ENDC} {result.get('model_name')}")
        print(f"\n{Colors.BOLD}Question:{Colors.ENDC} {result.get('question')}")
        print(f"{Colors.BOLD}Response:{Colors.ENDC} {result.get('model_response')}")

        return result.get('response_id')

    except requests.exceptions.RequestException as e:
        print_error(f"API request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print_error(f"Response: {e.response.text}")
        return None


def cmd_evaluate(args) -> Optional[str]:
    """
    Submit a user evaluation (interactive prompt).

    Args:
        args: Parsed command-line arguments

    Returns:
        Evaluation ID if successful, None otherwise
    """
    print_header("EVALUATION SUBMISSION TEST")

    if not args.response_id:
        print_error("Response ID is required. Use --response-id")
        return None

    print_info(f"Submitting evaluation for response: {args.response_id}")
    print_info("Enter scores (1-5) or null for each metric:\n")

    evaluations = {}
    for metric in EVALUATION_METRICS:
        while True:
            try:
                user_input = input(f"{metric} (1-5 or null): ").strip()
                if user_input.lower() == 'null' or user_input == '':
                    score = None
                else:
                    score = int(user_input)
                    if not 1 <= score <= 5:
                        print_warning("Score must be between 1 and 5")
                        continue

                reasoning = input(f"  Reasoning: ").strip()
                evaluations[metric] = {"score": score, "reasoning": reasoning}
                break
            except ValueError:
                print_warning("Invalid input. Enter a number or 'null'")
            except KeyboardInterrupt:
                print_warning("\nEvaluation cancelled")
                return None
            except EOFError:
                # Handle non-interactive mode
                print_warning("\nNon-interactive mode detected. Using default scores.")
                # Use reasonable defaults for testing
                evaluations = {
                    metric: {"score": 3, "reasoning": "Test evaluation (CLI default)"}
                    for metric in EVALUATION_METRICS
                }
                break

    request_data = {
        "response_id": args.response_id,
        "evaluations": evaluations
    }

    try:
        result = api_post("/api/evaluations/submit", request_data)

        print_success("Evaluation submitted successfully!")
        print(f"\n{Colors.BOLD}Evaluation ID:{Colors.ENDC} {result.get('evaluation_id')}")
        print(f"{Colors.BOLD}Status:{Colors.ENDC} {result.get('status')}")
        print(f"{Colors.BOLD}Message:{Colors.ENDC} {result.get('message')}")

        return result.get('evaluation_id')

    except requests.exceptions.RequestException as e:
        print_error(f"API request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print_error(f"Response: {e.response.text}")
        return None


def cmd_judge(args) -> None:
    """
    Poll for judge evaluation feedback.

    Args:
        args: Parsed command-line arguments
    """
    print_header("JUDGE FEEDBACK TEST")

    if not args.evaluation_id:
        print_error("Evaluation ID is required. Use --evaluation-id")
        return

    evaluation_id = args.evaluation_id
    timeout = args.timeout or 60
    poll_interval = 2

    print_info(f"Polling for judge feedback: {evaluation_id}")
    print_info(f"Timeout: {timeout}s, Poll interval: {poll_interval}s\n")

    start_time = time.time()
    attempt = 0

    while time.time() - start_time < timeout:
        attempt += 1
        try:
            result = api_get(f"/api/evaluations/{evaluation_id}/feedback")

            status = result.get('status')
            if status == 'completed':
                elapsed = time.time() - start_time
                print_success(f"Judge evaluation completed in {elapsed:.1f}s!")
                print(f"\n{Colors.BOLD}Result:{Colors.ENDC}")
                print(json.dumps(result, indent=2))
                return

            elif status == 'processing':
                print_info(f"Attempt {attempt}: Still processing... ({time.time() - start_time:.1f}s elapsed)")

            time.sleep(poll_interval)

        except requests.exceptions.RequestException as e:
            print_error(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print_error(f"Response: {e.response.text}")
            time.sleep(poll_interval)

    print_warning(f"Timeout after {timeout}s. Judge evaluation may still be running.")


def cmd_full(args) -> None:
    """
    Run complete workflow: generate → evaluate → judge.

    Args:
        args: Parsed command-line arguments
    """
    print_header("FULL WORKFLOW INTEGRATION TEST")

    # Step 1: Generate question and get response
    print_info(f"{Colors.BOLD}Step 1:{Colors.ENDC} Generating question and K model response...")
    response_id = cmd_generate(args)
    if not response_id:
        print_error("Failed to generate question")
        return

    # Step 2: Submit evaluation
    print(f"\n{Colors.BOLD}Step 2:{Colors.ENDC} Submitting user evaluation...")
    args.response_id = response_id  # Set response_id for evaluate command
    evaluation_id = cmd_evaluate(args)
    if not evaluation_id:
        print_error("Failed to submit evaluation")
        return

    # Step 3: Wait for judge feedback
    print(f"\n{Colors.BOLD}Step 3:{Colors.ENDC} Waiting for judge evaluation...")
    args.evaluation_id = evaluation_id
    cmd_judge(args)

    # Summary
    print_header("TEST SUMMARY")
    print_success(f"Response ID: {response_id}")
    print_success(f"Evaluation ID: {evaluation_id}")
    print_info("Check the database to verify:")
    print("  - user_evaluations.judged = TRUE")
    print("  - (Week 4) judge_evaluations record created")


# =====================================================
# Main
# =====================================================

def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="MentorMind CLI Testing Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m backend.cli full --metric Truthfulness
  python -m backend.cli generate --metric Safety --pool
  python -m backend.cli evaluate --response-id resp_123
  python -m backend.cli judge --evaluation-id eval_123 --timeout 120

Metrics:
  Truthfulness, Helpfulness, Safety, Bias, Clarity, Consistency, Efficiency, Robustness
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Common arguments
    metric_choices = EVALUATION_METRICS

    # generate command
    generate_parser = subparsers.add_parser('generate', help='Generate question and K model response')
    generate_parser.add_argument('--metric', required=True, choices=metric_choices,
                                help='Primary metric for question generation')
    generate_parser.add_argument('--pool', action='store_true',
                                help='Use question pool instead of generating new')

    # evaluate command
    evaluate_parser = subparsers.add_parser('evaluate', help='Submit user evaluation')
    evaluate_parser.add_argument('--response-id', required=True,
                                help='Model response ID to evaluate')

    # judge command
    judge_parser = subparsers.add_parser('judge', help='Poll for judge feedback')
    judge_parser.add_argument('--evaluation-id', required=True,
                             help='Evaluation ID to check')
    judge_parser.add_argument('--timeout', type=int, default=60,
                             help='Polling timeout in seconds (default: 60)')

    # full command
    full_parser = subparsers.add_parser('full', help='Run complete workflow test')
    full_parser.add_argument('--metric', default='Truthfulness', choices=metric_choices,
                            help='Primary metric for question generation (default: Truthfulness)')
    full_parser.add_argument('--pool', action='store_true',
                            help='Use question pool instead of generating new')
    full_parser.add_argument('--timeout', type=int, default=60,
                            help='Judge polling timeout in seconds (default: 60)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    if args.command == 'generate':
        cmd_generate(args)
    elif args.command == 'evaluate':
        cmd_evaluate(args)
    elif args.command == 'judge':
        cmd_judge(args)
    elif args.command == 'full':
        cmd_full(args)


if __name__ == '__main__':
    main()
