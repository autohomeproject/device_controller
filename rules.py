import time
import pg
from threading import Thread

class Action:
    def __init__(self, device_id, duration, value):
        self.device_id = device_id
        self.duration = duration
        self.value = value

    def getDeviceID(self):
        return self.device_id

    def generateDeviceName(self, con):
        q = con.query('select * from "devices" where "id"=' + str(self.device_id))
        r = q.dictresult()
        self.device_name = r[0]['name']

    def getDeviceName(self):
        return self.device_name

    def getDuration(self):
        return self.duration

    def getValue(self):
        return self.value

class Condition:
    C_EQUAL = 0
    C_LT = 1
    C_GT = 2

    def __init__(self, device_id, comparison, value):
        self.device_id = device_id
        self.comparison = comparison
        self.value = value

    def getDeviceID(self):
        return self.device_id

    def generateDeviceName(self, con):
        q = con.query('select * from "devices" where "id"=' + str(self.device_id))
        r = q.dictresult()
        self.device_name = r[0]['name']
        

    def getDeviceName(self):
        return self.device_name

    def getValue(self):
        return self.value

    def evaluateValue(self, value):
        result = False
        if self.comparison == self.C_EQUAL:
            if value == self.value:
                result = True
        elif self.comparison == self.C_GT:
            if value > self.value:
                result = True
        elif self.comparison == self.C_LT:
            if value < self.value:
                result = True
        return result


class ActionSet:
    def __init__(self, action_set_id):
        self.id = action_set_id
    
    def generateActionList(self, con):
        q = con.query('select * from "actions" where "action_set_id"=' + str(self.id))
        r = q.dictresult()
        self.actions = []
        for row in r:
            a = Action(row['device_id'], row['duration'], int(row['value']))
            a.generateDeviceName(con)
            self.actions.append(a)
    
    def execute(self, dl):
        for d in dl:
            for a in self.actions:
                if d.getName() == a.getDeviceName():
                    d.setValue(a.getValue())


class ConditionSet:
    def __init__(self, condition_set_id):
        self.id = condition_set_id

    def generateConditionList(self, con):
        q = con.query('select * from "conditions" where "condition_set_id"=' + str(self.id))
        r = q.dictresult()
        self.conditions = []
        for row in r:
            c = Condition(row['device_id'], row['comparison'], int(row['value']))
            c.generateDeviceName(con)
            self.conditions.append(c)

    def evaluate(self, dl):
        result = True
        for d in dl:
            for c in self.conditions:
                if d.getName() == c.getDeviceName() and c.evaluateValue(d.getValue()) == False:
                    #print "Hit!: " + d.getName() + " vs. " + c.getDeviceName()
                    result = False
        return result

class RuleSet:
    def __init__(self, rule_set_id):
        self.id = rule_set_id

    def generateIDs(self, con):
        q = con.query('select * from "rule_sets" where "id"=' + str(self.id))
        r = q.dictresult()
        self.condition_set_id = r[0]['condition_set_id']
        self.action_set_id = r[0]['action_set_id']

    def getConditionSet(self, con):
        q = con.query('select * from "condition_sets" where "id"=' + str(self.condition_set_id))
        r = q.dictresult()
        self.condition_set = ConditionSet(r[0]['id'])

    def getActionSet(self, con):
        q = con.query('select * from "action_sets" where "id"=' + str(self.action_set_id))
        r = q.dictresult()
        self.action_set = ActionSet(r[0]['id'])

    def execute(self, dl):
        cr = self.condition_set.evaluate(dl)
        if cr == True:
            self.action_set.execute(dl)
        return cr

class RuleSetTracker(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.con = pg.connect('autohome_development', 'menlohotels.com', 5432, None, None, 'autohome', 'autohome') 
        self.generateRuleSetList()

    def generateRuleSetList(self):
        q = self.con.query('select * from "rule_sets"')
        r = q.dictresult()
        rsl = []
        for row in r:
            #print "Processing row #" + str(row['id'])
            if row['active'] == 't':
                #print "HIT!!!"
                rset = RuleSet(row['id'])
                rset.generateIDs(self.con)
                rset.getConditionSet(self.con)
                rset.getActionSet(self.con)
                rset.condition_set.generateConditionList(self.con)
                rset.action_set.generateActionList(self.con)
                rsl.append(rset)
        self.rsl = rsl

    def evaluate(self, dl):
        if self.rsl == None:
            print "No rule sets!"
        else:
            for rset in self.rsl:
                rset.execute(dl)
    
    def run(self):
        while 1:
            print "Updating rulesets..."
            self.generateRuleSetList()
            print "Done updating rulesets!"
            time.sleep(4)


