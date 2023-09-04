![V1LeagueManager.png](static%2FV1LeagueManager.png)

## API Documentation
### Ports 


## Needs and Solutions

## Growth Opportunities

## Maintainability and Scalability

# Security

To ensure only authenticated users can access certain FastAPI endpoints, you can define a dependency to verify the user's token. This dependency can be used with any endpoint where you want to ensure the user is authenticated.

Here's how you can achieve this:

1. Define a function (dependency) that will verify the user's token:

```python
from fastapi import Depends, HTTPException, Request
from firebase_admin import auth

def get_current_user(token: str = Depends(get_token_from_request)):
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=403, detail="Invalid authentication credentials")

def get_token_from_request(request: Request):
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=401, detail="Token not provided")
    return token.split("Bearer ")[1]
```

2. Use this dependency in your endpoint:

```python
@app.get("/protected-data/")
async def get_protected_data(current_user: dict = Depends(get_current_user)):
    return {"data": "This is protected data!", "user": current_user}
```

3. When you call this endpoint, make sure to include the Firebase authentication token in the `Authorization` header in the format `Bearer YOUR_TOKEN_HERE`.

Here's how it works:

- The `get_token_from_request` function extracts the token from the `Authorization` header.
- The `get_current_user` function uses the extracted token to verify it against Firebase and if valid, returns the decoded token.
- If the token is not valid or some other exception occurs, a `HTTPException` is raised, which will stop the request and return the specified error to the client.
- By using `Depends(get_current_user)` in the endpoint, FastAPI ensures that this function runs before the actual endpoint logic. If the function returns without any issue, the endpoint logic runs; otherwise, the client sees the raised error.

This ensures only authenticated users with a valid token can access the endpoint.
