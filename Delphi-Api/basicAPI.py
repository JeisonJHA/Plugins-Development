import sublime
import re

clean_name = re.compile(
    '^\s*(public\s+|private\s+|protected\s+|static\s+|procedure\s+' +
    '|function\s+|def\s+|Shortint\s+|Integer\s+|Longint\s+|Byte\s+' +
    '|Word\s+|Boolean\s+|WordBool\s+|LongBool\s+|ByteBool\s+|Real\s+' +
    '|Single\s+|Double\s+|Extended\s+|Comp\s+|String\s+|Char\s+|Length\s+' +
    '|Upcase\s+|textbackground\s+|textcolor\s+|gotoxy\s+|crt\s+|clrscr\s+' +
    '|readkey\s+|read\s+|readln\s+|class procedure\s+|class function\s+' +
    '|property\s+|constructor\s+|destructor\s+)+', re.I)


clean_name_private = re.compile('^\s*()+', re.I)


def GetMethodRegion(view):
    for region in view.sel():
        region_row, region_col = view.rowcol(region.begin())
        function_regions = view.find_by_selector(
            'meta.function.parameters')
        if function_regions:
            for r in (function_regions):
                row, col = view.rowcol(r.begin())
                if row >= region_row:
                    return r


def GetMethodType(view):
    for region in view.sel():
        region_row, region_col = view.rowcol(region.begin())
        function_regions = view.find_by_selector('storage.type.function')
        if function_regions:
            for r in reversed(function_regions):
                row, col = view.rowcol(r.begin())
                if row <= region_row:
                    lines = view.substr(r).splitlines()
                    name = clean_name.sub('', lines[0])
                    s = name.strip()
                    s = s.split(".")[0]

                    return s


def GetName(view, metodo, new=False):
    for region in view.sel():
        region_row, region_col = view.rowcol(region.begin())
        function_regions = view.find_by_selector('meta.function')
        if function_regions:
            for r in reversed(function_regions):
                row, col = view.rowcol(r.begin())
                if row <= region_row:
                    pos = 0
                    lines = view.substr(r).splitlines()
                    if (len(lines[0].split(".")) > 1 and
                            lines[0].split(".")[1] == ''):
                        pos = 1

                    name = clean_name.sub('', lines[pos])

                    s = name.strip()
                    if not metodo:
                        s = s.split(".")[0]
                    else:
                        if (len(s.split(".")) > 1):
                            s = s.split(".")[1]
                        s = s.split("(")[0]
                        if s.find(':') >= 0:
                            s = s.split(":")[0]

                        if s.find(';') >= 0:
                            s = s.split(";")[0]
                    if (len(GetMethodRegions(view, s)) == 1) and not new:
                        continue
                    return s, r


def GetMethodRegions(view, method):
    result = []
    for symbol in view.symbols():
        if method == symbol[1]:
            result.append(symbol[0])
    return result


def GetMethodDeclaration(view, region, metodo):
    # for region in view.sel():
    region_row, region_col = view.rowcol(region.begin())
    function_regions = view.find_by_selector('meta.function')
    if function_regions:
        for r in reversed(function_regions):
            row, col = view.rowcol(r.begin())
            if row <= region_row:

                lines = view.substr(r).splitlines()
                name = clean_name.sub('', lines[0])
                s = name.strip()
                if (len(s.split(".")) > 1):
                    s = s.split(".")[1]
                s = s.split("(")[0]
                if s.find(':') >= 0:
                    s = s.split(":")[0]

                if s.find(';') >= 0:
                    s = s.split(";")[0]
                # print('s:%s' % s)
                # print('metodo:%s' % metodo)
                if s == metodo:
                    return r


def GetReturnType(view, region_method, method_with_params):
    if method_with_params:
        # nRegion_Parmeters_Begin = view.find("\(", region_method.begin())
        # nRegion_Parmeters_End = view.find("\)", region_method.begin())

        nRegion_ReturnType_Begin = view.find("\)\:", region_method.begin())
        # print('nRegion_ReturnType_Begin:%s' % nRegion_ReturnType_Begin)
        # print('region_method.b:%s' % region_method.b)
        if (nRegion_ReturnType_Begin.a > region_method.b or
                nRegion_ReturnType_Begin.empty()):
            return GetReturnType(view, region_method, False)

        nRegion_ReturnType_End = view.find(
            ";", nRegion_ReturnType_Begin.begin())

        region_type = sublime.Region(
            nRegion_ReturnType_Begin.begin(), nRegion_ReturnType_End.end())
        word_region = view.word(region_type)
        word = view.substr(word_region).strip()
        word = word.split(":")[1].split(" ")[1].split(";")[0]
        return word, region_type
    else:
        nRegion_ReturnType_Begin = view.find("\:", region_method.begin())

        nRegion_ReturnType_End = view.find(
            ";", nRegion_ReturnType_Begin.begin())
        region_type = sublime.Region(
            nRegion_ReturnType_Begin.begin(), nRegion_ReturnType_End.end())

        method_region = view.full_line(region_method)
        lines = view.substr(method_region).splitlines()
        # print('lines:%s' % lines)
        name = clean_name.sub('', lines[0])
        s = name.strip()
        nRegion_ReturnType_Begin = s.find(":")
        s = s.split(":")[1].split(" ")[1].split(";")[0]
        return s, region_type


def GetParams(params):
    variable_name = []
    # print('params:%s' % params)
    if (params != []):
        size = len(params)
        i = 0
        for i in range(size):
            next_comma = params[i].find(',')
            next_semicolon = params[i].find(';')
            if ((next_comma != -1) and (next_comma > next_semicolon) and
                    (next_semicolon != -1)):
                next_position = params[i].find(':')
                if next_position == -1:
                    next_position = next_comma
            else:
                next_position = next_comma
            # print('next_comma: %s' % next_comma)
            # print('next_semicolon: %s' % next_semicolon)
            # print('next_position: %s' % next_position)
            # print('params[i]: %s' % params[i])
            if (next_position > 0):
                variable = params[i][0:len(params[i])]
                variable_name.append(variable[0:next_position])
                DefineParams(variable, variable_name)
            elif (params[i].find(':') > 0):
                variable = params[i][0:params[i].find(':')]
                variable_name.append(variable)
                if (params[i].find(';') > 0):
                    DefineParams(
                        params[i][params[i].find(';') + 1:len(params[i])],
                        variable_name)

    return variable_name


def DefineParams(variable, variables):
    control = False
    next_comma1 = variable.find(',')
    next_semicolon1 = variable.find(';')
    if (next_comma1 > next_semicolon1) and (next_semicolon1 != -1):
        next_position1 = next_semicolon1
        if next_position1 == -1:
            next_position1 = next_comma1
    else:
        next_position1 = next_comma1

    if (next_position1 > 0):
        next_variable = variable[next_position1 + 1:len(variable)]
    else:
        next_variable = variable

    next_comma = next_variable.find(',')
    next_semicolon = next_variable.find(';')
    next_colon = next_variable.find(':')
    if ((next_comma < next_semicolon) and (next_comma != -1) or
            (next_semicolon == -1)):
        if (next_comma > 0):
            variable_end = next_variable.find(',')
        else:
            if (next_colon > 0):
                control = True
                variable_end = next_variable.find(':')
            else:
                variable_end = len(next_variable)
    else:
        if (next_colon > 0):
            control = True
            variable_end = next_variable.find(':')
        else:
            variable_end = len(next_variable)

    variables.append(next_variable[0:variable_end])

    if ((next_variable.find(',') > 0) or
            (next_variable[0:variable_end].find(':') > 0) or
            (next_semicolon > 0)):
        if control:
            next_variable = next_variable[
                next_variable.find(';') + 1:len(next_variable)]

        DefineParams(next_variable, variables)


def GetParametersName(view, region_method):
    regiaodometodo = view.full_line(region_method)
    lines = view.substr(regiaodometodo).splitlines()
    name = clean_name.sub('', lines[0])
    s = name.strip()
    if (len(s.split("(")) <= 1):
        return ''

    nRegion_Parmeters_Begin = view.find("\(", region_method.begin())
    nRegion_Parmeters_End = view.find("\)", region_method.begin())
    regions = [
        sublime.Region(nRegion_Parmeters_Begin.begin(),
                       nRegion_Parmeters_End.end())]
    for region in regions:
        region_row, region_col = view.rowcol(region.begin())
        function_regions = view.find_by_selector(
            'meta.function.parameters')
        if function_regions:
            for r in (function_regions):
                r_begin = r.begin()
                r_end = r.end()
                region_method_begin = region_method.begin()
                region_method_end = region_method.end()

                if ((region_method_begin < r_begin) and
                        (region_method_end > r_end)):
                    row, col = view.rowcol(r.begin())
                    if row >= region_row:
                        lines = view.substr(r).splitlines()
                        name = []
                        size = len(lines)
                        i = 0
                        for i in range(size):
                            lines[i] = re.sub(
                                'var\s+|const\s+|out\s+|\s*', '', lines[i])
                            if (lines[i] != ''):
                                name.append(lines[i])
                        return name
    return []


def GetParameters(view, region_method):
    regiaodometodo = view.full_line(region_method)
    lines = view.substr(regiaodometodo).splitlines()
    name = clean_name.sub('', lines[0])
    s = name.strip()
    if (len(s.split("(")) <= 1):
        return

    nRegion_Parmeters_Begin = view.find("\(", region_method.begin())
    nRegion_Parmeters_End = view.find("\)", region_method.begin())
    regions = [
        sublime.Region(nRegion_Parmeters_Begin.begin(),
                       nRegion_Parmeters_End.end())]
    # print('regiaodoparametro:%s' % view.substr(regions))
    for region in regions:
        region_row, region_col = view.rowcol(region.begin())
        function_regions = view.find_by_selector(
            'meta.function.parameters')
        if function_regions:
            for r in (function_regions):
                r_begin = r.begin()
                r_end = r.end()
                region_method_begin = region_method.begin()
                region_method_end = region_method.end()

                if ((region_method_begin < r_begin) and
                        (region_method_end > r_end)):
                    row, col = view.rowcol(r.begin())
                    if row >= region_row:
                        lines = view.substr(r)
                        return lines
    return []


def GetClassName(owner, view):

    def dothing(owner):
        regions = view.find_by_selector(
            'entity.name.class')
        print('regions:%s' % regions)
        # Test if all results are for the same location
        # If they are, don't give a option, just go there
        # first_abs_path = None
        # Display options in quick panel
        display_options = []
        for region in regions:
            row, col = view.rowcol(region.begin())
            print('view.full_line(r):%s' % view.substr(view.full_line(region)))
            display_options.append(view.window().extract_variables()[
                'file'] + ':' + str(row))

        if len(display_options) == 1:
            # on_done(owner, display_options[0])
            print('regions:%s' % regions)
            print('view.substr(view.full_line(display_options[0])):%s' %
                  view.substr(view.full_line(regions[0])).strip().split("=")[0])
            return view.substr(view.full_line(regions[0])).strip().split("=")[0].strip()

        # Display options in quick panel
        # display_options = []
        # for option in options:
        #     display_options.append(option[1] + ':' + str(option[2][0]))
        view.window().show_quick_panel(
            items=display_options,
            on_select=on_done,
            on_highlight=lambda f: on_highlight(owner, display_options)
        )

    def on_done(option):
        """
        Open the specified file on the correct line number.
        """
        print('option:%s' % option)
        if option == -1:
            return
        if isinstance(option, int) or option.isdigit():
            option = self.options[option]
            print('option:%s' % str(option))
            file_path = option[0] + ':' + str(option[2][0])
        else:
            file_path = option
            print('file_path:%s' % file_path)
        self.view.window().open_file(file_path, sublime.ENCODED_POSITION)

    def on_highlight(self, option):
        """
        Preview the specified file on the correct line number.
        """
        print('option:%s' % option)
        option = self.options[option]
        print('passou aqui')
        file_path = option[0] + ':' + str(option[2][0])
        self.view.window().open_file(
            file_path,
            sublime.ENCODED_POSITION | sublime.TRANSIENT
        )

    return dothing(owner)
    # region = sublime.Region(0, view.size())
    # region_class = view.find("= class", region.begin())
    # if region_class.empty():
    #     return ''
    # regiaodaclasse = view.full_line(region_class)

    # lines = view.substr(regiaodaclasse).splitlines()
    # name = clean_name.sub('', lines[0])
    # s = name.strip()
    # s = s.split("=")[0]
    # s = s.split(" ")[0]
    # return s


def GetMethodRegionsWithParams(view, method, parameters):
    result = []
    for symbol in view.symbols():
        if method == symbol[1]:
            method_region = GetMethodDeclaration(
                view, symbol[0], symbol[1])
            # print('method_region:%s' % method_region)
            methods_params = "".join(
                GetParametersName(view, method_region))
            if (methods_params == parameters):
                result.append(method_region)
    return result


def GetDeclarationRegion(view, word):
    for region in view.sel():
        region_row, region_col = view.rowcol(region.begin())
        function_regions = view.find_by_selector('keyword.control')
        if function_regions:
            for r in function_regions:
                row, col = view.rowcol(r.begin())
                if row <= region_row:
                    lines = view.substr(r).splitlines()
                    name = clean_name_private.sub('', lines[0])
                    s = name.strip()
                    if s == word:
                        return r


def PegarParametrosForaDoPadrao(variable, parametros_com_tipo):
    if ((parametros_com_tipo != []) and (not (parametros_com_tipo is None))):
        text_size = len(variable)
        vaiable_size = len(parametros_com_tipo)
        parametros_errados = []

        settings = sublime.load_settings('delphi.sublime-settings')
        validador = settings.get("validador", {})
        # print(variable)
        # print(parametros_com_tipo)
        i = 0
        j = 0
        for i in range(text_size):
            for j in range(vaiable_size):
                if (parametros_com_tipo[j].find(variable[i]) > -1):
                    if (parametros_com_tipo[j].find(';') > -1):
                        end_pos = parametros_com_tipo[j].find(';')
                    else:
                        end_pos = len(parametros_com_tipo[j])
                    type_param = parametros_com_tipo[j][
                        parametros_com_tipo[j].find(':') + 1:end_pos]

                    # print('type_param: %s' % type_param)
                    # print('variable: %s' % variable[i])

                    if type_param.upper() in validador:
                        key = type_param.upper()
                        if (variable[i][0:len(validador[key])].lower() !=
                                validador[key].lower()):
                            parametros_errados.append(variable[i])
                    else:
                        key = 'ELSE'
                        if (variable[i][0:len(validador[key])].lower() !=
                                validador[key].lower()):
                            parametros_errados.append(variable[i])

                    # for key in validador:
                    #     if (type_param.upper() == key):
                    #         if (variable[i][0:len(validador[key])].lower() != validador[key].lower()):
                    #             parametros_errados.append(variable[i])
                    #             break
                    #     else:
                    #         if key == 'ELSE' and (variable[i][0:len(validador[key])].lower() != validador[key].lower()):
                    #             parametros_errados.append(variable[i])
                    #             break
    return parametros_errados


def ShowObjectMethod(obj):
    methodList = [method for method in dir(obj) if callable(
        getattr(obj, method))]
    processFunc = (
        lambda s: " ".join(s.split())) or (lambda s: s)
    print("\n".join(["%s %s" %
                     (method.ljust(10),
                      processFunc(str(getattr(obj, method).__doc__)))
                     for method in methodList]))
