# pyle
 Self-host that pile of web articles / links you want to keep a copy for yourself. 

# The main story 

We all have some links to web content we would like to keep for ourselves, no
matter what happens to the original site. 

The idea of this app is to allow someone to self-host its own solution for
that. Some similar solutions are, e.g. pocket, wallabag. 

Two features are the most important for this solution: 

1) Provide a REST API to manage your links

2) Provide a telegram bot to allow an easy way to add new articles to your
collection. 

The bot could evolve in the future to fully interact with the app, and I also
am interested on using a Machine Learning classifier to auto-tag articles on
the future. 

# The architecture: 

- API SERVER: Serves the REST API to manage your collection. 

- FRONTEND SERVER: Serves a frontend API, which consumes the REST API. In the
  first version it will be an old-fashioned frontend stack, using Material UI.
Later on, there are plans to move it to React. 

- TELEGRAM BOT: A bot that can be used to post new links on your collection. It
  also consumes the REST API. 

# How to run the API Server

See [https://github.com/tiagoprn/pyle/tree/master/src/api].