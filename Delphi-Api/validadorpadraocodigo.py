import sublime
import sublime_plugin
import re
from . import *

clean_name_private = re.compile('^\s*()+', re.I)
methods_name = ';|class function| |property|write|read|function|procedure|program|constructor|destructor[\s*]'


class validadorpadraocodigo(sublime_plugin.TextCommand):

    """docstring for validadorpadraocodigo"""

    def run(self, edit):
        print('Validando.')
        view = self.view
        regions = [sublime.Region(0, 0)]
        parametros_errados = []
        metodo_com_parametro = []
        function_regions = view.find_by_selector('meta.function')
        for region in regions:
            region_row, _ = view.rowcol(region.begin())
            parameters_regions = view.find_by_selector(
                'meta.function.parameters')
            nPosicao_implementatio = self.GetDeclarationRegion(
                view, 'implementation')
            nPosicao_private = self.MethodVisibility(view)
            if parameters_regions:
                for r in (parameters_regions):
                    if (r < nPosicao_implementatio) and (r > nPosicao_private):
                        row, _ = view.rowcol(r.begin())
                        if row >= region_row:
                            lines = view.substr(r).splitlines()
                            size = len(lines)
                            i = 0
                            name = ''
                            for i in range(size):
                                lines[i] = re.sub(
                                    'var\s+|const\s+|out\s+|\s*', '', lines[i])

                                if (lines[i] != ''):
                                    name += lines[i]
                            name += ';'

                            parametros_com_tipo = []
                            while name.count(';') >= 1:
                                parametros_com_tipo.append(
                                    name[0:name.find(';')])
                                name = name[name.find(';') + 1:len(name)]
                            variable = self.GetParams(parametros_com_tipo)
                            parametros_errados = PegarParametrosForaDoPadrao(
                                variable, parametros_com_tipo)
                            if parametros_errados != []:
                                if function_regions:
                                    for function_r in (function_regions):
                                        if ((function_r.begin() < r.begin()) and (function_r.end() > r.end())):
                                            row, _ = view.rowcol(
                                                function_r.begin())
                                            metodo = view.substr(
                                                function_r)
                                            metodo = metodo.split("(")[0]
                                            metodo = re.sub(
                                                methods_name, '', metodo)
                                            metodo_com_parametro2 = []
                                            metodo_com_parametro2.append(
                                                metodo)
                                            metodo_com_parametro2.append(
                                                parametros_errados)
                                            metodo_com_parametro.append(
                                                metodo_com_parametro2)
                                            break

        print('parametros_errados %s' % metodo_com_parametro)
        # self.add_update(metodo_com_parametro)
        if metodo_com_parametro != []:
            view = self.view
            new_view = self.view.window().new_file(sublime.TRANSIENT, 'Delphi')
            new_view.insert(
                edit, new_view.text_point(0, 0), self.FormatarParametroParaString(metodo_com_parametro))
        pass

    def FormatarParametroParaString(self, metodo_com_parametro):
        qtd_metodos = len(metodo_com_parametro)
        i = 0
        retorno = ''
        for i in range(qtd_metodos):
            retorno += metodo_com_parametro[i][0] + ':\n'
            qtd_parametros = len(metodo_com_parametro[i][1])
            j = 0
            for j in range(qtd_parametros):
                retorno += '     ' + metodo_com_parametro[i][1][j] + '\n'
                pass
            pass
            retorno += '\n'
        return retorno
        pass

    def add_update(self, metodo_com_parametro):
        sublime.message_dialog(str(metodo_com_parametro))

    def MethodVisibility(self, view):
        retorno = self.GetDeclarationRegion(view, 'private')
        if not (retorno is None):
            return retorno

        retorno = self.GetDeclarationRegion(view, 'protected')
        if not (retorno is None):
            return retorno

        retorno = self.GetDeclarationRegion(view, 'public')
        if not (retorno is None):
            return retorno

        retorno = self.GetDeclarationRegion(view, 'published')
        if not (retorno is None):
            return retorno

    def GetDeclarationRegion(self, view, word):
        regions = [sublime.Region(0, view.size())]
        for region in regions:
            region_row, _ = view.rowcol(region.begin())
            function_regions = view.find_by_selector('keyword.control')
            if function_regions:
                for r in function_regions:
                    row, _ = view.rowcol(r.begin())
                    if row >= region_row:
                        lines = view.substr(r).splitlines()
                        name = clean_name_private.sub('', lines[0])
                        s = name.strip()
                        if s == word:
                            return r
                            break

    def GetParams(self, params):
        variable_name = []

        if not (params is None):
            size = len(params)
            i = 0
            for i in range(size):
                if (params[i].find(',') > 0):
                    variable = params[i][0:len(params[i])]
                    variable_name.append(variable[0:variable.find(',')])
                    self.DefineParams(variable, variable_name)
                elif (params[i].find(':') > 0):
                    variable = params[i][0:params[i].find(':')]
                    variable_name.append(variable)
                    if (params[i].find(';') > 0):
                        self.DefineParams(
                            params[i][params[i].find(';') + 1:len(params[i])], variable_name)

        size = len(variable_name)
        i = 0
        param_return = []
        for i in range(size):
            if (variable_name[i] != ''):
                param_return.append(variable_name[i])
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
        if (next_comma < next_semicolon) and (next_comma != -1) or (next_semicolon == -1):
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

        if (next_comma > 0) or (next_variable[0:variable_end].find(':') > 0) or (next_semicolon > 0):
            if control:
                next_variable = next_variable[
                    next_variable.find(';') + 1:len(next_variable)]

            self.DefineParams(next_variable, variables)
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
                        variable[(variable.find(';') + 1):len(params[i])], variable_name)
                elif (params[i].find(',') > 0) and (len(params[i]) - 1 == params[i].find(',')):
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

            size = len(variable_name)
            i = 0
            param_return = []
            for i in range(size):
                if (variable_name[i] != ''):
                    param_return.append(variable_name[i])
        return param_return

    def DefineParamsWithType(self, variable, variable_name):
        if (variable.find(';') > 0):
            variable = variable[0:len(variable)]
            variable_name.append(variable[0:(variable.find(';') + 1)])
            self.DefineParamsWithType(
                variable[(variable.find(';') + 1):len(variable)], variable_name)
        else:
            variable = variable[0:len(variable)]
            variable_name.append(variable)

    # def FormatarParametrosNoPadrao(self):
    #     if ((variables != []) and (not (variables is None))):
    #         text_size = len(variable_on_text)
    #         vaiable_size = len(variables)
    #         i = 0
    #         j = 0
    #         for i in range(text_size):
    #             for j in range(vaiable_size):
    #                 if (variables[j].find(variable_on_text[i]) > -1):
    #                     if (variables[j].find(';') > -1):
    #                         end_pos = variables[j].find(';')
    #                     else:
    #                         end_pos = len(variables[j])
    #                     type_param = variables[j][
    #                         variables[j].find(':') + 1:end_pos]
    #                     param_type = ''
    #                     if (type_param.upper() == 'INTEGER') or (type_param.upper() == 'DOUBLE'):
    #                         if (variable_on_text[i][0:1] == 'n'):
    #                             param_type = 'p'
    #                         elif (variable_on_text[i][0:2] != 'pn'):
    #                             param_type = 'pn'
    #                     elif (type_param.upper() == 'STRING'):
    #                         if (variable_on_text[i][0:1] == 's'):
    #                             param_type = 'p'
    #                         elif (variable_on_text[i][0:2] != 'ps'):
    #                             param_type = 'ps'
    #                     elif (type_param.upper() == 'VARIANT') or (type_param.upper() == 'OLEVARIANT'):
    #                         if (variable_on_text[i][0:1] == 'v'):
    #                             param_type = 'p'
    #                         elif (variable_on_text[i][0:2] != 'pv'):
    #                             param_type = 'pv'
    #                     elif (type_param.upper() == 'BOOLEAN'):
    #                         if (variable_on_text[i][0:1] == 'b'):
    #                             param_type = 'p'
    #                         elif (variable_on_text[i][0:2] != 'pb'):
    #                             param_type = 'pb'
    #                     elif (type_param.upper() == 'TSPCLIENTDATASET') or (type_param.upper() == 'TCLIENTDATASET'):
    #                         if (variable_on_text[i][0:3] == 'cds'):
    #                             param_type = 'p'
    #                         elif (variable_on_text[i][0:1] != 'pcds'):
    #                             param_type = 'pcds'
    #                     else:
    #                         if (variable_on_text[i][0:1] == 'o'):
    #                             param_type = 'p'
    #                         elif (variable_on_text[i][0:2] != 'po'):
    #                             param_type = 'po'

    #                     variable_on_text_with_type.append(
    #                         param_type + variable_on_text[i] + ': ' + type_param + ';')
    #     pass
