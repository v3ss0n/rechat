#!/usr/bin/env python
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging
import tornado.escape
import tornado.ioloop
import tornado.web
import os.path
import uuid
import rethinkdb as r
from tornado.concurrent import Future
from tornado import gen
from tornado.options import define, options, parse_command_line
r.set_loop_type("tornado")
define("port", default=8080, help="run on the given port", type=int)
define("debug", default=False, help="run in debug mode")
conn = r.connect("localhost")
evt = r.db("rechat").table("events")

class MainHandler(tornado.web.RequestHandler):

    @gen.coroutine
    def get(self):
        con = yield conn
        curs = yield evt.run(con)
        messages = []
        while (yield curs.fetch_next()):
            item = yield curs.next()
            messages.append(item)

        self.render("index.html", messages=messages)


class MessageNewHandler(tornado.web.RequestHandler):

    @gen.coroutine
    def post(self):
        con = yield conn
        message = {
            "body": self.get_argument("body")
        }
        # to_basestring is necessary for Python 3's json encoder,
        # which doesn't accept byte strings.
        messages = (yield evt.insert(message, durability="soft").run(con))
        message['id'] = messages['generated_keys'][0]
        message["html"] = tornado.escape.to_basestring(
            self.render_string("message.html", message=message))
        if self.get_argument("next", None):
            self.redirect(self.get_argument("next"))
        else:
            self.write(message)


class MessageUpdatesHandler(tornado.web.RequestHandler):

    @gen.coroutine
    def post(self):
        con = yield conn
        curs = yield evt.changes().run(con)

        while (yield curs.fetch_next()):
            feed = yield curs.next()
            message = {'id': feed['new_val']['id'], 'html': tornado.escape.to_basestring(
                self.render_string("message.html", message=feed['new_val']))}
            break

        self.finish(dict(messages=[message]))


def main():
    parse_command_line()
    app = tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"/a/message/new", MessageNewHandler),
            (r"/a/message/updates", MessageUpdatesHandler),
        ],
        cookie_secret="_asdfasdaasdfasfas",
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        xsrf_cookies=True,
        debug=options.debug,
    )
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
