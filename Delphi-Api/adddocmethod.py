import datetime
import os
import sublime_plugin
from . import *


class AddDocMethodCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        print("Add doc")
        settings = sublime.load_settings('delphi.sublime-settings')
        if not (settings.get("methoddoctype", "XML") in ["XML", "JAVADOC"]):
            sublime.message_dialog('"methoddoctype" not configured.')
            return
        datetimeformat = settings.get("datetimeformat", "%d/%m/%Y")

        self.methoddocXML = settings.get("methoddoctype", "XML") == "XML"

        view = self.view
        method, region_method = GetName(view, True)
        params = GetParametersName(view, region_method)

        method_with_params = (params != []) and not (params is None)

        method_type = GetMethodType(view)

        begin = '' if self.methoddocXML else '{'
        end = '' if self.methoddocXML else '}\n'

        method_title = ('/// <summary>\n' +
                        '/// \n' +
                        '/// </summary>\n' if self.methoddocXML else
                        '\n    @Summary:\n')

        tag = 'Owner: ' + \
            os.environ['USERNAME'].title() + ' Date: ' + \
            datetime.datetime.now().strftime(datetimeformat)

        tag = ('/// <remarks>\n'
               '/// ' + tag + '\n'
               '/// </remarks>\n' if self.methoddocXML else
               '    @Remarks: ' + tag + '\n')

        variable = ''
        if method_with_params:
            variable = self.GetParams(params)

        function_return = ''
        if (method_type == 'function') or (method_type == 'class function'):
            function_return = (
                '/// <returns></returns>\n' if self.methoddocXML else
                '    @Return:\n')

        if (method_type == 'property'):
            function_return = (
                '/// <value></value>\n' if self.methoddocXML else
                '    @Value:\n')

        self.view.run_command("insert_snippet",
                              {"contents": "%s" % begin + method_title + tag +
                               variable + function_return + end})
        view.show(region_method)

    def GetParams(self, params):
        variable_name = GetParams(params)

        param_return = ''
        for variable in variable_name:
            if variable:
                if self.methoddocXML:
                    param_return += ('/// <param name="' + variable + '">\n' +
                                     '/// </param>\n')
                else:
                    param_return += ('    @Param: ' + variable + '\n')
        return param_return
