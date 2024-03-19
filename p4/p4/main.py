# project: p4
# submitter: yzhang2232
# partner: none
# hours: 10

# Data adapted from https://www.kaggle.com/datasets/padhmam/qs-world-university-rankings-2017-2022


import pandas as pd
import flask
from flask import Flask, request, jsonify
import re
import time
from io import StringIO, BytesIO
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')


app = Flask(__name__)
df = pd.read_csv("main.csv")

visit = 0
def count():
    global visit
    visit += 1

dona_count = {"A":0,"B":0}    

@app.route('/')
def home():
    global visit
    global dona_count
    count()
    with open("index.html") as f:
        html = f.read()
    if visit <= 10:
        if visit % 2 == 1:
            html = html.replace("?from=A","?from=B")
            html = html.replace("blue","red")
        return html
    else:
        if dona_count["A"] >= dona_count["B"]:
            return html
        else:
            html = html.replace("?from=A","?from=B")
            html = html.replace("blue","red")
            return html      


@app.route('/browse.html')
def browse():
    global df
    df_str = df.to_html()
    html = "<html><body bgcolor = 'lightgrey'><h1><b>Browse</b></h1>{}</body</html>".format(df_str)
    return html

last_visit = 0
addr_dict = {}

@app.route('/browse.json')
def jsonify_to_dict():
    global last_visit
    global df
    global addr_dict
    ip_addr = request.remote_addr
    df_dict = df.to_dict(orient = "index")
    
    if ip_addr not in addr_dict:
        last_visit = time.time()
        addr_dict[ip_addr] = last_visit
        return jsonify(df_dict)
    else:
        if time.time()-last_visit < 60:
            return flask.Response("too many requests", status=429,
                              headers={"Retry-After": "60"})
        else:
            return jsonify(df_dict)

@app.route('/email', methods=["POST"])
def email():
    email = str(request.data, "utf-8")
    if re.match(r"\w+@\w+\.\w+", email): # 1
        with open("emails.txt", "a") as f: # open file in append mode
            f.write(email + "\n") 
        with open("emails.txt", "r") as f:
            num_subscribed = len(f.readlines())
        return jsonify(f"thanks, you're subscriber number {num_subscribed}!")
    return jsonify("you entered invalid email address, please try again!") # 3

@app.route('/donate.html')
def donate():
    html = '''
    <html><body bgcolor="lightblue">
    <h3>Please help this little "start-up" webpage by donating one dollar :)</h3>
    </body></body>
    </html>
    '''
    global dona_count
    args = dict(flask.request.args)
    key = args.get("from")
    if key != None:
        dona_count[key] += 1 
    return html

@app.route("/plot1.svg")
def plot1_svg():
    fig, ax = plt.subplots(figsize=(12,7))
    global df
    if dict(flask.request.args).get("legend") == "size":
        # color scatter plot by categories
        # adapted from https://www.statology.org/matplotlib-scatterplot-color-by-value/
        groups = df.groupby("size")
        for name, group in groups:
            plt.plot(group.score,group.student_faculty_ratio, marker = "o",
            linestyle="",label = name)
        # change legend order
        # adapted from https://www.statology.org/matplotlib-legend-order/
        ax.set_title("Scattor Plot of Ranking Score vs. Student-Faculty-Ratio (Colored by Size)")
        handles, labels = plt.gca().get_legend_handles_labels()
        order = [2,1,0,3]
        plt.legend([handles[idx] for idx in order],[labels[idx] for idx in order])
    else:
        plt.scatter(df["score"],df["student_faculty_ratio"])
        ax.set_title("Scattor Plot of Ranking Score vs. Student-Faculty-Ratio")
    ax.set_xlabel("Score")
    ax.set_ylabel("Student-faculty-ratio")
    
    f = StringIO() 
    plt.tight_layout()
    fig.savefig(f, format="svg")
    plt.close()
    
    svg = f.getvalue()
    
    hdr = {"Content-Type": "image/svg+xml"}
    return flask.Response(svg, headers=hdr)


@app.route("/plot2.svg")
def plot2_svg():
    fig, ax = plt.subplots(figsize=(12,7))
    global pd
    df["country"].hist(ax=ax, orientation = "horizontal")
    ax.set_xlabel("Numbers")
    ax.set_ylabel("Country")
    ax.set_title("Histogram of Countries Having Top 400 University")
    
    f = StringIO()
    plt.tight_layout()
    fig.savefig(f, format="svg")
    plt.close()
    
    svg = f.getvalue()
    
    hdr = {"Content-Type": "image/svg+xml"}
    return flask.Response(svg, headers=hdr)


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=False) # don't change this line!

# NOTE: app.run never returns (it runs for ever, unless you kill the process)
# Thus, don't define any functions after the app.run call, because it will
# never get that far.