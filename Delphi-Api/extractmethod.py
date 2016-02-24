import sublime
import sublime_plugin
import re

clean_name = re.compile('^\s*(public\s+|private\s+|protected\s+|static\s+|procedure\s+|function\s+|def\s+|Shortint\s+|Integer\s+|Longint\s+|Byte\s+|Word\s+|Boolean\s+|WordBool\s+|LongBool\s+|ByteBool\s+|Real\s+|Single\s+|Double\s+|Extended\s+|Comp\s+|String\s+|Char\s+|Length\s+|Upcase\s+|textbackground\s+|textcolor\s+|gotoxy\s+|crt\s+|clrscr\s+|readkey\s+|read\s+|readln\s+|property\s+|)+', re.I)

clean_name_private = re.compile('^\s*()+', re.I)


class extractmethod(sublime_plugin.TextCommand):

    def run(self, edit):
        print("Extract Method")
        view = self.view
        selection_region = view.sel()[0]
        word_region = view.word(selection_region)

        word = view.substr(word_region).strip()
        amount_selected_row = word.count('\n') + 1
        word = re.sub('[\=\:\(\)\{\}\s]', '', word)

        nRegion_Procedure, nRegion_Function = self.GetMethodsRegion(
            view, selection_region)

        nPosicaoMetodoMaisPerto = sublime.Region(-1, -1)
        if ((nRegion_Function > nRegion_Procedure) or
                (nRegion_Function is None)):
            nPosicaoMetodoMaisPerto = nRegion_Procedure
        if ((not (nRegion_Function is None)) and
                (nRegion_Function < nRegion_Procedure)):
            nPosicaoMetodoMaisPerto = nRegion_Function

        if (nPosicaoMetodoMaisPerto < selection_region):
            regions = self.GetDeclarationRegion(view, 'implementation')
            nPosicaoMetodoMaisPerto = view.find(
                'initialization', regions.begin())
            if (nPosicaoMetodoMaisPerto == sublime.Region(-1, -1)):
                nPosicaoMetodoMaisPerto = view.find(
                    'end\.', regions.begin())

        line, _ = view.rowcol(nPosicaoMetodoMaisPerto.begin())
        selection_text, variable, variable_on_text = self.GetObject(
            view, self.GetViewSel(view, view.sel()[0]))
        self.AddMethod(
            edit, view, line, amount_selected_row, selection_text,
            variable, variable_on_text)

    def GetMethodDeclarationLine(self):
        for selectedReg in self.view.sel():
            regionRow, regionColumn = self.view.rowcol(selectedReg.begin())
            funcRegion = self.view.find_by_selector('entity.name.function')

            for sFirst in reversed(funcRegion):
                row, col = self.view.rowcol(sFirst.end())
                if row <= regionRow:
                    return row - 1

    def GetMethodsRegion(self, view, selection):
        procedure_valido = False
        i = 0
        while not procedure_valido:
            i += 1

            if (i == 30):
                break

            nRegion_Procedure = view.find('procedure', selection.begin())

            if (nRegion_Procedure == sublime.Region(-1, -1)):
                continue

            regiaodaprocedure = view.full_line(nRegion_Procedure)
            linha_procedure = view.substr(
                regiaodaprocedure).splitlines()
            linha_procedure = clean_name_private.sub('', linha_procedure[0])
            linha_procedure = linha_procedure.strip()

            if (linha_procedure.find('.') >= 1):
                procedure_valido = True
                break
            # else:
            #     selection = sublime.Region(
            #         (selection.end() + 1), (selection.end() + 70))
            pass

        function_valido = False
        i = 0
        while not function_valido:
            i += 1

            if (i == 30):
                break
            nRegion_Function = view.find('function', selection.begin())
            if (nRegion_Function == sublime.Region(-1, -1)):
                continue

            regiaodafunction = view.full_line(nRegion_Function)
            linha_function = view.substr(regiaodafunction).splitlines()
            linha_function = clean_name_private.sub('', linha_function[0])
            linha_function = linha_function.strip()

            if (linha_function.count('.') >= 1):
                function_valido = True
                break
            # else:
            #     selection = sublime.Region(
            #         (selection.end() + 1), (selection.end() + 70))
            pass

        return nRegion_Procedure, nRegion_Function

    def GetViewSel(self, view, selecao):
        selection_region = selecao
        word_region = view.word(selection_region)
        word = view.substr(word_region).strip()
        word = re.sub('[\=\:\(\)\{\}\s]', '', word)
        for selectedReg in view.sel():
            line, regionColumn = view.rowcol(selectedReg.begin())
        return word_region

    def GetDeclarationRegion(self, view, word):
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
                            break

    def GetClassName(self, view):
        region = sublime.Region(0, view.size())
        region_class = view.find("= class", region.begin())
        regiaodaclasse = view.full_line(region_class)

        lines = view.substr(regiaodaclasse).splitlines()
        name = clean_name.sub('', lines[0])
        s = name.strip()
        s = s.split("=")[0]
        s = s.split(" ")[0]
        return s

    def AddHeadMethod(self, edit, view, parametros):
        region_protected = self.GetDeclarationRegion(view, 'protected')
        if region_protected is None:
            region_private = self.GetDeclarationRegion(view, 'private')
        if not (region_protected is None):
            linha, region_col = view.rowcol(region_protected.begin())
        else:
            linha, region_col = view.rowcol(region_private.begin())
        if not (region_protected is None):
            linha = linha - 1

        linha += 1
        pt = view.text_point(linha, 0)
        view.insert(
            edit, pt, '\n' + '    procedure ExtractedMethod' +
            parametros + ';' + '\n')

    def LineDecreases(self, region, line):
        line -= 1
        ptinicio = self.view.text_point(line, 0)
        if ((region.begin() < ptinicio) and (region.end() > ptinicio)):
            return self.LineDecreases(region, line)
        return ptinicio, line

    def AddMethod(self, edit, view, line, amount_selected_row, selection_text,
                  variable, variable_on_text):
        classe = self.GetClassName(view)
        line_decreases = True
        line -= 1
        comment_previous_line = False
        while line_decreases:
            ptinicio = view.text_point(line, 0)
            comment_block_regions = view.find_by_selector(
                'comment.block.delphi')
            if comment_block_regions:
                for r in comment_block_regions:
                    ptinicio = view.text_point(line, 0)
                    if (((r.begin() < ptinicio) and (r.end() > ptinicio)) or
                            (r.begin() == ptinicio)):
                        ptinicio, line = self.LineDecreases(r, line)
                        comment_previous_line = True
                    else:
                        line_decreases = False
            else:
                comment_line_regions = view.find_by_selector(
                    'comment.line.double-slash')
                if comment_line_regions:
                    for r in comment_line_regions:
                        linha, _ = view.rowcol(r.begin())
                        ptinicio = view.text_point(line, 0)
                        if (((r.begin() < ptinicio) and (r.end() > ptinicio)) or
                                (r.begin() == ptinicio)):
                            ptinicio, line = self.LineDecreases(r, line)
                            comment_previous_line = True
                        else:
                            line_decreases = False
                else:
                    break

        if not comment_previous_line:
            line += 1
            ptinicio = view.text_point(line, 0)

        parametros = ''
        if variable != [] and not (variable is None):
            parametros = '('
            for var in variable:
                parametros += var
            if parametros[len(parametros) - 1:len(parametros)] == ';':
                parametros = parametros[0:len(parametros) - 1]
            parametros += ')'
        view.insert(edit, ptinicio, 'procedure ' +
                    classe + '.ExtractedMethod' + parametros + ';' + '\n')

        line_begin = line + 1
        pt = view.text_point(line_begin, 0)
        view.insert(edit, pt, 'begin' + ' \n')

        line_text = line_begin + 1
        pt = view.text_point(line_text, 0)
        word_region = self.GetViewSel(view, view.sel()[0])

        texto = ''
        for text in selection_text:
            texto += text + '\n'
        view.insert(edit, pt, '  ' + texto + ' \n')

        linha_end = line_text + 0 + amount_selected_row
        pt = view.text_point(linha_end, 0)
        view.insert(edit, pt, 'end;' + ' \n')

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

        view.replace(
            edit, word_region, '\n  ExtractedMethod' + params_declare + '; \n')

        linha, _ = view.rowcol(word_region.begin())

        ptnovo = view.text_point(linha, 2)

        selection_region = view.sel()[0]
        word_region = view.word(selection_region)
        view.sel().subtract(word_region)
        view.sel().add(ptnovo)

        self.AddHeadMethod(edit, view, parametros)

        self.filter(self.view, edit, '')

    def GetVariablesMethod(self, view, word_region):
        region_variables = []
        begin_line, column = self.view.rowcol(word_region.begin())
        funcRegion = self.view.find_by_selector('keyword.control')
        region_method = self.GetMethodRegion(view)
        for sFirst in reversed(funcRegion):
            if (sFirst < region_method):
                break
            region_line_meta, col = self.view.rowcol(sFirst.end())
            if region_line_meta <= begin_line:
                line = self.view.substr(sFirst)
                if line.find('var') >= 0:
                    region_variables.append(sFirst.end())

                    begin_line2, column = self.view.rowcol(sFirst.begin())
                    funcRegion2 = self.view.find_by_selector(
                        'keyword.control')
                    for sSecond in (funcRegion2):
                        line_region_var, col = self.view.rowcol(sSecond.end())
                        if line_region_var > begin_line2:
                            line2 = self.view.substr(sSecond)
                            if (line2.find('begin') >= 0):
                                region_variables.append(sSecond.end())
                                break
                    break

        if (region_variables == []):
            return

        word_region = view.word(
            sublime.Region(region_variables[0], region_variables[1]))
        words = view.substr(word_region).splitlines()

        variable = []
        for word in words:
            word = re.sub('begin\s+|var\s+|\s*', '', word)
            if (word != ''):
                variable.append(word)
            pass
        return variable

    def GetParametersName(self, view, region_method):
        method_region = view.full_line(region_method)
        lines = view.substr(method_region).splitlines()
        continua = False
        for line in lines:
            if (len(line.split("(")) > 1):
                continua = True
        if not continua:
            return

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
                for r in reversed(function_regions):
                    row, col = view.rowcol(r.begin())
                    if row <= region_row:
                        lines = view.substr(r).splitlines()
                        name = []
                        for line in lines:
                            line = re.sub(
                                'var\s+|const\s+|out\s+|\s*', '', line)

                            if (line != ''):
                                name.append(line)
                        return name
                        break
        return []

    def GetParams(self, params):
        variable_name = []

        if not (params is None):
            for param in params:
                if (param.find(',') > 0):
                    variable = param[0:len(param)]
                    variable_name.append(variable[0:variable.find(',')])
                    self.DefineParams(variable, variable_name)
                elif (param.find(':') > 0):
                    variable = param[0:param.find(':')]
                    variable_name.append(variable)
                    if (param.find(';') > 0):
                        self.DefineParams(
                            param[param.find(';') + 1:len(param)],
                            variable_name)

            param_return = []
            for variable_1 in variable_name:
                if (variable_1 != ''):
                    param_return.append(variable_1)
        return param_return

    def DefineParams(self, variable, variables):
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

            self.DefineParams(next_variable, variables)
        pass

    def GetMethodRegion(self, view):
        for region in view.sel():
            region_row, region_col = view.rowcol(region.begin())
            function_regions = view.find_by_selector('meta.function')
            if function_regions:
                for r in reversed(function_regions):
                    row, col = view.rowcol(r.begin())
                    if row <= region_row:
                        return r
                        break

    def DefinirParametros(self, variavel, variaveis):
        proxima_variavel = variavel[variavel.find(',') + 1:len(variavel)]
        if (proxima_variavel.find(',') > 0):
            fimvariavel = proxima_variavel.find(',')
        else:
            fimvariavel = len(proxima_variavel)

        variaveis.append(proxima_variavel[0:fimvariavel])

        if (proxima_variavel.find(',') > 0):
            self.DefinirParametros(proxima_variavel, variaveis)
        pass

    def GetParamsWithType(self, params):
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
                    self.DefineParamsWithType(
                        variable[(variable.find(';') + 1):len(params[i])],
                        variable_name)
                elif ((params[i].find(',') > 0) and
                      (len(params[i]) - 1 == params[i].find(','))):
                    control_i = i + 1
                    variable = params[i][0:len(params[i])]
                    variable += params[control_i][0:len(params[control_i])]
                    self.DefineParamsWithType(
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

    def DefineParamsWithType(self, variable, variable_name):
        if (variable.find(';') > 0):
            variable = variable[0:len(variable)]
            variable_name.append(variable[0:(variable.find(';') + 1)])
            self.DefineParamsWithType(
                variable[(variable.find(';') + 1):len(variable)],
                variable_name)
        else:
            variable = variable[0:len(variable)]
            variable_name.append(variable)

    def GetObject(self, view, word_region):
        variables = self.GetVariablesMethod(view, word_region)
        selection_text = view.substr(word_region).splitlines()
        variable_name = []

        if not (variables is None):
            for variable in variables:
                if (variable.find(',') > 0):
                    variavel = variable[0:variable.find(':')]
                    variable_name.append(variavel[0:variavel.find(',')])
                    self.DefinirParametros(variavel, variable_name)
                elif (variable.find(':') > 0):
                    variavel = variable[0:variable.find(':')]
                    variable_name.append(variavel)

            #print('variables: %s' % variables)

        params = self.GetParametersName(view, self.GetMethodRegion(view))
        # print('selection_text: %s' % selection_text)
        # print('variables: %s' % variables)
        # print('params: %s' % params)
        if (params is None) and (variables is None):
            return selection_text, [], []
        params_with_type = []
        if not (params is None):
            params_with_type = self.GetParamsWithType(params)
            #print('params_with_type: %s' % params_with_type)
        method_with_params = (params != []) and not (params is None)
        parametros = []
        if method_with_params:
            parametros = self.GetParams(params)
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

        settings = sublime.load_settings('delphi.sublime-settings')
        extracao = settings.get("extracao", {})

        if ((params_with_type != []) and not (params_with_type is None)):
            for new_variable in variable_on_text:
                for new_param in params_with_type:
                    if (new_param.find(new_variable) > -1):
                        if (new_param.find(';') > -1):
                            end_pos = new_param.find(';')
                        else:
                            end_pos = len(new_param)

                        type_param = new_param[new_param.find(':') + 1:end_pos]
                        param_type = ''
                        if type_param.upper() in extracao:
                            for key_in in extracao[type_param.upper()]:
                                if len(extracao[type_param.upper()][key_in]) in [1, 3]:
                                    if (new_variable[0:len(extracao[type_param.upper()][key_in])] == key_in):
                                        param_type = extracao[
                                            type_param.upper()][key_in]
                                        break
                                else:
                                    if (new_variable[0: len(extracao[type_param.upper()][key_in])] != key_in):
                                        param_type = extracao[type_param.upper()][key_in][0:1] if (
                                            new_variable[0:1] == key_in[1:2]) else extracao[type_param.upper()][key_in]
                                        break
                                    else:
                                        break
                        else:
                            key = 'ELSE'
                            for key_in in extracao[key]:
                                if len(extracao[key][key_in]) == 1:
                                    if (new_variable[0:1] == key_in):
                                        param_type = extracao[
                                            key][key_in]
                                        break
                                else:
                                    if (new_variable[0: len(extracao[key][key_in])] != key_in):
                                        param_type = extracao[key][key_in][0:1] if (
                                            new_variable[0:1] == key_in[1:2]) else extracao[key][key_in]
                                        break

                        variable_on_text_with_type.append(
                            param_type + new_variable + ': ' + type_param + ';')

        if ((variables != []) and not (variables is None)):
            for new_variable in variable_on_text:
                for new_param in variables:
                    if (new_param.find(new_variable) > -1):
                        if (new_param.find(';') > -1):
                            end_pos = new_param.find(';')
                        else:
                            end_pos = len(new_param)
                        type_param = new_param[new_param.find(':') + 1:end_pos]
                        param_type = ''

                        if type_param.upper() in extracao:
                            for key_in in extracao[type_param.upper()]:
                                if len(extracao[type_param.upper()][key_in]) in [1, 3]:
                                    if (new_variable[0:len(extracao[type_param.upper()][key_in])] == key_in):
                                        param_type = extracao[
                                            type_param.upper()][key_in]
                                        break
                                else:
                                    if (new_variable[0: len(extracao[type_param.upper()][key_in])] != key_in):
                                        param_type = extracao[type_param.upper()][key_in][0:1] if (
                                            new_variable[0:1] == key_in[1:2]) else extracao[type_param.upper()][key_in]
                                        break
                                    else:
                                        break
                        else:
                            key = 'ELSE'
                            for key_in in extracao[key]:
                                if len(extracao[key][key_in]) == 1:
                                    if (new_variable[0:1] == key_in):
                                        param_type = extracao[
                                            key][key_in]
                                        break
                                else:
                                    if (new_variable[0: len(extracao[key][key_in])] != key_in):
                                        param_type = extracao[key][key_in][0:1] if (
                                            new_variable[0:1] == key_in[1:2]) else extracao[key][key_in]
                                        break

                        variable_on_text_with_type.append(
                            param_type + new_variable + ': ' + type_param + ';')

        # print(variable_on_text_with_type)

        for i in range(0, len(selection_text)):
            for var, var_with_type in zip(variable_on_text,
                                          variable_on_text_with_type):
                selection_text[i] = selection_text[i].replace(
                    var, var_with_type[0: var_with_type.find(':')])

        return selection_text, variable_on_text_with_type, variable_on_text

    # def abreJanela(self, edit, view):
    #     def done(needle):
    #         nova_regiao = self.filter(self.view, edit, needle)

    #     cb = sublime.get_clipboard()
    #     sublime.active_window().show_input_panel(
    #         "Nome do novo metodo: ", cb, done, None, None)

    def filter(self, view, edit, needle):
        regions = [s for s in view.sel() if not s.empty()]

        if len(regions) == 0:
            regions = [sublime.Region(0, view.size())]

        regiao_metodo_novo = 0

        view.sel().clear

        selection_region = view.sel()[0]
        word_region = view.word(selection_region)

        view_sel = view.sel()
        view_sel.subtract(word_region)

        for region in reversed(regions):
            lines = view.split_by_newlines(region)

            for line in reversed(lines):
                if 'ExtractedMethod' in view.substr(line):
                    # word_region = view.word(line)
                    # word = view.substr(word_region).strip()
                    regiao_do_metodo = view.find(
                        'ExtractedMethod', line.begin())
                    view.sel().add(regiao_do_metodo)

        view.show(regiao_do_metodo)
        return regiao_metodo_novo
