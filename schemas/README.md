# Schema source of truth

The Pydantic models in `src/ideaforge/models.py` are authoritative. Regenerate these JSON Schema files after a model change:

```powershell
python -m ideaforge export-schemas
```
