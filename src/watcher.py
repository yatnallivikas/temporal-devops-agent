import requests
import time
import subprocess
import os
import sys

from dotenv import load_dotenv


# =========================
# LOAD ENV VARIABLES
# =========================

load_dotenv()


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OWNER = os.getenv("GITHUB_OWNER")
REPO = os.getenv("GITHUB_REPO")


# =========================
# DISABLE SSL WARNINGS
# =========================

requests.packages.urllib3.disable_warnings()


# =========================
# GITHUB API HEADERS
# =========================

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}


# =========================
# TRACK LAST FAILURE
# =========================

last_run_id = None


# =========================
# WATCHER START MESSAGE
# =========================

print("\n========== WATCHER STARTED ==========\n")

print(f"Repository: {OWNER}/{REPO}")

print("\nWatching GitHub Actions failures...\n")


# =========================
# CONTINUOUS MONITORING LOOP
# =========================

while True:

    try:

        # =========================
        # FETCH WORKFLOW RUNS
        # =========================

        url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs"

        response = requests.get(
            url,
            headers=headers,
            timeout=20,
            verify=False
        )


        # =========================
        # VALIDATE RESPONSE
        # =========================

        if response.status_code != 200:

            print("\nFailed to fetch workflow runs")

            print("Status Code:", response.status_code)

            time.sleep(30)

            continue


        response_json = response.json()


        if "workflow_runs" not in response_json:

            print("\nworkflow_runs key not found")

            time.sleep(30)

            continue


        runs = response_json["workflow_runs"]


        # =========================
        # FIND FAILED WORKFLOW
        # =========================

        failed_run = None

        for run in runs:

            if run["conclusion"] == "failure":

                failed_run = run

                break


        # =========================
        # HANDLE FAILURE
        # =========================

        if failed_run:

            current_run_id = failed_run["id"]


            # =========================
            # NEW FAILURE DETECTED
            # =========================

            if current_run_id != last_run_id:

                print("\n===================================")
                print("NEW FAILED WORKFLOW DETECTED")
                print("===================================\n")

                print("Workflow Name:", failed_run["name"])

                print("Run ID:", current_run_id)

                print("Conclusion:", failed_run["conclusion"])


                last_run_id = current_run_id


                # =========================
                # FETCH LOGS
                # =========================

                print("\nFetching GitHub Actions logs...\n")


                fetch_result = subprocess.run(
                    [
                        sys.executable,
                        "src/agents/github_log_fetcher.py"
                    ],
                    capture_output=True,
                    text=True
                )


                print(fetch_result.stdout)


                if fetch_result.returncode != 0:

                    print("\nLog fetcher failed")

                    print(fetch_result.stderr)

                    time.sleep(30)

                    continue


                # =========================
                # RUN AI ANALYSIS
                # =========================

                print("\nRunning AI log analysis...\n")


                analysis_result = subprocess.run(
                    [
                        sys.executable,
                        "src/agents/log_analyzer.py"
                    ],
                    capture_output=True,
                    text=True
                )


                print(analysis_result.stdout)


                if analysis_result.returncode != 0:

                    print("\nAI analysis failed")

                    print(analysis_result.stderr)

                else:

                    print("\n===================================")
                    print("AUTONOMOUS AI ANALYSIS COMPLETED")
                    print("===================================\n")


            else:

                print("\nNo new failures detected")


        else:

            print("\nNo failed workflows found")


    # =========================
    # HANDLE ERRORS
    # =========================

    except Exception as e:

        print("\n===================================")
        print("WATCHER ERROR")
        print("===================================\n")

        print(str(e))


    # =========================
    # WAIT BEFORE NEXT CHECK
    # =========================

    print("\nWaiting 30 seconds before next check...\n")

    time.sleep(30)