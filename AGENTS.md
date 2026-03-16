# AGENTS.md - Model Trucks Codebase Guide

This document provides guidelines for agentic coding agents working in the model_trucks repository.

## Project Overview

This is a truck turnaround time prediction system using TimescaleDB, Grafana, and machine learning (C4.5 algorithm). The system:
- Uses Docker containers for TimescaleDB and Grafana
- Implements a C4.5 decision tree regression model for predictions
- Loads data into TimescaleDB and visualizes results in Grafana dashboards

## Build/Test/Lint Commands

### Docker Services
```bash
# Start services (TimescaleDB + Grafana)
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f
```

### Python Scripts
```bash
# Install dependencies (in respective directories)
# data_loader
cd data_loader
pip install -r requirements.txt  # Requires: psycopg2-binary
cd ..

# data_extract
cd data_extract
pip install -r requirements.txt  # Requires: psycopg2-binary
cd ..

# c4_5
cd c4_5
pip install -r requirements.txt  # Requires: pandas numpy scikit-learn jsons psycopg2-binary
cd ..


# Run data loader (from data_loader/ directory)
python data_loader.py <json_file> <database> <user> <password> <host> <table> --create
# Example:
python data_loader.py ../data/base_10000_01.json trucks_db postgres password localhost trucks_table --create


# Run data extraction (from data_extract/ directory)
python data_extract.py -db <database> -u <user> -p <password> -host <host> -t <table> [-o output.json]

# Run C4.5 algorithm (from c4_5/ directory)
python algoritm_c4_5.py -i_tra <training.json> -i_tst <testing.json> -db <database> -u <user> -p <password> -host <host> -t <table> [-o output.json]
```

### Testing
No formal test framework detected. Code validation should be done through:
1. Manual execution of scripts
2. Database connectivity tests
3. JSON file validation
4. Grafana dashboard verification

## Code Style Guidelines

### Python Code Style
**Imports:**
- Standard library imports first, then third-party, then local
- Use full module names (not wildcard imports)
- Import order: built-in → external → project
```python
import json
import collections
import argparse
import sys

import pandas as pd
import numpy as np
import psycopg2
from sklearn.model_selection import GridSearchCV
from sklearn.tree import DecisionTreeRegressor
```

**Formatting:**
- Use 4-space indentation (consistent with existing code)
- Max line length: ~100 characters (based on observed code)
- Function names: snake_case
- Variable names: snake_case
- Class names: PascalCase (if used)

**Error Handling:**
- Use try-except blocks for database operations
- Print clear error messages with sys.exit(1) for fatal errors
- Validate JSON input with try-catch
```python
try:
    conn = psycopg2.connect(conn_string)
except psycopg2.Error as e:
    print('Unable to connect!\n%s' % e)
    sys.exit(1)
```

**Command-line Arguments:**
- Use argparse with required/optional argument groups
- Provide clear help text for all parameters
- Validate input types in argparse
```python
parser = argparse.ArgumentParser(description=text)
parser._action_groups.pop()
required = parser.add_argument_group('required arguments')
optional = parser.add_argument_group('optional arguments')
```

### Database/SQL Conventions
- Use parameterized queries for security.
- Table names: lowercase_with_underscores
- Column names: lowercase_with_underscores
```python
# Example of parameterized query
cursor.execute("SELECT * FROM %s WHERE id = %s", (table_name, some_id))
```

### File Organization
- Keep related files in dedicated directories:
  - `data_loader/`: Python data loading scripts
  - `data_extract/`: Python data extraction scripts  
  - `c4_5/`: Machine learning algorithms
  - `dashboard/`: Grafana dashboard JSON files
  - `experiments/`: Experiment results and data
  - `data/`: Sample data files
  - `config_images/`: Documentation images

### Naming Conventions
- JSON files: descriptive names with sizes (e.g., `base_10000_01.json`)
- Database tables: plural nouns (e.g., `trucks`, `predictions`)
- Functions: descriptive verbs (e.g., `create_database`, `upload_to_timescale`)
- Variables: descriptive names (e.g., `connection_data`, `parsed_json`)

## Development Workflow

### Adding New Features
1. Check existing patterns in similar directories
2. Follow import/formatting conventions
3. Add appropriate error handling
4. Update README.md if adding new commands
5. Test with sample data

### Modifying Existing Code
1. Maintain backward compatibility with command-line arguments
2. Preserve existing database schemas
3. Keep JSON file formats consistent
4. Update requirements.txt if adding new dependencies

### Code Review Checklist
- [ ] Follows existing import patterns
- [ ] Consistent indentation (4 spaces for Python)
- [ ] Error handling for database operations
- [ ] Clear console output messages
- [ ] Command-line help text updated if needed
- [ ] No hardcoded credentials
- [ ] JSON parsing with error handling

## Common Patterns

### Database Connection
```python
# Python pattern
conn_string = "dbname=" + db + " user=" + user + " password=" + password + " host=" + host
conn = psycopg2.connect(conn_string)
```

### JSON Processing
```python
# Python pattern
with open(file_path, 'r') as f:
    data = json.load(f)
```

### Command-line Interface
Python scripts use `argparse` with comprehensive CLI arguments:
- Required and optional parameters
- Clear help text
- Input validation
- Default values for optional parameters

## Agent Notes

1. **No test framework** - Test manually by running scripts
2. **Docker-centric** - Most operations depend on Docker services
3. **Data pipeline focus** - Code transforms data between JSON ↔ Database ↔ ML model
4. **Documentation in README.md files** - Each directory has its own usage instructions

Always check directory-specific README.md files for additional instructions before modifying code.