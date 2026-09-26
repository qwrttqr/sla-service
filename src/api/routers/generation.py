import io
import zipfile

from fastapi import APIRouter, Query
from fastapi.responses import Response

from core.services.generation.generator import (
    generate_engineer_rows,
    generate_request_rows,
)
from core.services.generation.csv_exporter import (
    engineers_to_csv,
    requests_to_csv,
)

router = APIRouter(prefix="/generate", tags=["generation"])


@router.get("/dataset.zip")
def generate_dataset_zip(
    engineers_count: int = Query(12, ge=1, le=50),
    requests_count: int = Query(80, ge=1, le=200),
):
    engineers_csv = engineers_to_csv(generate_engineer_rows(engineers_count))
    requests_csv = requests_to_csv(generate_request_rows(requests_count))

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("engineers.csv", engineers_csv)
        zf.writestr("requests.csv", requests_csv)

    return Response(
        content=buf.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="dataset.zip"'},
    )