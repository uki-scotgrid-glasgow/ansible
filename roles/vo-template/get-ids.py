#! /usr/bin/env python

import glob, os, yaml


DIR_ANSIBLE = '/etc/ansible'
DIR_ROLES = os.path.join(DIR_ANSIBLE, 'roles')


# Get list of filenames of vars files to parse
def get_vars_files():
    results = []
    for role in os.listdir(DIR_ROLES):
        if role.startswith('vo-'):
            fn_dir = os.path.join(DIR_ROLES, role, 'defaults')
            os.chdir(fn_dir)
            results.extend((os.path.join(fn_dir, x) for x in glob.glob('*.yml')))
    return results


# Parse vars file to extract account information
def parse_vars_file(filename):
    results = []
    with open(filename, 'r') as f:
        # Parse YAML
        data = yaml.safe_load(f)

        # Omit files without entries
        if 'vo_accounts' not in data:
            return

        for x in data['vo_accounts']:
            # {'first_uid': 3001, 'gid': 3001, 'user_prefix': 'atlas', 'num_accounts': 10}
            results.append((filename, x['user_prefix'], x['gid'], x['first_uid'], x['num_accounts'], x['first_uid'] + x['num_accounts'] - 1))

    # (FILENAME, USERNAME PREFIX, GID, FIRST UID, NUMBER OF USERS, LAST UID)
    return results


# Get vars files and extract account information
results = []
for fn_vars in get_vars_files():
    parsed = parse_vars_file(fn_vars)
    if parsed is not None:
        results.extend(parsed)

# Find largest GID and UID
max_gid = 0
max_uid = 0
for (_, _, gid, _, _, uid) in results:
    if gid > max_gid:
        max_gid = gid
    if uid > max_uid:
        max_uid = uid

# Print account details
print('{0:12} {1:>6} {2:>6} {3:>6} {4:>6}'.format('Account', 'GID', 'UID0', 'UIDn', 'No.'))
print('')
for x in sorted(results, key = lambda tup: tup[-1]):
    print('{0:12} {1:6} {2:6} {3:6} {4:6}'.format(x[1], x[2], x[3], x[5], x[4]))
print('')
print('Last GID: {0}'.format(max_gid))
print('Last UID: {0}'.format(max_uid))
