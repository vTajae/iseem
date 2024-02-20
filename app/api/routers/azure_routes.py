from datetime import datetime
from fastapi import APIRouter, Depends, Request, HTTPException
from app.api.services.azure_service import AzureBlobService
from app.api.schemas.quickbooks.quickbooks_TransactionList import QuickBooksQueryParams
from app.api.models.User import User
from app.api.services.quickbooks_service import QuickBooksService
from app.api.dependencies.azure_dependencies import get_azure_blob_service, get_azure_service
from app.api.dependencies.quickbooks_dependencies import get_quickbooks_service
from app.api.dependencies.auth import get_current_user

router = APIRouter()

@router.get("/quickbooks/{report_type}")
async def get_quickbooks_report(
    request: Request,
    report_type: str,
    query_params: QuickBooksQueryParams = Depends(),
    service: QuickBooksService = Depends(get_quickbooks_service),
    user: User = Depends(get_current_user),
    azure_blob_service: AzureBlobService = Depends(get_azure_service)
):
    access_token = request.cookies.get("access_token")
    full_data = await service.make_quickbooks_report_request(report_type, query_params.dict(), access_token, user.id)
    if not full_data:
        raise HTTPException(status_code=404, detail="Report data not found.")

    blob_name = f"QuickBooksReports/{report_type}_{datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')}.json"
    await azure_blob_service.upload_blob(blob_name, full_data)
    
    return {"message": f"{report_type} uploaded successfully"}

    # Processing and response logic...
