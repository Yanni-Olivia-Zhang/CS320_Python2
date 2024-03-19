race_lookup = {
    "1": "American Indian or Alaska Native",
    "2": "Asian",
    "21": "Asian Indian",
    "22": "Chinese",
    "23": "Filipino",
    "24": "Japanese",
    "25": "Korean",
    "26": "Vietnamese",
    "27": "Other Asian",
    "3": "Black or African American",
    "4": "Native Hawaiian or Other Pacific Islander",
    "41": "Native Hawaiian",
    "42": "Guamanian or Chamorro",
    "43": "Samoan",
    "44": "Other Pacific Islander",
    "5": "White",
}

class Applicant:
    def __init__(self, age, race):
        self.age = age
        self.race = set()
        for r in race:
            if r in race_lookup:
                self.race.add(race_lookup[r])
    
    def __repr__(self):
        return "Applicant({}, {})".format(repr(self.age), sorted(list(self.race)))
    
    def lower_age(self):
        return int(self.age.replace("<", "").replace(">","").split("-")[0])
    
    def __lt__(self, other):
        return self.lower_age() < other.lower_age()
    
    
    
class Loan:
    def __init__(self, values):
        if values["loan_amount"] != "NA" and values["loan_amount"] != "Exempt":
            self.loan_amount = float(values["loan_amount"])
        else:
            self.loan_amount = -1
        if values["property_value"] != "NA" and values["property_value"] != "Exempt":
            self.property_value = float(values["property_value"])
        else:
            self.property_value = -1 
        if values["interest_rate"] != "NA" and values["interest_rate"] != "Exempt":
            self.interest_rate = float(values["interest_rate"])
        else:
            self.interest_rate = -1         

        self.applicants = []
        rklist = []
        rnlist = []
        for key in values:
            if key.startswith("applicant_race-"):
                rklist.append(key)
        for rk in rklist: 
            if values[rk] != "":
                rnlist.append(values[rk])
        self.applicants.append(Applicant(values["applicant_age"],rnlist))  
        
        if values["co-applicant_age"] != "9999":
            corklist = []
            cornlist = []
            for key in values:
                if key.startswith("co-applicant_race-"):
                    corklist.append(key)
            for rk in corklist: 
                if values[rk] != "":
                    cornlist.append(values[rk])
            self.applicants.append(Applicant(values["co-applicant_age"], cornlist))
            
    def __str__(self):
        return "<Loan: {}% on ${} with {} applicant(s)>".format(self.interest_rate, self.property_value,len(self.applicants))
         
    def __repr__(self):
        return "<Loan: {}% on ${} with {} applicant(s)>".format(self.interest_rate, self.property_value,len(self.applicants))

    def yearly_amounts(self, yearly_payment):
        assert self.interest_rate > 0 and self.loan_amount > 0
        amt = self.loan_amount

        while amt > 0:
            yield amt
            amt = amt * (self.interest_rate / 100 + 1)
            amt = amt - yearly_payment
        
import json 
import csv
from zipfile import ZipFile
from io import TextIOWrapper
        
class Bank:
    def __init__(self,name):
        f = open("banks.json")
        data = json.load(f)
        f.close()
        
        entry = None
        for d in data:
            if d["name"] == name:
                self.name = name
                entry = d
        self.lei = entry["lei"]
        
        with ZipFile('wi.zip') as zf:
            with zf.open("wi.csv", "r") as f:
                tio = TextIOWrapper(f)
                data = csv.DictReader(tio)
                loanlist = []
                for d in data:
                    if d["lei"] == self.lei:
                        loanlist.append(Loan(d))
        self.loanlist = loanlist
        
    def __getitem__(self,key):
        return self.loanlist[key]
    
    def __len__(self):
        return len(self.loanlist)
        
        