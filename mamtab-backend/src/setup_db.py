import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
SCHEMA_PATH = BASE_DIR.parent / 'PostgreSQL.sql'

DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_NAME = os.environ.get('DB_NAME', 'gtfs_db')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'root')


class SetupError(RuntimeError):
	pass


def split_sql_statements(script: str) -> list[str]:
	statements = []
	buffer = []
	in_single_quote = False
	in_dollar_quote = False
	i = 0

	while i < len(script):
		if not in_single_quote and script.startswith('--', i):
			newline_index = script.find('\n', i)
			if newline_index == -1:
				break
			i = newline_index + 1
			continue

		if not in_single_quote and not in_dollar_quote and script.startswith('/*', i):
			comment_end = script.find('*/', i + 2)
			if comment_end == -1:
				raise SetupError('Commento SQL non chiuso in PostgreSQL.sql')
			i = comment_end + 2
			continue

		if script.startswith('$$', i) and not in_single_quote:
			in_dollar_quote = not in_dollar_quote
			buffer.append('$$')
			i += 2
			continue

		char = script[i]
		if char == "'" and not in_dollar_quote:
			in_single_quote = not in_single_quote
			buffer.append(char)
			i += 1
			continue

		if char == ';' and not in_single_quote and not in_dollar_quote:
			statement = ''.join(buffer).strip()
			if statement:
				statements.append(statement)
			buffer = []
			i += 1
			continue

		buffer.append(char)
		i += 1

	statement = ''.join(buffer).strip()
	if statement:
		statements.append(statement)

	return statements

def ensure_database(admin_conn):
	with admin_conn.cursor() as cur:
		cur.execute('SELECT 1 FROM pg_database WHERE datname = %s', (DB_NAME,))
		if cur.fetchone():
			print(f'Database {DB_NAME} già presente.')
			return

		cur.execute(f'CREATE DATABASE "{DB_NAME}"')
		print(f'Database {DB_NAME} creato.')


def normalize_schema_script(script: str) -> str:
	lines = []
	for line in script.splitlines():
		if line.strip() == 'CREATE DATABASE gtfs_db;':
			continue
		lines.append(line)
	return '\n'.join(lines)


def apply_schema():
	if not SCHEMA_PATH.is_file():
		raise SetupError(f'Schema SQL non trovato: {SCHEMA_PATH}')

	with SCHEMA_PATH.open(encoding='utf-8') as f:
		script = normalize_schema_script(f.read())

	statements = split_sql_statements(script)

	with psycopg2.connect(
		host=DB_HOST,
		database=DB_NAME,
		user=DB_USER,
		password=DB_PASSWORD,
	) as conn:
		conn.autocommit = False
		with conn.cursor() as cur:
			cur.execute('CREATE SCHEMA IF NOT EXISTS public;')
			cur.execute('SET search_path TO public;')
			for statement in statements:
				cur.execute(statement)
		conn.commit()

	print('Schema applicato con successo.')


def main():
	print('\n=== PostgreSQL setup ===')
	print(f'Host:     {DB_HOST}')
	print(f'App DB:   {DB_NAME}')
	print(f'User:     {DB_USER}')
	print()

	with psycopg2.connect(
		host=DB_HOST,
		database=DB_USER,
		user=DB_USER,
		password=DB_PASSWORD,
	) as admin_conn:
		admin_conn.autocommit = True
		ensure_database(admin_conn)

	apply_schema()
	print('\nSetup completato.')


if __name__ == '__main__':
	try:
		main()
	except Exception as e:
		print(f'\n❌ Setup fallito: {e}')
		raise
