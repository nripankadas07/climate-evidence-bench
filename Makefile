.PHONY: test demo golden check

test:
	PYTHONPATH=src python3 -m unittest discover -s tests -v

demo:
	PYTHONPATH=src python3 -m climate_evidence_bench demo --emit-jsonl --output-dir reports

golden:
	PYTHONPATH=src python3 -m climate_evidence_bench demo --emit-jsonl --output-dir artifacts/demo

check:
	python3 -m compileall -q src tests
