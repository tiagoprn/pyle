### CHECKLIST

- [ ] Add the code that will detect when an URL is entered on
  `on_callback_query` - I could try to download the page contents with
the `requests` library and see if it returns contents. It should be smart
enough to add `http/s` and `www` when an URL is entered (check if the requests
library doesn't do that by default). When something different from an URL is
entered, respond saying that only URLs are accepted.

- [ ] When a URL too long is entered (e.g. with marketing tracking parameters like from some newsletters), 
it should remove these marketing parameters to record the shortest URL possible. These parameters list should 
 be kept on a `const`, aside `BOT_TOKEN` (I could check my newsletters to get an initial list of this tracking parameters.) 

- [ ] Keep a record of the URLs that are entered on a local SQLite database  (`url`,
  `created_at`, `saved_to_pile`) using peewee for simplicity [http://docs.peewee-orm.com/en/latest/peewee/quickstart.html#working-with-existing-databases]()
  
- [ ] Add the code that will create the record on the pyle REST API on `on_callback_query`.  
