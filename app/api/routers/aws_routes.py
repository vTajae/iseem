from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.aws_dependencies import get_aws_s3_service
from app.api.dependencies.quickbooks_dependencies import get_quickbooks_service
from app.api.models.User import User
from app.api.schemas.quickbooks.quickbooks_TransactionList import QuickBooksQueryParams
# Adjust import path as needed
from app.api.services.aws_service import AWSS3Service
from app.api.services.quickbooks_service import QuickBooksService
from app.utils.utils import paginate_data

router = APIRouter()


# @router.get("/quickbooks/{report_type}")
# async def get_quickbooks_report(
#     request: Request,
#     report_type: str,
#     query_params: QuickBooksQueryParams = Depends(),
#     service: QuickBooksService = Depends(get_quickbooks_service),
#     user: User = Depends(get_current_user),
#     aws_s3_service: AWSS3Service = Depends(get_aws_s3_service),
#     ):
    
#     access_token = request.cookies.get("access_token")  # Retrieve access token from cookies

#     # Fetch full data from QuickBooks using the provided access token
#     full_data = await service.make_quickbooks_report_request(report_type, query_params.dict(), access_token, user.id)
    
#     print(full_data)
#     if not full_data:
#         raise HTTPException(status_code=404, detail="Report data not found.")

#     # Generate a unique file name for the report

#     file_name = f"{report_type}_{datetime.utcnow().strftime('%Y-%m-%dT%H-%M-%S')}.json"
    
#     # Upload the report data to AWS S3
#     try:
#         await aws_s3_service.upload_json_to_s3( object_name=file_name, data=full_data)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to upload report to AWS S3: {str(e)}")
    
#     parsed_report = service.parse_quickbooks_report(full_data)
#     paginated_response = paginate_data(
#         parsed_report, query_params.page, query_params.limit)
#     return paginated_response


@router.post("/upload-to-s3/{object_name}")
async def upload_to_s3(object_name: str, data: dict, aws_s3_service: AWSS3Service = Depends(get_aws_s3_service)):
    await aws_s3_service.upload_json_to_s3(object_name=object_name, data=data)
    return {"message": "Upload successful"}


@router.get("/quickbooks/{report_type}")
async def get_quickbooks_report(
    request: Request,
    report_type: str,
    query_params: QuickBooksQueryParams = Depends(),
    service: QuickBooksService = Depends(get_quickbooks_service),
    user: User = Depends(get_current_user),
    aws_s3_service: AWSS3Service = Depends(get_aws_s3_service),

):
    # # Retrieve the access token from cookies, or use None to refresh the token
    access_token = request.cookies.get("access_token")

    custom_params = query_params.get_custom_params()

    print(custom_params, "custom_params")

    #  Fetch full data from QuickBooks using the provided access token
    full_data = await service.make_quickbooks_report_request(report_type, custom_params, access_token, user.id)

    # print(full_data)
    if not full_data:
        raise HTTPException(status_code=404, detail="Report data not found.")

    # Generate a unique file name for the report
    
    file_name = f"{report_type}_{datetime.utcnow().strftime('%Y-%m-%dT%H-%M-%S')}.json"

    # Upload the report data to AWS S3
    try:
        await aws_s3_service.upload_json_to_s3(object_name=file_name, data=full_data)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to upload report to AWS S3: {str(e)}")

    parsed_report = service.parse_quickbooks_report(full_data, report_type)
    paginated_response = paginate_data(
        parsed_report, query_params.page, query_params.limit)
    return paginated_response
