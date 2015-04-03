# ReChat
RethinkDB + Tornado Chat Demo

Using Async RethinDB Driver , with change feeds and Longpolling.
Change feeds makes 


#How it works
- When new chat message arrived it is inserted into ```events``` table RethinkDB automatically notify to the changfeed listeners.
- It makes massaging  persistant and scalable.
- No need to track previous messages cursors thanks to changefeeds.
- Better maintainability over combo of Queues and Database architectures.

> Tested with rethinkdb 2.0RC1 and tornado 4.1.0 . 
> Also included python rethinkdb drivers from latest commit for easy testing.

#Setup

``` bash
easy_install install tornado==4.1.0
#Or 
pip install tornado==4.1.0
```
#Running
```bash
python rechat.py
```