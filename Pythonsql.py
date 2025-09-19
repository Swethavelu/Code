latest

_-----++-
import pandas as pd
import logging

# ----------------------------
# Initialize logger
# ----------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("sql_generation.log"),  # Save logs to file
        logging.StreamHandler()                     # Also log to console
    ]
)
logger = logging.getLogger(__name__)

# ----------------------------
# Function to generate SQL
# ----------------------------
def generate_sql(df):
    sql_scripts = []

    for index, row in df.iterrows():
        table = row['table_name']
        existing_col = row.get('existing_column', '')
        new_col = row.get('new_column', '')
        dtype = row.get('datatype', '')
        change = str(row.get('change_type', '')).strip().lower()
        idx_name = row.get('index', '')
        renamed = row.get('renamed_objects', '')

        # Generate SQL and log each action
        if change == 'add':
            script = f"ALTER TABLE [{table}] ADD [{new_col}] {dtype};"
            logger.info(f"Add column: Table={table}, Column={new_col}, Type={dtype}")

        elif change == 'alter':
            script = f"ALTER TABLE [{table}] ALTER COLUMN [{existing_col}] {dtype};"
            logger.info(f"Alter column: Table={table}, Column={existing_col}, NewType={dtype}")

        elif change == 'drop column':
            script = f"ALTER TABLE [{table}] DROP COLUMN [{existing_col}];"
            logger.info(f"Drop column: Table={table}, Column={existing_col}")

        elif change == 'col rename':
            script = f"EXEC sp_rename '[{table}].[{existing_col}]', '{new_col}', 'COLUMN';"
            logger.info(f"Rename column: Table={table}, OldName={existing_col}, NewName={new_col}")

        elif change == 'create table':
            script = f"-- Add to CREATE TABLE [{table}]: [{new_col}] {dtype}"
            logger.info(f"Create table column definition: Table={table}, Column={new_col}, Type={dtype}")

        elif change == 'create view':
            script = f"-- CREATE VIEW [{table}] AS SELECT ... -- Define view manually"
            logger.info(f"Create view placeholder: View={table} (manual definition needed)")

        elif change == 'drop index':
            script = f"DROP INDEX [{idx_name}] ON [{table}];"
            logger.info(f"Drop index: Table={table}, Index={idx_name}")

        elif change == 'create index':
            script = f"CREATE INDEX [{idx_name}] ON [{table}] ([{new_col}]);"
            logger.info(f"Create index: Table={table}, Index={idx_name}, Column={new_col}")

        else:
            logger.warning(f"Unknown change_type: '{change}' for Table={table}")
            script = f"-- Unknown change_type: {change} for table {table}"

        sql_scripts.append(script)

    # Output generated scripts
    for script in sql_scripts:
        print(script)

    return sql_scripts


def execute_sql_scripts(sql_scripts, conn):
    cursor = conn.cursor()
    errors = []

    try:
        # Start a transaction
        for i, script in enumerate(sql_scripts, start=1):
            try:
                logger.info(f"Executing Script {i}: {script}")
                cursor.execute(script)
            except Exception as e:
                logger.error(f"Error executing Script {i}: {script}")
                logger.error(f"Exception: {str(e)}")
                errors.append((i, script, str(e)))
                # Optional: continue executing others, or break
                # break  # Uncomment to stop on first error

        conn.commit()  # Commit all if no errors or you're continuing anyway
        logger.info("All scripts executed and committed successfully.")

    except Exception as e:
        conn.rollback()
        logger.critical("Transaction failed. Rolled back all changes.")
        logger.critical(str(e))

    finally:
        cursor.close()

    return errors


# Step 1: Read Excel and generate SQL scripts
df = pd.read_excel(r"C:\Users\storage\test.xlsx")
sql_scripts = generate_sql(df)  # Must return the list now

# Write generated scripts to a .sql file
with open("generated_scripts.sql", "w", encoding="utf-8") as f:
    for script in sql_scripts:
        f.write(script + "\n")
logger.info("SQL scripts written to 'generated_scripts.sql'")


# Step 2: Execute them
conn = pyodbc.connect(conn_str)
errors = execute_sql_scripts(sql_scripts, conn)
conn.close()

if errors:
    logger.warning(f"{len(errors)} script(s) failed.")
else:
    logger.info("All scripts ran successfully.")



latest:
import subprocess
import shutil
import os
import sys

# -------- Configuration --------
src_file = "scripts/query.sql"              # Source file path
dest_file = "deployed/query.sql"            # Destination path
git_branch = "main"                         # Target Git branch
commit_message = "Deploy SQL file via script"
repo_dir = os.getcwd()                      # Change if needed

# -------- Utility to run shell commands --------
def run_command(cmd, cwd=None):
    try:
        print(f"> Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=cwd, check=True, text=True, capture_output=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {' '.join(cmd)}")
        print(e.stderr)
        sys.exit(1)

# -------- Step 1: Copy the file --------
try:
    os.makedirs(os.path.dirname(dest_file), exist_ok=True)
    shutil.copy(src_file, dest_file)
    print(f"✅ Copied: {src_file} → {dest_file}")
except Exception as e:
    print(f"❌ File copy failed: {e}")
    sys.exit(1)

# -------- Step 2: Git operations --------

# Checkout branch
run_command(["git", "checkout", git_branch], cwd=repo_dir)

# Add file
run_command(["git", "add", dest_file], cwd=repo_dir)

# Commit
run_command(["git", "commit", "-m", commit_message], cwd=repo_dir)

# Push
run_command(["git", "push", "origin", git_branch], cwd=repo_dir)

print("🚀 Deployment completed successfully.")

