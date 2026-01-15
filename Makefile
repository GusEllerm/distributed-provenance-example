.PHONY: rocrate validate

rocrate:
	python3 scripts/generate_ro_crate.py

validate:
	python3 scripts/validate_metadata.py

