# Contributing to Fintech Analytics

First off, thank you for considering contributing to the Fintech Analytics Platform! It's people like you that make the open source community such a fantastic place to learn, inspire, and create.

## 1. Where do I go from here?

If you've noticed a bug or have a question, [search the issue tracker](#) to see if someone else in the community has already created a ticket. If not, go ahead and make one!

## 2. Fork & create a branch

If this is something you think you can fix, then fork the repository and create a branch with a descriptive name.

A good branch name would be (where issue #325 is the ticket you're working on):

```sh
git checkout -b 325-fix-validation-bug
```

## 3. Local Development Setup

To get your environment ready:

1. Clone your fork locally.
2. Ensure you have Python 3.12 installed.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the CI quality gates before committing:
   ```bash
   ruff check src tests
   mypy src tests
   pytest
   ```

## 4. Architectural Boundaries

Please adhere to the Clean Architecture boundaries documented in `docs/adr/0001-clean-architecture.md`. 
- **No business logic in the FastAPI routers**.
- **Service layer classes (`IngestionPipeline`, `ModelPredictor`) must remain decoupled from specific HTTP request/response schemas**.

## 5. Implement your fix or feature

At this point, you're ready to make your changes! Feel free to ask for help; everyone is a beginner at first.

## 6. Make a Pull Request

At this point, you should switch back to your master branch and make sure it's up to date with the original repository.

1. Open a Pull Request from your fork to the main repository.
2. Ensure the GitHub Actions CI pipeline passes (Type checks, Formatting, Pytest, Security Audit, and Docker compilation).
3. A maintainer will review your code shortly!
