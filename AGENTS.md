# LLM Agent Structure

This document outlines a basic structure for defining and understanding LLM agents for coding assistance.

## Purpose

A clear and concise statement about the agent's primary goal. What problem does it solve?

* **Example:** This agent assists developers by automatically applying labels from issues to the pull requests that close them.

## Capabilities

A description of the agent's skills, knowledge domains, and available tools.

* **Skills:**
    * Natural Language Understanding
    * Code Analysis
    * GitHub API Interaction
* **Knowledge Domain:**
    * GitHub Actions
    * Pull Requests and Issues
    * Labeling best practices
* **Tools:**
    * `read_file`: To understand project context.
    * `write_file`: To create or modify files.
    * `run_shell_command`: To execute commands, like `git`.
    * `github_api`: To interact with GitHub.

## Interaction Model

How do users interact with the agent? Is it through a chat interface, command-line, or something else?

* **Interface:** Chat-based interaction within a terminal.
* **Invocation:** Users can invoke the agent with a natural language command.
* **Responses:** The agent responds with a combination of text and tool calls.

## Examples

Illustrative examples of user-agent interactions.

**Example 1: Summarizing the project**

> **User:** Give this project an overview summary.
>
> **Agent:** This project is a GitHub Action that automatically copies labels from any issues that are closed by a pull request to the pull request itself.

**Example 2: Creating a new file**

> **User:** I want you to create an AGENTS.md file in order to help understand the structure for LLM agents while coding with us.
>
> **Agent:** (Creates the `AGENTS.md` file with a predefined structure)

### How it Works

The action is composed of three shell scripts:

*   `entrypoint.sh`: The main script that orchestrates the process. It does the following:
    1.  Calls `get-closing-labels` to fetch all labels from issues closed by the pull request.
    2.  Calls `get-removed-labels` to fetch all labels that have been recently removed from the pull request.
    3.  Uses `jq` to compute the final set of labels to be added. This logic considers the `exclude` input and whether to respect the `unlabeled` event.
    4.  Uses the `gh` CLI to add the final labels to the pull request.

*   `get-closing-labels`: This script uses a GitHub GraphQL query to find all issues that are referenced as "closing" by the pull request. It then extracts and returns a unique list of labels from these issues.

*   `get-removed-labels`: This script uses a GitHub GraphQL query to look at the pull request's timeline. It finds all `UnlabeledEvent`s and returns a unique list of labels that were removed.

## Document Structure

This document is organized into the following sections:

* **Purpose:** A high-level description of the agent's objective.
* **Capabilities:** The skills, knowledge, and tools the agent possesses.
* **Interaction Model:** How users can interact with the agent.
* **Examples:** Concrete examples of user-agent interactions.
* **Document Structure:** This section, which describes the layout of this document.

## Refactoring from Shell to Python

We discussed the possibility of refactoring the project's shell scripts into
Python to improve long-term maintainability. Here is a summary of that
conversation:

### Initial State & Suggestions

The project initially consisted of three shell scripts (`get-closing-labels`, `get-removed-labels`, `entrypoint.sh`) that orchestrated `gh` and `jq` commands to sync labels from closing issues to pull requests. The `get-closing-labels` script fetches labels from issues closed by a PR, while `get-removed-labels` fetches labels recently removed from the PR. The `entrypoint.sh` script coordinates these scripts and uses a complex `jq` query to determine the final labels to apply to the PR.

### Rationale for Migrating to Python

The conversation then moved towards a more robust solution: migrating the logic to Python. The primary reasons for this recommendation were:

*   **Testability:** Python offers mature testing frameworks like `pytest`, making it much easier to write reliable unit tests compared to shell scripts.
*   **Readability & Maintainability:** For the level of complexity in this project, Python provides a more readable and structured way to express the logic, especially for data manipulation, which is currently handled by a complex `jq` query.
*   **Robustness:** A Python implementation would interact directly with the GitHub API (e.g., via the `requests` library), which is a more stable and robust integration than parsing the output of a CLI tool.

### Addressing Overhead Concerns

We also addressed potential concerns about the overhead of switching to Python:

*   **Performance:** The speed of the action would not be noticeably affected. The primary bottleneck is network I/O from GitHub API calls, which is common to both approaches.
*   **Size:** While a Python Docker image would be larger than the current one, the increase can be managed by using optimized base images (like `python:slim` or `python:alpine`) and multi-stage builds. The trade-off in size is worthwhile for the significant gains in maintainability.

### Implementation Strategy

The recommended approach is to process API responses directly within Python rather than shelling out to `gh --jq`. This "pure Python" approach is cleaner, easier to test, and less brittle.

The plan is to migrate the scripts incrementally, starting with one piece of functionality to demonstrate the benefits.

## Security Audit and Documentation

A security audit of this action was performed to assess the risks associated
with using the `pull_request_target` trigger. The audit identified a command
injection vulnerability that is only exploitable by repository maintainers, and
not by external contributors via the `pull_request_target` trigger.

As a result of this audit, the following changes were made:

*   A `SECURITY.md` file was created to provide a clear security policy and instructions for reporting vulnerabilities.
*   The `README.md` was updated with a "Security" section that links to the new `SECURITY.md` file.
*   The `SECURITY.md` file includes a section explaining the use of `pull_request_target` and why it is considered safe for this action.

These changes improve the project's security posture and provide transparency for users.

## Local Development

To build and run the Docker container used in the action locally, you can use
the following Make commands:

*   `make build`: Builds the Docker image. You can specify a different version of the `gh` CLI by passing the `GH_VERSION` variable (e.g., `GH_VERSION=2.81.0 make build`).
*   `make interactive`: Enters an interactive shell within the running container.

Once inside the container, you can run the action script with the necessary environment variables:

```sh
INPUT_OWNER="williambdean" \
INPUT_REPO="closing-labels" \
INPUT_PR_NUMBER="21" \
INPUT_EXCLUDE="wontfix,duplicate" \
INPUT_RESPECT_UNLABELED="true" \
INPUT_DRY_RUN="true" \
./entrypoint.sh
```

This setup allows for local testing and development of the action's functionality.
