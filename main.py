import requests
import json
import urllib
import urllib.request
import os
import json
import getpass
import sys

conf_file = "settings.conf"
conf = None

ISSUES_STATUSES = "issue-statuses"
ISSUES_PATH = "issues/"
AUTH_PATH = "auth"

def saveConf():
    global conf_file
    global conf
    
    lines = []
    for key, value in conf.items():
        lines.append(key + "=" + value + "\n")
        
    myfile = open(conf_file, 'w')
    myfile.writelines(lines)

def readConf():
    if os.path.exists(conf_file):
        conf = {}
        for line in open(conf_file, 'r'):
            key, value = line.replace("\n", "").split("=")
            conf[key] = value
            
        return conf
            
    return None

def initConf():
    global conf
    global conf_file
    
    conf = {}
    
    conf["rest_api_url"] = input('Rest api URL: ')
    conf["issues_link"] = input('Issues link: ')
    
    conf["token"] = ""
    
    auth(conf)
    saveConf()
    
    return readConf()

def auth(data=None):
    global conf
    global conf_file
    
    email = input('Email: ')
    password = getpass.getpass('Password: ')
    
    auth_data = {'username' : email, 'type' : 'normal', 'password': password}
    headers={'Content-type': 'application/json'}
    
    r = requests.post(data["rest_api_url"] + AUTH_PATH, json=auth_data, headers=headers)
    
    if (r.status_code == 200):
        conf["token"] = json.loads(r.text)["auth_token"]
        saveConf()
        return

    print(r.text)
    print("Authentication failed.")
    
    sys.exit(1)

'''
 Get params
'''
def getParams():
    global conf
    global data
    
    ACTIONS = (["auth", "help", "get_tests", "get_tests_titles", "get_types",
            "get_status", "get_links", "get_issues_statuses", "get_tags", "add_tag", "get_opened_issues", "get_closed_issues"])
    
    data = {}
    
    data["action"] = None
    
    if (len(sys.argv) < 2):
        print("Action not provided")
        usage()
        
        return None
    else:
        data["action"] = str(sys.argv[1])
        
        for i in range(2, len(sys.argv)):
            current = str(sys.argv[i])
            if (current.startswith("-")):
                if (len(sys.argv) < i + 1):
                    usage()
                    return None
                data[current[1:]] = str(sys.argv[i + 1])
                i = i + 1
    
    if (data["action"] is None or not data["action"] in ACTIONS):
        print("Action not provided")
        usage()
        return None

    conf = readConf()

    if (conf is None):
        conf = initConf()

    data["token"] = conf["token"]
    data["rest_api_url"] = conf["rest_api_url"]
    data["issues_link"] = conf["issues_link"]

    return data

'''
 Get links from a issues list
'''
def getLinks(data):
    mylist1 = []
    coredumps = []
    issue = ""
    toAppend = ""
    result = ""
    filter_by_coredumps = data["fbc"]

    if (filter_by_coredumps):
        for line in open(data["coredumps_issues"],'r'):
	        issue = line.replace('\n'	, '')
	        coredumps.append(issue)

    for line in open(data["issues"],'r'):
        issue = line.replace('\n', '')
        toAppend = '=HYPERLINK("' + data["url"] + issue + '";"' + issue + '")'

        if filter_by_coredumps:
            if (issue in coredumps):
        	    toAppend = toAppend + "\tYES\n"
        	    coredumps.remove(issue)
            else:
        	    toAppend = toAppend + "\tNO\n"
        else:
            toAppend = toAppend + "\n"

        result = result + toAppend

    print(result)

def addTagToIssue(data, issue):
    url = data["rest_api_url"] + ISSUES_PATH + str(issue["id"])
    tags = issue["tags"]
    
    token = data["token"]
    tag = data["tag"]
    
    if (tag in tags):
        return True
    
    tags.append(tag)
    
    json_data = {'tags': tags, 'version': issue["version"]}
    headers={'Content-type': 'application/json', 'Authorization': 'Bearer ' + token}
    
    r = requests.patch(url, json=json_data, headers=headers)
    
    if (r.status_code != 200):
        print("Status code: ", r.status_code)
        print("       Text: ", r.text)
        
        return False
    
    return True
    
'''
 Get links from a issues list
'''
def addTag(data):
    total = 0
    i = 0
    
    groups = set()
    
    for line in open(data["groups"],'r'):
        line = line.replace('\n'	, '')
        lineSplit = line.split("\t")
        
        if (lineSplit[2] == "NO"):
            groups.add(lineSplit[0])
            total += int(lineSplit[1])
    
    for line in open(data["issues"],'r'):
        line = line.replace('\n', '')
        lineSplit = line.split("\t")
        
        issue_number = lineSplit[0]
        group = lineSplit[4]
        
        if (group in groups):
            i = i + 1
            issue = getIssue(data, issue_number)
            
            if (not addTagToIssue(data, issue)):
                break
        
        print("\r" + str(i) + "/" + str(total), end="\r")


def getIssue(data, issue_number):
    url = data["rest_api_url"] + ISSUES_PATH + 'by_ref?ref=' + issue_number + "&project=6"
    req = urllib.request.Request(url)
    req.add_header('Content-Type', 'application/json')
    req.add_header('Authorization', 'Bearer ' + data["token"])
    
    response = urllib.request.urlopen(req)
    return json.loads(response.read().decode('utf-8'))
    

'''
 Get type from a individual issue
'''
def getIssueType(issue_number, token):
    url = data["rest_api_url"] + ISSUES_PATH + 'by_ref?ref=' + issue_number + "&project=6"
    req = urllib.request.Request(url)
    req.add_header('Content-Type', 'application/json')
    req.add_header('Authorization', 'Bearer ' + token)
    
    response = urllib.request.urlopen(req)
    data = json.loads(response.read().decode('utf-8'))
    subject = data['subject']
    subjectSplit = subject.split("'")
    
    return subjectSplit[2].strip().upper()

'''
Get tags from issues list
'''
def getTags(data):

    for line in open(data["issues"], 'r'):
        line = line.replace('\n', '')
        
        issue_data = getIssue(data, line)
        to_print = ""
        
        for tag in issue_data["tags"]:
            to_print = tag + ","
            
        print(to_print[:-1] if len(to_print) else to_print)


'''
 Get type from taiga issues
'''
def getIssuesTypes(data):
    total = sum(1 for line in open(data["issues"]))
    i = 1

    types = set()
    result = ""

    for line in open(data["issues"],'r'):
        line = line.replace('\n'	, '')
        
        i = i + 1
        
        lineSplit = line.split("\t")
        
        issue = lineSplit[0]
        i_type = getIssueType(issue, data["token"])
        
        types.add(i_type)
        
        toAppend = ('=HYPERLINK("' + data["url"] + issue + '";"'
                + issue + '")\t'
                + i_type + "\n")

        result = result + toAppend
        
        print("\r" + str(i) + "/" + str(total), end="\r")

    print("\rTypes: \n" + str(types))

    print("\nResult:\n" + result)

def requesIssuesStatuses(data):
    url = data["rest_api_url"] + ISSUES_STATUSES + "?project=6"
    req = urllib.request.Request(url)
    req.add_header('Content-Type', 'application/json')
    req.add_header('Authorization', 'Bearer ' + data["token"])


    response = urllib.request.urlopen(req)
    return json.loads(response.read().decode('utf-8'))

'''
 Get status from taiga issues
'''
def getIssuesStatus(data):
    total = sum(1 for line in open(data["issues"]))
    i = 1

    statuses = requesIssuesStatuses(data)
    statuses_dict = {}
    for status in  statuses:
        statuses_dict[status["id"]] = status["name"].upper()

    types = set()
    result = ""

    for line in open(data["issues"],'r'):
        line = line.replace('\n'	, '')
        
        i = i + 1
        
        lineSplit = line.split("\t")
        
        issue_id = lineSplit[0]
        issue_data = getIssue(data, issue_id)
        
        print(statuses_dict[issue_data["status"]])

'''
 Get available statuses from taiga issues
'''
def getIssuesStatuses(data):
    statuses = requesIssuesStatuses(data)
    
    for status in  statuses:
        print(status["id"], "=", status["name"])


'''
 Get tests titles from a issues list
'''
def getTestsTitles(data):
    report = []
    
    total = sum(1 for line in open(data["issues"]))
    i = 1

    for line in open(data["issues"], 'r'):
        line = line.replace('\n', '')
        
        req = urllib.request.Request(data["rest_api_url"] + ISSUES_PATH + 'by_ref?ref=' + line + "&project=6")
        req.add_header('Content-Type', 'application/json')
        req.add_header('Authorization', 'Bearer ' + data["token"])
        
        response = urllib.request.urlopen(req)
        
        _data = json.loads(response.read().decode('utf-8'))
        
        print(_data['subject'])

'''
 Get tests folders from a issues list
'''
def getTests(data):
    tests_result_folder = data["tests_result"]
    if not os.path.exists(tests_result_folder):
        os.mkdir(tests_result_folder)

    report = []
    
    total = sum(1 for line in open(data["issues"]))
    i = 1

    for line in open(data["issues"],'r'):
        line = line.replace('\n', '')
        
        req = urllib.request.Request(data["rest_api_url"] + ISSUES_PATH + 'by_ref?ref=' + line + "&project=6")
        req.add_header('Content-Type', 'application/json')
        req.add_header('Authorization', 'Bearer ' + data["token"])
        
        response = urllib.request.urlopen(req)
        
        _data = json.loads(response.read().decode('utf-8'))
        
        subject = _data['subject']
        
        subjectSplit = subject.split("'")
        
        subjectSplit2 = subjectSplit[1].split("_")
        
        if (len(subjectSplit2) < 1):
            print ("error at issue", line)
            print ("subjectSplit2:", subjectSplit2)
            sys.exit()
        
        app_path = subjectSplit2[0] + "/" + subjectSplit[1]
        
        cmd = ["cp", "-r", app_path, tests_result_folder]
        p = subprocess.Popen(cmd)
        p.wait()
        
        report.append(line + "=" + app_path + "\n")
        
        print(str(i) + "/" + str(total))
        i = i + 1


    myfile = open(tests_result_folder + data["out"],'w')
    myfile.writelines(report)

def getOpenedIssues(data):
    url = data["rest_api_url"] + "issues?status__is_closed=false&project=6"
    req = urllib.request.Request(url)
    req.add_header('Content-Type', 'application/json')
    req.add_header('Authorization', 'Bearer ' + data["token"])
    req.add_header('x-disable-pagination', 'True')

    response = urllib.request.urlopen(req)
    result = json.loads(response.read().decode('utf-8'))

    myfile = open(data["out"], 'w')

    lines = []
    lines.append("ID\tTitulo\tCriador\tResponsável\tStatus\tSeveridade\tPrioridade\tTipo\tis_closed\ttags\twatchers\tdata_criacao\tdata_modificacao\tdata_finalizacao\n")
    for n in result:
        username = ""
        if n["assigned_to"]:# and n["assigned_to"] != "None":
            username = str(n['assigned_to_extra_info']["username"])
        lines.append('\t'.join([str(n['ref']), str(n['subject']), str(n['owner_extra_info']['username']), username, str(n['status_extra_info']['name']), str(n['severity']), str(n['priority']), str(n['type']), str(n['is_closed']), str(n['tags']), str(n['watchers']), str(n['created_date']), str(n['modified_date']), str(n['finished_date'])]) + "\n")
    
    myfile.writelines(lines)
    myfile.close()

def getClosedIssues(data):
    url = data["rest_api_url"] + "issues?status__is_closed=true&project=6"
    req = urllib.request.Request(url)
    req.add_header('Content-Type', 'application/json')
    req.add_header('Authorization', 'Bearer ' + data["token"])
    req.add_header('x-disable-pagination', 'True')

    response = urllib.request.urlopen(req)
    result = json.loads(response.read().decode('utf-8'))

    myfile = open(data["out"], 'w')

    lines = []
    lines.append("ID\tTitulo\tCriador\tResponsável\tStatus\tSeveridade\tPrioridade\tTipo\tis_closed\ttags\twatchers\tdata_criacao\tdata_modificacao\tdata_finalizacao\n")
    for n in result:
        username = ""
        if n["assigned_to"]:# and n["assigned_to"] != "None":
            username = str(n['assigned_to_extra_info']["username"])
        lines.append('\t'.join([str(n['ref']), str(n['subject']), str(n['owner_extra_info']['username']), username, str(n['status_extra_info']['name']), str(n['severity']), str(n['priority']), str(n['type']), str(n['is_closed']), str(n['tags']), str(n['watchers']), str(n['created_date']), str(n['modified_date']), str(n['finished_date'])]) + "\n")
    
    myfile.writelines(lines)
    myfile.close()

def usage(data=None):
    print("Usage: ")
    print("python3 main.py [action] [args]")
    print("Actions:")
    
    print("    help: Show this text\n")
    
    print("    auth: Authenticate user")
    
    print("    get_tests: ")
    print("        -tests [FOLDER]: Path where tests are located")
    print("        -issues [FILE]: File with issues ids list")
    print("        -tests_result [FOLDER]: Folder to copy the tests")
    print("        -out [FILE]: File to save the results")
    
    print("    get_tests_titles: ")
    print("        -issues [FILE]: File with issues ids list")
    
    print("    get_types: ")
    print("        -issues [FILE]: File with issues ids list")
    
    print("    get_status: ")
    print("        -issues [FILE]: File with issues ids list")
    
    print("    get_issues_statuses:\n")
    
    print("    get_links: ")
    print("        -issues [FILE]: File with issues ids list")
    print("        -fbc [BOOLEAN]: Sets if add YES|NO at the end to indicate if has crash")
    print("        -coredumps_issues [PATH]: File with coredumps issues ids")
    
    print("    get_tags: ")
    print("        -issues [FILE]: File with issues ids list")
    
    print("    add_tag: ")
    print("        -issues [FILE]: File with issues ids list")
    print("        -groups [FILE]: File with issues groups")
    print("        -tag [STRING]: Tag to be added")

    print("    get_closed_issues: ")
    print("        -out [FILE]: File to save the results")

    print("    get_opened_issues: ")
    print("        -out [FILE]: File to save the results")


def main():
    data = getParams()
    
    if (not data is None):
        functions = {
            "auth": auth,
            "help": usage,
            "get_tests": getTests,
            "get_types" : getIssuesTypes,
            "get_status" : getIssuesStatus,
            "get_issues_statuses" : getIssuesStatuses,
            "get_links" : getLinks,
            "get_tags": getTags,
            "add_tag" : addTag,
            "get_tests_titles": getTestsTitles,
            "get_closed_issues": getClosedIssues,
            "get_opened_issues": getOpenedIssues
        }
        
        functions[data["action"]](data)
        
        return True    
    else:
        return False

if __name__ == '__main__':
    if (main()):
        sys.exit(0)
    else:
        sys.exit(1)


