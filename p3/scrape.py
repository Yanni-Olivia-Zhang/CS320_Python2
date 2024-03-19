# project: p3
# submitter: yzhang2232
# partner: none
# hours: 6

import os
import pandas as pd
import time
import requests
from selenium.common.exceptions import NoSuchElementException


class GraphScraper:
    def __init__(self):
        self.visited = set()
        self.order = []

    def go(self, node):
        raise Exception("must be overridden in sub classes -- don't change me here!")

    def dfs_search(self, node):
        self.visited.clear()
        self.order.clear()
        return self.dfs_visit(node)

    def dfs_visit(self, node):
        if node in self.visited:
            return
        self.visited.add(node)
        self.order.append(node)
        chilist = self.go(node)
        for chi in chilist:
            self.dfs_visit(chi)
            
    def bfs_search(self, node):
        self.visited.clear()
        self.order.clear()
        return self.bfs_visit(node)
    
    def bfs_visit(self, node):
        self.visited.add(node)
        self.order.append(node)
        queue = [node]
        while len(queue) > 0:
            curr = queue.pop(0)
            chilist = self.go(curr)
            for child in chilist:
                if not child in self.visited:
                    queue.append(child)
                    self.visited.add(child)
                    self.order.append(child)
            
class MatrixSearcher(GraphScraper):
    def __init__(self, df):
        super().__init__()
        self.df = df

    def go(self, node):
        children = []
        for node, has_edge in self.df.loc[node].items():
            if has_edge:
                children.append(node)
        return children
    
    
class FileSearcher(GraphScraper):
    def __init__(self):
        super().__init__()
    
    def go(self, node):
        children = []
        with open(os.path.join('file_nodes/', node)) as f:
            r = f.read()
            child = r.split("\n")[1].split(",")
            for chi in child:
                children.append(chi)
        return children
    
    def message(self):
        msg = ""
        for i in self.order:
            with open(os.path.join('file_nodes/', i)) as f:
                r = f.read()
                msg += r.split('\n')[0]
        return msg
        
    
class WebSearcher(GraphScraper):
    def __init__(self, driver):
        super().__init__()
        self.driver = driver
        
    def go(self, node):
        children = []
        self.driver.get(node)
        self.dfs = pd.read_html(self.driver.page_source)
        child_tbl = self.driver.find_element(value = "Pages")
        urls = child_tbl.find_elements(by = 'tag name', value = "a")
        for url in urls:
            children.append(url.get_attribute("href"))
        return children
   
    def table(self):
        data_frames = []
        for node in self.order:
            self.go(node)
            data_frames.append(self.dfs[0])
        df = pd.concat(data_frames, ignore_index = True)
        return df
    
    
def reveal_secrets(driver, url, travellog):
    password = ''
    for i in travellog["clue"].items():
        password += str(i[1])
    driver.get(url)
    search = driver.find_element(value = "password")
    botton = driver.find_element(value = "attempt-button")
    search.send_keys(password)
    botton.click()
    loc_botton = driver.find_element(value = "securityBtn")
    loc_botton.click()
    attempts = 15
    for _ in range(attempts):
        try:
            pic = driver.find_element(value = "image")
            pic_url = pic.get_attribute("src")
            break
        except NoSuchElementException:
            time.sleep(0.2)
    # copied from https://www.adamsmith.haus/python/answers/how-to-download-an-image-using-requests-in-python#:~:text=Use%20requests.,write%2Dand%2Dbinary%20mode.
    r = requests.get(pic_url)
    file = open("Current_Location.jpg", "wb")
    file.write(r.content)
    file.close()
    cur_loc = driver.find_element(value = "location").text
    return cur_loc

    
        
        
        
        
        