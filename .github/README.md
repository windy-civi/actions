# GitHub Labels Template

This directory contains a reusable label template for GitHub repositories.

## Files

- `labels.json` - JSON file containing all label definitions
- `apply-labels.sh` - Script to apply labels to any GitHub repository

## Setup (One-Time)

### 1. Install GitHub CLI

```bash
brew install gh
```

### 2. Authenticate

```bash
gh auth login
```

## Usage

### Apply Labels to Current Repository

From any directory in this repo:

```bash
.github/apply-labels.sh
```

### Apply Labels to Any Repository

```bash
.github/apply-labels.sh owner/repo-name
```

For example:

```bash
.github/apply-labels.sh wanderlust-create/USA-pipeline-sample
```

## Labels Included

### Type Labels

- `bug` - Something isn't working
- `enhancement` - New feature or improvement
- `documentation` - Documentation improvements
- `refactor` - Code refactoring/cleanup
- `performance` - Performance improvements
- `security` - Security-related issues

### Component Labels

- `scraper` - OpenStates scraping issues
- `formatter` - Data formatting/processing
- `text-extraction` - Text extraction pipeline
- `data-pipeline` - Overall data pipeline
- `github-actions` - CI/CD workflows
- `infrastructure` - Infrastructure/deployment

### Priority Labels

- `priority: critical` - Blocking issue, needs immediate attention
- `priority: high` - Important, should be done soon
- `priority: medium` - Normal priority
- `priority: low` - Nice to have

### Status Labels

- `in-progress` - Currently being worked on
- `blocked` - Waiting on something else
- `needs-testing` - Ready for testing
- `ready-for-review` - Ready for code review

### Complexity Labels

- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed
- `complex` - Requires significant effort

### Data Quality Labels

- `data-quality` - Data accuracy/completeness issues
- `missing-data` - Data not being captured
- `data-loss` - Risk of losing data

### State-Specific Labels

- `state: federal` - Federal/USA issues
- `state: specific` - State-specific issues

## Customizing

Edit `labels.json` to add, remove, or modify labels. The format is:

```json
{
  "name": "label-name",
  "color": "hexcolor",
  "description": "Description text"
}
```

Colors are 6-digit hex codes without the `#` symbol.

## Reusing Across Projects

You can copy the `.github/` directory to any new project, or keep it in a central location and reference it when needed.

Alternatively, symlink the files:

```bash
cd ~/path/to/new-project
mkdir -p .github
ln -s ~/path/to/this/.github/labels.json .github/labels.json
ln -s ~/path/to/this/.github/apply-labels.sh .github/apply-labels.sh
```
