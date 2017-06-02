### CHECKLIST

- [ ] There is no way to pass complex data on `keyboard.callback_data` 
      (tried with json.dumps(), a simple string with a '|' on it, and these didn't work). 
      So, Keep a record of the URLs that are entered on a local SQLite database  
      (`url`, `sqlite_id`, `created_at`, `saved_to_pile`) using peewee 
      for simplicity [http://docs.peewee-orm.com/en/latest/peewee/quickstart.html#working-with-existing-databases]()
  
- [ ] Add the code that will create the record on the pyle REST API on `on_callback_query`.  
