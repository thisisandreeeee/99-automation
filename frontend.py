from flask import Flask
from flask_table import Table, Col

app = Flask(__name__)

class ItemTable(Table):
    time = Col('Timestamp')
    name = Col('Name')
    desc = Col('Description')

class Item(object):
    def __init__(self, time, name, desc):
        self.time = time
        self.name = name
        self.desc = desc

@app.route("/")
def main():
    f = open('debug.log', 'r')
    lst = list(f)[::-1]
    items = []
    for i in lst:
        if i == "#####":
            items.append('','','')
        else:
            try:
                log = i.split(";")
                items.append(Item(log[0], log[1], log[2]))
            except:
                pass

    table = ItemTable(items)
    return table.__html__()

if __name__ == "__main__":
    app.run()
