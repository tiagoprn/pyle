- [ ] Add the code that will detect when an URL is entered on
  `on_callback_query` - I could try to download the page contents with
the `requests` library and see if it returns contents. It should be smart
enough to add `http/s` and `www` when an URL is entered (check if the requests
library doesn't do that by default). When something different from an URL is
entered, respond saying that only URLs are accepted.
- [ ] Keep a record on a local SQLite database the URLs that are entered (url,
  created_at, saved_to_pile)
  (http://pythoncentral.io/introductory-tutorial-python-sqlalchemy/)
- [ ] Add the code that will create the record on the pyle REST API on
  `on_callback_query`.  
