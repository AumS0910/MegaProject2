@echo off
python -m uvicorn api.trifold_brochure_api:app --host 0.0.0.0 --port 8007 --reload
