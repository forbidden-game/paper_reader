# Paper Reader CLI commands

.PHONY: paper-init paper-discover paper-add paper-list paper-search paper-show paper-update-status paper-delete

paper-init:
	@cd paper_reader && uv run python -m paper_reader.main init

paper-discover:
	@cd paper_reader && uv run python -m paper_reader.main discover $(if $(DAYS),--days $(DAYS)) $(if $(MAX),--max-results $(MAX))

paper-add:
	@cd paper_reader && uv run python -m paper_reader.main add $(ARXIV_ID)

paper-list:
	@cd paper_reader && uv run python -m paper_reader.main list

paper-search:
	@cd paper_reader && uv run python -m paper_reader.main "$(QUERY)"

paper-show:
	@cd paper_reader && uv run python -m paper_reader.main show $(PAPER_ID)

paper-update-status:
	@cd paper_reader && uv run python -m paper_reader.main update-status $(PAPER_ID) $(STATUS)

paper-delete:
	@cd paper_reader && uv run python -m paper_reader.main delete $(PAPER_ID)

# Aliases for convenience
paper-init-interests: paper-init
paper-find: paper-discover

# Development commands
.PHONY: install check test

install:
	uv sync

check:
	uv run ruff check .
	uv run pyright .

test:
	uv run pytest tests/ -v
