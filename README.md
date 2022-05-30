# Currency exchange calculator

1. `pip install requirements.txt`
2. Create a database
3. Put database URL to `DB_URL` environment variable, for example: `export DB_URL=postgres://postgres@localhost/currency_example`
4. Bring db schema up to date: `aerich upgrade`
5. Load initial data: `python import_initial_data.py <path/to/exchange.csv>`
6. Run dev server `uvicorn src.app:app --reload`
7. Visit http://127.0.0.1:8000/docs and explore API

TODO: Add more tests
