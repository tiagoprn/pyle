# How to run the API Server

    $ cd src
    $ pip install -r requirements.txt (please do this on a virtualenv)
    $ cd api
    $ python manage.py migrate
    $ python manage.py createsuperuser (this user will be used to login to the API, which will support permissions on a few iterations on the future).
    $ python manage.py runserver

Access ```http://localhost:8000/``` to get a WebUI to navigate through the API. Then, click on  "login", on the upper right, and use the credentials you entered at ```createsuperuser``` above.
To post a link, e.g.: 

    http://localhost:8000/links/
    
This way you can post a link and also create its corresponding tags, if they do not exist. 

On this UI, you must go down below and click on "Raw data", to be able to post the tags and the link simultaneously. 

Below are examples of the full payload to POST a link, creating its corresponding tags: 

    {
        "uri": "http://link1.com",
        "name": "link1",
        "notes": "",
        "content": "",
        "content_last_updated_at": null,
        "tags": [{"name": "first"}, {"name": "second"}]
    }
    
    {
        "uri": "http://go.now.com",
        "name": "gonow",
        "notes": "",
        "content": "",
        "content_last_updated_at": null,
        "tags": [{"name": "first"}, {"name": "third"}]
    }

Then, click the "POST" button. If successful it will post the JSON of the created resource, otherwise check the errors shown on the response payload.
    
**NOTE: If you try both payloads above, you will see the second one fails (because its trying to recreate the tag "first", and this aparently is not being handled by the LinkSerializer). I'm working on it.**


## How to get a token to make api calls: 

    $ curl -X POST -H "Content-Type: application/json" -d '{"username":"tiago","password":"MYPASSWORDHERE"}' http://localhost:8000/api-token-auth/
    
## How to verify if a token is valid: 
    
    $ curl -X POST -H "Content-Type: application/json" -d '{"token":"MY_GIANT_TOKEN_HERE"}' http://localhost:8000/api-token-verify/
    
## Manually create a token: (must be added as a management command in the future)

http://getblimp.github.io/django-rest-framework-jwt/#creating-a-new-token-manually

## How to access a protected resource: 

    $ curl -iX POST -H "Authorization: JWT [YOUR-GIANT-JWT-TOKEN-HERE]" -H "Content-Type: application/json" -d '{"name":"awesome"}' http://localhost:8000/tags

