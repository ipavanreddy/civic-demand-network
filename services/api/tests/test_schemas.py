from app import export_schemas


def test_exported_json_schemas_are_up_to_date():
    for path, text in export_schemas.rendered().items():
        assert path.exists(), f"missing {path}; run: uv run python -m app.export_schemas"
        assert path.read_text(encoding="utf-8") == text, f"stale {path.name}; run: uv run python -m app.export_schemas"
