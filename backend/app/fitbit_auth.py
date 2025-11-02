"""
Fitbit OAuth 2.0 authentication service.
Handles authorization flow, token exchange, and token refresh.
"""

from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# Load Fitbit OAuth configuration
config = Config(environ=os.environ)

FITBIT_CLIENT_ID = os.getenv("FITBIT_CLIENT_ID")
FITBIT_CLIENT_SECRET = os.getenv("FITBIT_CLIENT_SECRET")
FITBIT_AUTHORIZE_URL = os.getenv("FITBIT_AUTHORIZE_URL", "https://www.fitbit.com/oauth2/authorize")
FITBIT_TOKEN_URL = os.getenv("FITBIT_TOKEN_URL", "https://api.fitbit.com/oauth2/token")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# OAuth scopes for Fitbit API
# See: https://dev.fitbit.com/build/reference/web-api/developer-guide/application-design/#Scopes
FITBIT_SCOPES = [
    "activity",      # Steps, distance, calories, active minutes
    "heartrate",     # Heart rate data and zones
    "sleep",         # Sleep duration and stages
    "profile",       # User profile information
]

# Initialize OAuth client
oauth = OAuth(config)
oauth.register(
    name='fitbit',
    client_id=FITBIT_CLIENT_ID,
    client_secret=FITBIT_CLIENT_SECRET,
    authorize_url=FITBIT_AUTHORIZE_URL,
    access_token_url=FITBIT_TOKEN_URL,
    client_kwargs={
        'scope': ' '.join(FITBIT_SCOPES),
        'token_endpoint_auth_method': 'client_secret_post',  # Required by Fitbit
    }
)


def generate_authorization_url(state: str = None) -> str:
    """
    Generate Fitbit OAuth authorization URL.
    
    Args:
        state (str): Optional state parameter for CSRF protection
    
    Returns:
        str: Authorization URL to redirect user to
    """
    redirect_uri = f"{BACKEND_URL}/api/fitbit/callback"
    
    params = {
        'client_id': FITBIT_CLIENT_ID,
        'response_type': 'code',
        'scope': ' '.join(FITBIT_SCOPES),
        'redirect_uri': redirect_uri,
    }
    
    if state:
        params['state'] = state
    
    # Build URL with parameters
    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    return f"{FITBIT_AUTHORIZE_URL}?{query_string}"


async def exchange_code_for_tokens(code: str) -> dict:
    """
    Exchange authorization code for access and refresh tokens.
    
    Args:
        code (str): Authorization code from Fitbit OAuth callback
    
    Returns:
        dict: Token response containing access_token, refresh_token, expires_in, user_id
    """
    import httpx
    
    redirect_uri = f"{BACKEND_URL}/api/fitbit/callback"
    
    data = {
        'client_id': FITBIT_CLIENT_ID,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
    }
    
    # Fitbit requires client_secret in the body, not Basic Auth
    auth = (FITBIT_CLIENT_ID, FITBIT_CLIENT_SECRET)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            FITBIT_TOKEN_URL,
            data=data,
            auth=auth,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to exchange code: {response.text}")
        
        return response.json()


async def refresh_access_token(refresh_token: str) -> dict:
    """
    Refresh an expired access token using the refresh token.
    Fitbit access tokens expire after 8 hours.
    
    Args:
        refresh_token (str): Refresh token from initial authorization
    
    Returns:
        dict: New token response with updated access_token and refresh_token
    """
    import httpx
    
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
    }
    
    auth = (FITBIT_CLIENT_ID, FITBIT_CLIENT_SECRET)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            FITBIT_TOKEN_URL,
            data=data,
            auth=auth,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to refresh token: {response.text}")
        
        return response.json()


def calculate_token_expiry(expires_in: int) -> datetime:
    """
    Calculate token expiration datetime.
    
    Args:
        expires_in (int): Seconds until token expires (typically 28800 = 8 hours)
    
    Returns:
        datetime: Expiration datetime
    """
    return datetime.utcnow() + timedelta(seconds=expires_in)


def is_token_expired(expires_at: datetime) -> bool:
    """
    Check if a token has expired or will expire soon.
    Adds 5-minute buffer to refresh before actual expiry.
    
    Args:
        expires_at (datetime): Token expiration datetime
    
    Returns:
        bool: True if token is expired or expires within 5 minutes
    """
    buffer = timedelta(minutes=5)
    return datetime.utcnow() + buffer >= expires_at
