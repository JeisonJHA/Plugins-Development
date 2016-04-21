import sublime
import sublime_plugin
import re

clean_name = re.compile('^\s*(public\s+|private\s+|protected\s+|static\s+|procedure\s+|function\s+|def\s+|Shortint\s+|Integer\s+|Longint\s+|Byte\s+|Word\s+|Boolean\s+|WordBool\s+|LongBool\s+|ByteBool\s+|Real\s+|Single\s+|Double\s+|Extended\s+|Comp\s+|String\s+|Char\s+|Length\s+|Upcase\s+|textbackground\s+|textcolor\s+|gotoxy\s+|crt\s+|clrscr\s+|readkey\s+|read\s+|readln\s+|property\s+|)+', re.I)

clean_name_private = re.compile('^\s*()+', re.I)


class ExtractMethodCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        print("Extract Method")
        self.filterValidClasses()

        self.addMethod(edit)

    def filterValidClasses(self):
        view = self.view
        selector = view.find_by_selector
        self.method_regions = selector('function.implementation.delphi')
        self.methoddeclaration = selector('meta.function.delphi')
        self.classdefinition = selector('entity.class.interface.delphi')
        self.class_name_region = selector('entity.name.section.delphi')
        exclude_list = []
        for s in self.classdefinition:
            rowa, _ = self.view.rowcol(s.a)
            rowb, _ = self.view.rowcol(s.b)
            rowbb = rowb - 1
            if (rowa == rowb) or (rowa == rowbb):
                exclude_list.append(s)

        for r in exclude_list:
            self.classdefinition.remove(r)

        exclude_name_list = []
        for r in exclude_list:
            for s in self.class_name_region:
                if r.contains(s):
                    exclude_name_list.append(s)

        for r in exclude_name_list:
            self.class_name_region.remove(r)

    def addMethod(self, edit):
        v = self.view
        self.cursor_region = v.sel()[0]
        cursor_region = self.cursor_region
        word_region = v.word(cursor_region)
        word = v.substr(word_region).strip()
        amount_selected_row = word.count('\n') + 1

        line, ptinicio = self.getValidPosition()
        # Class where the method will be included
        self.classdefinition = [
            s for s in self.classdefinition if s.contains(cursor_region)]

        method_region = [
            s for s in self.method_regions if cursor_region.intersects(s)]

        methoddeclarationfiltered = [
            s for s in self.methoddeclaration if s.intersects(method_region[0])]

        class_name = self.getClassName()

        selection_text = v.substr(word_region).splitlines()
        params = self.getParametersName(methoddeclarationfiltered[0])
        variables = self.getVariablesMethod(self.getViewSel(cursor_region))
        print('variables:%s' % variables)
        print('params:%s' % params)

        return

        selection_text, variable, variable_on_text = self.getObject(
            self.getViewSel(cursor_region))

        parametros = ''
        if variable != [] and not (variable is None):
            parametros = '('
            for var in variable:
                parametros += var
            if parametros[len(parametros) - 1:len(parametros)] == ';':
                parametros = parametros[0:len(parametros) - 1]
            parametros += ')'
        v.insert(edit, ptinicio, 'procedure ' +
                 class_name + '.ExtractedMethod' + parametros + ';' + '\n')

        line_begin = line + 1
        pt = v.text_point(line_begin, 0)
        v.insert(edit, pt, 'begin' + ' \n')

        line_text = line_begin + 1
        pt = v.text_point(line_text, 0)
        word_region = self.getViewSel(v.sel()[0])

        method_body = ''
        for text in selection_text:
            method_body += text + '\n'
        v.insert(edit, pt, '  ' + method_body + ' \n')

        linha_end = line_text + 0 + amount_selected_row
        pt = v.text_point(linha_end, 0)
        v.insert(edit, pt, 'end;' + ' \n')

        params_declare = ''
        if (variable_on_text != []) and not (variable_on_text is None):
            params_declare = '('
            params_lenght = len(variable_on_text)
            k = 0
            for k in range(params_lenght):
                # print(k, params_lenght)
                if (k == (params_lenght - 1)):
                    divisor = ''
                else:
                    divisor = ', '
                params_declare += variable_on_text[k] + divisor
            params_declare += ')'

        v.replace(
            edit, word_region, '\n  ExtractedMethod' + params_declare + '; \n')

        linha, _ = v.rowcol(word_region.begin())

        ptnovo = v.text_point(linha, 2)

        selection_region = v.sel()[0]
        word_region = v.word(selection_region)
        v.sel().subtract(word_region)
        v.sel().add(ptnovo)

        self.addHeadMethod(edit, parametros)

        self.filter(edit, '')

    def getValidPosition(self):
        v = self.view

        def DisregardingCommentStartingBlock(line):

            line_decreases = True
            comment_previous_line = False
            while line_decreases:
                ptinicio = v.text_point(line, 0)
                comment_block_regions = v.find_by_selector(
                    'comment.block')

                if comment_block_regions:
                    for r in comment_block_regions:
                        ptinicio = v.text_point(line, 0)
                        if (((r.begin() < ptinicio) and (r.end() > ptinicio)) or
                                (r.begin() == ptinicio)):
                            ptinicio, line = self.lineDecreases(r, line)
                            comment_previous_line = True
                        else:
                            line_decreases = False

                comment_line_regions = v.find_by_selector(
                    'comment.line.double-slash')
                if comment_line_regions:
                    for r in comment_line_regions:
                        linha, _ = v.rowcol(r.begin())
                        ptinicio = v.text_point(line, 0)
                        if (((r.begin() < ptinicio) and (r.end() > ptinicio)) or
                                (r.begin() == ptinicio)):
                            ptinicio, line = self.lineDecreases(r, line)
                            comment_previous_line = True
                        else:
                            line_decreases = False
                else:
                    break

            if not comment_previous_line:
                line += 1
                ptinicio = v.text_point(line, 0)
            return line, ptinicio

        method_regions = v.find_by_selector(
            'function.implementation.delphi')
        next_method_region = [
            s for s in method_regions if self.cursor_region.end() < s.begin()]

        if next_method_region:
            line, _ = v.rowcol(next_method_region[0].begin())
            line -= 1
        else:
            next_method_region = v.find_by_selector(
                'implementation.block.delphi')
            line, _ = v.rowcol(next_method_region[0].end())

        return DisregardingCommentStartingBlock(line)

    def getParametersName(self, region_method):
        v = self.view

        def params(region):
            params_region = v.find_by_selector(
                'meta.function.parameters.delphi')
            param_name_region = v.find_by_selector(
                'variable.parameter.function.delphi')
            params_region_filt = [
                s for s in params_region if region.contains(s)]
            params_region_filt = [
                s for s in param_name_region if
                params_region_filt[0].contains(s)]

            return params_region_filt

        def paramsFromRegion(region):
            try:
                params_region_filt = params(region)
                x = [v.substr(x) for x in params_region_filt]
                return x
            except:
                return []
        return paramsFromRegion(region_method)

    def getVariablesMethod(self, word_region):
        v = self.view
        region_variables = []
        begin_line, column = v.rowcol(word_region.begin())
        funcRegion = v.find_by_selector('keyword.control')
        region_method = self.method_region[0]
        for sFirst in reversed(funcRegion):
            if (sFirst < region_method):
                break
            region_line_meta, col = v.rowcol(sFirst.end())
            if region_line_meta <= begin_line:
                line = v.substr(sFirst)
                if line.find('var') >= 0:
                    region_variables.append(sFirst.end())

                    begin_line2, column = v.rowcol(sFirst.begin())
                    funcRegion2 = v.find_by_selector(
                        'keyword.control')
                    for sSecond in (funcRegion2):
                        line_region_var, col = v.rowcol(sSecond.end())
                        if line_region_var > begin_line2:
                            line2 = v.substr(sSecond)
                            if (line2.find('begin') >= 0) or (line2.find('out') >= 0):
                                region_variables.append(sSecond.end())
                                break
                    break

        if (region_variables == []):
            return

        word_region = v.word(
            sublime.Region(region_variables[0], region_variables[1]))
        words = v.substr(word_region).splitlines()

        variable = []
        for word in words:
            word = re.sub('begin\s*|var\s*|\s*', '', word)
            if (word != ''):
                variable.append(word)
            pass
        return variable

    def getClassName(self):
        class_name = ''
        view = self.view
        vsubstr = view.substr
        selector = view.find_by_selector
        classnamemethod = selector('entity.class.name.delphi')
        method_regions = selector('function.implementation.delphi')

        self.method_region = [
            s for s in method_regions if self.cursor_region.intersects(s)]
        method_region = self.method_region
        classnamemethodfiltered = [
            s for s in classnamemethod if method_region[0].contains(s)]

        if classnamemethodfiltered:
            class_name = vsubstr(classnamemethodfiltered[0])

        return class_name

    def getObject(self, word_region):
        v = self.view
        variables = self.getVariablesMethod(word_region)
        selection_text = v.substr(word_region).splitlines()
        variable_name = []

        if not (variables is None):
            for variable in variables:
                if (variable.find(',') > 0):
                    variavel = variable[0:variable.find(':')]
                    variable_name.append(variavel[0:variavel.find(',')])
                    self.definirParametros(variavel, variable_name)
                elif (variable.find(':') > 0):
                    variavel = variable[0:variable.find(':')]
                    variable_name.append(variavel)

            # print('variables: %s' % variables)

        params = self.getParametersName(self.method_region)
        # print('selection_text: %s' % selection_text)
        print('variables: %s' % variables)
        if params:
            print('params: %s' % params)
        if params and variables:
            return selection_text, [], []
        params_with_type = []
        if params:
            params_with_type = self.getParamsWithType(params)
            # print('params_with_type: %s' % params_with_type)
        method_with_params = (params != []) and not (params is None)
        parametros = []
        if method_with_params:
            parametros = self.getParams(params)
            # print('parametros: %s' % parametros)

        variable_on_text = []
        if ((parametros != []) and not (parametros is None)):
            for text in selection_text:
                for name in parametros:
                    if len(name) == 1:
                        continue

                    if (text.find(name) > -1):
                        if not (name in variable_on_text):
                            variable_on_text.append(name)

        # print('variable_name:%s' % variable_name)

        if ((variable_name != []) and not (variable_name is None)):
            for text in selection_text:
                for name in variable_name:
                    if len(name) == 1:
                        continue

                    if (text.find(name) > -1):
                        if not (name in variable_on_text):
                            # print('name:%s' % name)
                            variable_on_text.append(name)

        # print('variable_on_text: %s' % variable_on_text)
        variable_on_text_with_type = []

        # settings = sublime.load_settings(
        #     'plugins-development.sublime-settings')
        prefix_param = v.settings().get("prefix_param", {})
        print('prefix_param:%s' % prefix_param)

        # if ((params_with_type != []) and not (params_with_type is None)):
        #     for new_variable in variable_on_text:
        #         for new_param in params_with_type:
        #             if (new_param.find(new_variable) > -1):
        #                 if (new_param.find(';') > -1):
        #                     end_pos = new_param.find(';')
        #                 else:
        #                     end_pos = len(new_param)

        #                 type_param = new_param[new_param.find(':') + 1:end_pos]
        #                 param_type = ''
        #                 if type_param.upper() in prefix_param:
        #                     for key_in in prefix_param[type_param.upper()]:
        #                         if len(prefix_param[type_param.upper()][key_in]) in [1, 3]:
        #                             if (new_variable[0:len(prefix_param[type_param.upper()][key_in])] == key_in):
        #                                 param_type = prefix_param[
        #                                     type_param.upper()][key_in]
        #                                 break
        #                         else:
        #                             if (new_variable[0: len(prefix_param[type_param.upper()][key_in])] != key_in):
        #                                 param_type = prefix_param[type_param.upper()][key_in][0:1] if (
        #                                     new_variable[0:1] == key_in[1:2]) else prefix_param[type_param.upper()][key_in]
        #                                 break
        #                             else:
        #                                 break
        #                 else:
        #                     key = 'ELSE'
        #                     for key_in in prefix_param[key]:
        #                         if len(prefix_param[key][key_in]) == 1:
        #                             if (new_variable[0:1] == key_in):
        #                                 param_type = prefix_param[
        #                                     key][key_in]
        #                                 break
        #                         else:
        #                             if (new_variable[0: len(prefix_param[key][key_in])] != key_in):
        #                                 param_type = prefix_param[key][key_in][0:1] if (
        #                                     new_variable[0:1] == key_in[1:2]) else prefix_param[key][key_in]
        #                                 break

        #                 variable_on_text_with_type.append(
        # param_type + new_variable + ': ' + type_param + ';')

        # if ((variables != []) and not (variables is None)):
        #     for new_variable in variable_on_text:
        #         for new_param in variables:
        #             if (new_param.find(new_variable) > -1):
        #                 if (new_param.find(';') > -1):
        #                     end_pos = new_param.find(';')
        #                 else:
        #                     end_pos = len(new_param)
        #                 type_param = new_param[new_param.find(':') + 1:end_pos]
        #                 param_type = ''

        #                 if type_param.upper() in prefix_param:
        #                     for key_in in prefix_param[type_param.upper()]:
        #                         if len(prefix_param[type_param.upper()][key_in]) in [1, 3]:
        #                             if (new_variable[0:len(prefix_param[type_param.upper()][key_in])] == key_in):
        #                                 param_type = prefix_param[
        #                                     type_param.upper()][key_in]
        #                                 break
        #                         else:
        #                             if (new_variable[0: len(prefix_param[type_param.upper()][key_in])] != key_in):
        #                                 param_type = prefix_param[type_param.upper()][key_in][0:1] if (
        #                                     new_variable[0:1] == key_in[1:2]) else prefix_param[type_param.upper()][key_in]
        #                                 break
        #                             else:
        #                                 break
        #                 else:
        #                     key = 'ELSE'
        #                     for key_in in prefix_param[key]:
        #                         if len(prefix_param[key][key_in]) == 1:
        #                             if (new_variable[0:1] == key_in):
        #                                 param_type = prefix_param[
        #                                     key][key_in]
        #                                 break
        #                         else:
        #                             if (new_variable[0: len(prefix_param[key][key_in])] != key_in):
        #                                 param_type = prefix_param[key][key_in][0:1] if (
        #                                     new_variable[0:1] == key_in[1:2]) else prefix_param[key][key_in]
        #                                 break

        #                 variable_on_text_with_type.append(
        # param_type + new_variable + ': ' + type_param + ';')

        # print(variable_on_text_with_type)

        for i in range(0, len(selection_text)):
            for var, var_with_type in zip(variable_on_text,
                                          variable_on_text_with_type):
                selection_text[i] = selection_text[i].replace(
                    var, var_with_type[0: var_with_type.find(':')])

        return selection_text, variable_on_text_with_type, variable_on_text

    def getViewSel(self, cursor_region):
        v = self.view
        selection_region = cursor_region
        word_region = v.word(selection_region)
        return word_region

    def addHeadMethod(self, edit, parametros):
        v = self.view
        # settings = sublime.load_settings(
        #     'plugins-development.sublime-settings')
        extract_visibility = v.settings().get("extract_visibility", "private")
        head_region = self.getVisibilityRegion(extract_visibility)
        linha, _ = v.rowcol(head_region.begin())

        linha += 1
        pt = v.text_point(linha, 0)
        v.insert(
            edit, pt, '\n' + '    procedure ExtractedMethod' +
            parametros + ';' + '\n')

    def getVisibilityRegion(self, edit, classdefinitionfiltered):
        v = self.view
        visibility = v.settings().get("visibility", "private")
        createblock = v.settings().get("create_visibility_block", False)

        visibility_region = v.find_by_selector(
            visibility + '.block.delphi')
        visibility_regionfiltered = [
            s for s in visibility_region if classdefinitionfiltered.contains(s)]

        if not visibility_regionfiltered:
            if not createblock:
                print('Visibility ' + visibility + ' do not exists.')
                return
            elif createblock:
                line = classdefinitionfiltered.end()
                line, _ = v.rowcol(line)
                line -= 1
                pt = v.text_point(line, 0)
                pt = v.line(pt).end()
                tab_size = v.settings().get("tab_size")
                v.insert(edit, pt, '\n' + (' ' * tab_size) +
                         visibility)
                pt = pt + tab_size + len(visibility) + 2
                visibility_regionfiltered = [sublime.Region(
                    pt, pt + (tab_size * 2))]
        return visibility_regionfiltered

    def lineDecreases(self, region, line):
        line -= 1
        ptinicio = self.view.text_point(line, 0)
        if ((region.begin() < ptinicio) and (region.end() > ptinicio)):
            return self.lineDecreases(region, line)
        return ptinicio, line

    def getParams(self, params):
        variable_name = []

        if not (params is None):
            for param in params:
                if (param.find(',') > 0):
                    variable = param[0:len(param)]
                    variable_name.append(variable[0:variable.find(',')])
                    self.defineParams(variable, variable_name)
                elif (param.find(':') > 0):
                    variable = param[0:param.find(':')]
                    variable_name.append(variable)
                    if (param.find(';') > 0):
                        self.defineParams(
                            param[param.find(';') + 1:len(param)],
                            variable_name)

            param_return = []
            for variable_1 in variable_name:
                if (variable_1 != ''):
                    param_return.append(variable_1)
        return param_return

    def defineParams(self, variable, variables):
        control = False
        if (variable.find(',') > 0):
            next_variable = variable[variable.find(',') + 1:len(variable)]
        else:
            next_variable = variable

        next_comma = next_variable.find(',')
        next_semicolon = next_variable.find(';')
        next_colon = next_variable.find(':')
        if ((next_comma < next_semicolon) and
                (next_comma != -1) or (next_semicolon == -1)):
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

        if ((next_comma > 0) or
            (next_variable[0:variable_end].find(':') > 0) or
                (next_semicolon > 0)):
            if control:
                next_variable = next_variable[
                    next_variable.find(';') + 1:len(next_variable)]

            self.defineParams(next_variable, variables)
        pass

    def definirParametros(self, variavel, variaveis):
        proxima_variavel = variavel[variavel.find(',') + 1:len(variavel)]
        if (proxima_variavel.find(',') > 0):
            fimvariavel = proxima_variavel.find(',')
        else:
            fimvariavel = len(proxima_variavel)

        variaveis.append(proxima_variavel[0:fimvariavel])

        if (proxima_variavel.find(',') > 0):
            self.definirParametros(proxima_variavel, variaveis)
        pass

    def getParamsWithType(self, params):
        variable_name = []

        if not (params is None):
            size = len(params)
            control_i = -1
            i = 0
            for i in range(size):
                if (i == control_i):
                    continue
                if (params[i].find(';') > 0):
                    variable = params[i][0:len(params[i])]

                    variable_name.append(variable[0:variable.find(';') + 1])
                    self.defineParamsWithType(
                        variable[(variable.find(';') + 1):len(params[i])],
                        variable_name)
                elif ((params[i].find(',') > 0) and
                      (len(params[i]) - 1 == params[i].find(','))):
                    control_i = i + 1
                    variable = params[i][0:len(params[i])]
                    variable += params[control_i][0:len(params[control_i])]
                    self.defineParamsWithType(
                        variable, variable_name)
                else:
                    if (params[i].find('=') > 0):
                        nPos = params[i].find('=')
                        end_variable = ';'
                    else:
                        nPos = len(params[i])
                        end_variable = ''
                    variable = params[i][0:nPos] + end_variable
                    variable_name.append(variable)

            param_return = []
            for var in variable_name:
                if (var != ''):
                    param_return.append(var)
        return param_return

    def defineParamsWithType(self, variable, variable_name):
        if (variable.find(';') > 0):
            variable = variable[0:len(variable)]
            variable_name.append(variable[0:(variable.find(';') + 1)])
            self.defineParamsWithType(
                variable[(variable.find(';') + 1):len(variable)],
                variable_name)
        else:
            variable = variable[0:len(variable)]
            variable_name.append(variable)

    def filter(self, edit, needle):
        v = self.view
        regions = [s for s in v.sel() if not s.empty()]

        if len(regions) == 0:
            regions = [sublime.Region(0, v.size())]

        regiao_metodo_novo = 0

        v.sel().clear

        selection_region = v.sel()[0]
        word_region = v.word(selection_region)

        view_sel = v.sel()
        view_sel.subtract(word_region)

        for region in reversed(regions):
            lines = v.split_by_newlines(region)

            for line in reversed(lines):
                if 'ExtractedMethod' in v.substr(line):
                    # word_region = v.word(line)
                    # word = v.substr(word_region).strip()
                    regiao_do_metodo = v.find(
                        'ExtractedMethod', line.begin())
                    v.sel().add(regiao_do_metodo)

        v.show(regiao_do_metodo)
        return regiao_metodo_novo
