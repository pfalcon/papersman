papersman
=========

`papersman` is a simple, minimalist tag-based manager for electronic
documents, papers, etc. It's based on the following ideas:

1. Primary way to store document (meta)information is in human-readable
   structured format (subset of YAML), contained in files side-by-side
   with actual documents. Currently, `papersman` doesn't use any database.
   It may come as a way to cache metadata at later (much later) time, but
   on a typical modern system, just scanning YAML files should scale well
   to a few thousand of documents, which should be well enough for a
   personal collection.
2. Based on the above, the primary way to check and update metadata is
   with your text editor. `papersman` provides (or will provide) support
   commands for actions which aren't convenient/practical to do manually
   (e.g., rename a tag across all documents).
3. `papersman` uses hash of file contents to identify a file. This will
   allow to keep (or restore) document-metadata association across file
   rename of the original document.
4. For more advanced UI needs, `papersman` uses web browser as a frontend.
   And currently, it just generates static HTML files for per-tag document
   indexes, which you can use locally, send to anyone, or deploy to any
   web server. At later time, it's expected that a simple webapp for more
   advanced querying (e.g. boolean combinations of tags) will be written.


`papersman` is primarily developed and used with
[Pycopy](https://github.com/pfalcon/pycopy), a minimalist Python dialect.
Given that CPython is forward-compatible with Pycopy (by installing Pycopy
API modules), it can also be used with CPython (or another Python
implementation).


License
-------

`papersman` is written and maintained by Paul Sokolovsky. It's available
under the MIT license.
