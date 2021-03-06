from fastapi import APIRouter, Depends
from fastapi import FastAPI
from starlette.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from starlette.requests import Request
from starlette.routing import request_response, Route
import uvicorn


from fastapi_aad_auth import __version__, AADAuth, AuthenticationState

auth_provider = AADAuth()

router = APIRouter()

@router.get('/hello')
async def hello_world(auth_state:AuthenticationState=Depends(auth_provider.api_auth_scheme)):
    print(auth_state)
    return {'hello': 'world'}


if 'untagged' in __version__ or 'unknown':
    API_VERSION = 0
else:
    API_VERSION = __version__.split('.')[0]


async def homepage(request):
    if request.user.is_authenticated:
        return PlainTextResponse('Hello, ' + request.user.display_name)
    return HTMLResponse(f'<html><body><h1>Hello, you</h1><br></body></html>')


@auth_provider.auth_required()
async def test(request):
    if request.user.is_authenticated:
        return PlainTextResponse('Hello, ' + request.user.display_name)
 
routes = [
    Route("/", endpoint=homepage),
    Route("/test", endpoint=test)
]
              

app = FastAPI(title='fastapi_aad_auth test app',
              description='Adding Azure Active Directory Authentication for FastAPI',
              version=__version__,
              openapi_url=f"/api/v{API_VERSION}/openapi.json",
              docs_url='/api/docs',
              swagger_ui_init_oauth=auth_provider.api_auth_scheme.init_oauth,
              redoc_url='/api/redoc',
              routes=routes)

app.include_router(router)

auth_provider.configure_app(app)



if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', debug=True, port=8000)
