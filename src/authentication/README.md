# Auth App
This app handles authentication and csrf tokens
> Remember to precede every request with either one of following API host urls
```
API_HOST 
https://api.massenergize.org/
https://api.massenergize.com/
https://apis.massenergize.org/
https://apis.massenergize.com/
```

# POST  REQUESTS

##### Post SignIn Credentials
```
auth/sign-in
auth/signin
auth/login
```

# GET REQUESTS
#### Get CSRF token for a form/page
```
auth/csrf
```
When making a post request to the backend, you need to call this route first
Here is an example:
```javascript
fetch(`${API_HOST}/auth/csrf`, {
      method: 'GET',
      credentials: 'include',
    }).then(response => response.json()).then(jsonResponse => {
      const { csrfToken } = jsonResponse.data;
      return fetch(`${API_HOST}/user/myactualdestinationurl`, {
        credentials: 'include',
        method: 'POST',
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        body: dataToSend
      })
        .then(response => {
          console.log(response);
          return response.json();
        }).then(data => {
          console.log(data);
        });
    });
```