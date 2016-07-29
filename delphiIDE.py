import sublime_plugin


class MethodDeclaration(object):
    """docstring for MethodDeclaration"""

    def __init__(self):
        self._methodclass = None
        self.has_implementation = False
        self.has_interface = False

    @property
    def has_implementation(self):
        return self._has_implementation

    @has_implementation.setter
    def has_implementation(self, value):
        self._has_implementation = value

    @property
    def has_interface(self):
        return self._has_interface

    @has_interface.setter
    def has_interface(self, value):
        self._has_interface = value

    @property
    def methodname(self):
        return self._methodname

    @methodname.setter
    def methodname(self, value):
        self._methodname = value

    @property
    def methodregion(self):
        return self._methodregion

    @methodregion.setter
    def methodregion(self, value):
        self._methodregion = value

    @property
    def visibility(self):
        return self._visibility

    @visibility.setter
    def visibility(self, value):
        self._visibility = value

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, value):
        self._params = value

    @property
    def methodclass(self):
        return self._methodclass

    @methodclass.setter
    def methodclass(self, value):
        self._methodclass = value


class ClassDeclaration(object):
    """docstring for ClassDeclaration"""

    @property
    def classname(self):
        return self._classname

    @classname.setter
    def classname(self, value):
        self._classname = value

    @property
    def classregion(self):
        return self._classregion

    @classregion.setter
    def classregion(self, value):
        self._classregion = value

    @property
    def privateregion(self):
        return self._privateregion

    @privateregion.setter
    def privateregion(self, value):
        self._privateregion = value

    @property
    def protectedregion(self):
        return self._protectedregion

    @protectedregion.setter
    def protectedregion(self, value):
        self._protectedregion = value

    @property
    def publicregion(self):
        return self._publicregion

    @publicregion.setter
    def publicregion(self, value):
        self._publicregion = value

    @property
    def publishedregion(self):
        return self._publishedregion

    @publishedregion.setter
    def publishedregion(self, value):
        self._publishedregion = value


class DelphiIdeCommand(sublime_plugin.TextCommand):
    # // { "keys": ["ctrl+shift+x"], "command": "delphi_ide", "args": {"teste": "delphimethodnav"}}
    # view.window().run_command('show_panel',
    # args={"panel": 'output.find_results', "toggle": True})

    def run(self, edit, teste):
        print('teste[0]:%s' % teste)

        method = None
        try:
            method = getattr(self, teste)
        except AttributeError:
            raise NotImplementedError("Class `{}` does not implement `{}`".
                                      format(self.__class__.__name__,
                                             teste))

        method()

    def delphimethodnav(self):
        print('vai doido')

    def getMethodInformation(self):
        view = self.view
        cursor_region = view.sel()[0]
        cursor_pt = view.sel()[0].begin()

        if not view.match_selector(cursor_pt,
                                   'function.implementation.delphi'):
            # exit because it is not in a method
            return None

        def params(region):
            params_region = view.find_by_selector(
                'meta.function.parameters.delphi')
            param_name_region = view.find_by_selector(
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
                x = [view.substr(x) for x in params_region_filt]
                return x
            except:
                return []

        def getFunctionName():
            functionname = view.find_by_selector('entity.name.function')
            functionnamefiltered = [
                n for n in functionname if method.methodregion[0].contains(n)]

            return view.substr(functionnamefiltered[0])
        # has_implementation
        # has_interface
        # methodname
        # methodregion
        # visibility
        # params
        # methodclass
        method = MethodDeclaration()
        selector = view.find_by_selector
        method.methodregion = [r for r in selector('meta.function.delphi')
                               if cursor_region.intersects(r)]
        method.methodname = getFunctionName()

        method.params = self.paramsFromRegion(method.methodregion[0])

        return method

    def getClassInformation(self):
        pass
