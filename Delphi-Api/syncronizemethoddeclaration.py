import sublime_plugin
from . import *


class syncronizemethoddeclaration(sublime_plugin.TextCommand):

    def run(self, edit):
        print("Syncronize method")
        self.syncronizemethod(edit)

    def syncronizemethod(self, edit):
        classe = GetClassName(self.view)
        if classe:
            classe += '.'

        method_type = GetMethodType(self.view)
        method, region_method = GetName(self.view, True)

        regions = None
        parameters = GetParametersName(self.view, region_method)
        if parameters:
            parameters = "".join(parameters)
            regions = GetMethodRegionsWithParams(self.view, method, parameters)
        if (regions is None) or len(regions) == 1:
            regions = self.GetMethodRegions(self.view, method)

        parameters = GetParameters(self.view, region_method)

        method_with_params = not (parameters is None)

        method_type = GetMethodType(self.view)
        function_return = ''
        if (method_type == 'function') or (method_type == 'class function'):
            function_return, dummy = GetReturnType(
                self.view, regions[0], method_with_params)
            regions[0] = sublime.Region(regions[0].begin(),
                                        dummy.end())

            function_return, dummy = GetReturnType(
                self.view, regions[1], method_with_params)
            regions[1] = sublime.Region(regions[1].begin(),
                                        dummy.end())
            function_return = ': ' + function_return

        if method_with_params:
            parameters = '(' + parameters + ')'
        else:
            parameters = ''

        method_declaration = method_type + ' ' + classe + \
            method + parameters + function_return + ';'
        self.view.replace(edit, regions[1], method_declaration)

        method_declaration = '    ' + method_type + \
            ' ' + method + parameters + function_return + ';'
        self.view.replace(edit, regions[0], method_declaration)

    def GetMethodRegions(self, view, method):
        result = []
        for region in view.sel():
            region_row, region_col = view.rowcol(region.begin())
            function_regions = view.find_by_selector('meta.function')
            if function_regions:
                for r in (function_regions):
                    pos = 0
                    lines = view.substr(r).splitlines()
                    if (len(lines[0].split(".")) > 1 and
                            lines[0].split(".")[1] == ''):
                        pos = 1
                    name = clean_name.sub('', lines[pos])
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
