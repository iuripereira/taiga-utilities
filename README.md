# Taiga Utilities

## Description

Utilities script to access taiga rest API.

## Usage

`python3 main.py [action] [args]`

Actions:
    help: Show this text

    auth: Authenticate user
    get_tests: 
        -tests [FOLDER]: Path where tests are located
        -issues [FILE]: File with issues ids list
        -tests_result [FOLDER]: Folder to copy the tests
        -out [FILE]: File to save the results
    get_tests_titles: 
        -issues [FILE]: File with issues ids list
    get_types: 
        -issues [FILE]: File with issues ids list
    get_status: 
        -issues [FILE]: File with issues ids list
    get_issues_statuses:

    get_links: 
        -issues [FILE]: File with issues ids list
        -fbc [BOOLEAN]: Sets if add YES|NO at the end to indicate if has crash
        -coredumps_issues [PATH]: File with coredumps issues ids
    add_tag: 
        -issues [FILE]: File with issues ids list
        -groups [FILE]: File with issues groups
        -tag [STRING]: Tag to be added

