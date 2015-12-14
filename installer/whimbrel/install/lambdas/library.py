

def join_libraries(l_dict, *libraries):
    for gen_type in ['product', 'unit-tests', 'integration-tests']:
        for key in ['copy-files', 'copy-dirs', 'tokenized']:
            for library in libraries:
                if key in library[gen_type]:
                    if key not in l_dict[gen_type]:
                        l_dict[gen_type][key] = []
                    l_dict[gen_type][key].extend(library[gen_type][key])
        for key in ['npm', 'exec']:
            for library in libraries:
                if key in library[gen_type]:
                    if key not in l_dict[gen_type]:
                        l_dict[gen_type][key] = []
                    for val in library[gen_type][key]:
                        if val not in l_dict[gen_type][key]:
                            l_dict[gen_type][key].append(val)
        for key in ['user-overrides']:
            for library in libraries:
                if key in library:
                    if key not in l_dict[gen_type]:
                        l_dict[gen_type] = {}
                    for k, v in library[gen_type][key]:
                        if k not in l_dict[gen_type][key]:
                            l_dict[gen_type][key][k] = v
    return l_dict
