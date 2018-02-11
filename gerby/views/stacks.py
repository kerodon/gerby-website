import hashlib

from flask import render_template

from gerby.gerby import app
from gerby.database import *
import gerby.views.tag

# we need this for building GitHub URLs pointing to diffs
@app.context_processor
def md5_processor():
  def md5(string):
    m = hashlib.md5()
    m.update(string.encode("utf-8"))
    return m.hexdigest()

  return dict(md5=md5)


@app.route("/tags")
def show_tags():
  return render_template("single/tags.html")


@app.route("/acknowledgements")
def show_acknowledgements():
  return render_template("single/acknowledgements.html")


@app.route("/tag/<string:tag>/history")
def show_history(tag):
  if not gerby.views.tag.isTag(tag):
    return render_template("tag.invalid.html", tag=tag)

  try:
    tag = Tag.get(Tag.tag == tag)
  except Tag.DoesNotExist:
    return render_template("tag.notfound.html", tag=tag)

  breadcrumb = gerby.views.tag.getBreadcrumb(tag)
  neighbours = gerby.views.tag.getNeighbours(tag)

  # only show history for tags for which we have one
  if tag.type not in ["definition", "example", "exercise", "lemma", "proposition", "remark", "remarks", "situation", "theorem"]:
    return render_template("tag.history.invalid.html", tag=tag, breadcrumb=breadcrumb)

  changes = Change.select().where(Change.tag == tag) # TODO eventually order by Commit.time, once it's in there
  for change in changes:
    change.hash.time = change.hash.time.decode("utf-8").split(" ")[0] # TODO why in heaven's name is this returning bytes?!

  # this means something went wrong
  if len(changes) == 0:
    return render_template("tag.history.empty.html", tag=tag, breadcrumb=breadcrumb)

  return render_template("tag.history.html",
                         tag=tag,
                         changes=changes,
                         breadcrumb=breadcrumb,
                         neighbours=neighbours)

