import sublime_plugin


class changefunctionreturn(sublime_plugin.TextCommand):

    def run(self, edit, prompt=True, return_type=''):
        global classdefinition
        global class_name_region
        global methoddeclaration
        global classnamemethod
        global method_regions
        global cursor_pt
        global cursor_region
        global methodsname
        global vsubstr
        global research
        global view
        global methodstype
        global functionsreturn

        view = self.view
        vsubstr = view.substr
        cursor_pt = view.sel()[0].begin()
        cursor_region = view.sel()[0]

        if ((view.match_selector(
            cursor_pt, 'function.implementation.delphi')
        ) or (view.match_selector(cursor_pt, 'meta.function.delphi'))) \
                and prompt:
            print("Change method return")
            self.AskReturn(return_type)
            return

        # research = re.search
        selector = view.find_by_selector
        classdefinition = selector('entity.class.interface.delphi')
        class_name_region = selector('entity.class.definition.delphi')
        methoddeclaration = selector('meta.function.delphi')
        classnamemethod = selector('entity.class.name.delphi')
        method_regions = selector('function.implementation.delphi')
        methodsname = selector('entity.name.function')
        methodstype = selector('storage.type.function.delphi')
        functionsreturn = selector('return.type.delphi')

        if view.match_selector(cursor_pt, 'interface.block.delphi'):
            self.ChangeMethodReturnInterface(edit, return_type)
        else:
            self.ChangeMethodReturnImplementarion(edit, return_type)

    def ChangeMethodReturnInterface(edit, return_type):
        if not view.match_selector(cursor_pt, 'meta.function.delphi'):
            # exit because it is not in a method
            return
        pass

    def ChangeMethodReturnImplementarion(edit, return_type):
        if not view.match_selector(cursor_pt,
                                   'function.implementation.delphi'):
            # exit because it is not in a method
            return
        pass

    def DefineMethodDeclaration(self, edit, return_type):
        classe = GetClassName(self, self.view)

        tipo_metodo = GetMethodType(self.view)
        class_method = tipo_metodo.find('class') >= 0

        metodo, region_metodo = GetName(self.view, True)

        regions = None
        parameters = GetParametersName(self.view, region_metodo)
        if parameters:
            parameters = "".join(parameters)
            regions = GetMethodRegionsWithParams(self.view, metodo, parameters)
        if (regions is None) or len(regions) == 1:
            regions = self.GetMethodRegions(self.view, metodo)
        # regions = self.GetMethodRegions(self.view, metodo)

        parametros = GetParameters(self.view, region_metodo)
        # parametros = GetParametersName(self.view, region_metodo)

        method_with_params = not parametros is None
        if method_with_params:
            parametros = self.GetParams(parametros)

        if (tipo_metodo == 'function') or (tipo_metodo == 'class function'):
            _, region_return_interf = GetReturnType(
                self.view, regions[0], method_with_params)
            # print('region_return_interf:%s' % region_return_interf)

            _, region_return_implem = GetReturnType(
                self.view, regions[1], method_with_params)
            # print('region_return_implem:%s' % region_return_implem)
            self.view.replace(
                edit, region_return_implem, ');'
                if method_with_params else ';')
            self.view.replace(
                edit, region_return_interf, ');'
                if method_with_params else ';')
            regions = self.GetMethodRegions(self.view, metodo)

        retorno_funcao = return_type

        if retorno_funcao == '':
            tipo_metodo = 'procedure'
        else:
            tipo_metodo = 'function'
            retorno_funcao = ': ' + retorno_funcao

        if class_method:
            tipo_metodo = 'class ' + tipo_metodo
        if (parametros is None):
            parametros = ''
        else:
            parametros = '(' + parametros + ')'

        declaracao_metodo = tipo_metodo + ' ' + classe + \
            '.' + metodo + parametros + retorno_funcao + ';'
        self.view.replace(edit, regions[1], declaracao_metodo)

        declaracao_metodo = '    ' + tipo_metodo + \
            ' ' + metodo + parametros + retorno_funcao + ';'
        self.view.replace(edit, regions[0], declaracao_metodo)

    def GetMethodRegions(self, view, method):
        result = []
        for region in view.sel():
            region_row, region_col = view.rowcol(region.begin())
            function_regions = view.find_by_selector('meta.function')
            if function_regions:
                for r in (function_regions):
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
                    if s == method:
                        result.append(r)

        return result

    def GetParams(self, params):
        variable_name = params
        size = len(variable_name)
        i = 0
        param_return = ''
        for i in range(size):
            if (variable_name[i] != ''):
                param_return += variable_name[i]
        return param_return

    def AskReturn(self, return_type):
        self.view.window().show_input_panel(
            "Function return:",
            str(return_type),
            lambda f: self.view.run_command(
                "changefunctionreturn", {"return_type": f, "prompt": False}),
            None, None)
        pass
