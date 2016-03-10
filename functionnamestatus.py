import sublime
import sublime_plugin

import re
import sys
from time import time

# Ideas taken from C0D312, nizur & tito in http://www.sublimetext.com/forum/viewtopic.php?f=2&t=4589
# Also, from
# https://github.com/SublimeText/WordHighlight/blob/master/word_highlight.py


def plugin_loaded():
    global Pref

    class Pref:

        def load(self):
            Pref.display_file = settings.get('display_file', False)
            Pref.display_class = settings.get('display_class', False)
            Pref.display_function = settings.get('display_function', True)
            Pref.display_arguments = settings.get('display_arguments', False)
            Pref.display_visibility = settings.get('display_visibility', True)
            Pref.wait_time = 0.12
            Pref.time = time()

    settings = sublime.load_settings('Function Name Display.sublime-settings')
    Pref = Pref()
    Pref.load()
    settings.add_on_change('reload', lambda: Pref.load())

if sys.version_info[0] == 2:
    plugin_loaded()

clean_name = re.compile(
    '^\s*(public\s+|private\s+|protected\s+|static\s+|procedure\s+|function\s+|def\s+)+', re.I)

clean_name_private = re.compile('^\s*()+', re.I)


class FunctionNameStatusEventHandler(sublime_plugin.EventListener):
    # on_activated_async seems to not fire on startup

    def on_activated(self, view):
        Pref.time = time()
        view.settings().set('function_name_status_row', -1)
        sublime.set_timeout(
            lambda: self.display_current_class_and_function(view,
                                                            'activated'), 0)

    # why is it here?
    def on_modified(self, view):
        return
        Pref.time = time()

    # could be async, but ST2 does not support that
    def on_selection_modified(self, view):
        now = time()
        if now - Pref.time > Pref.wait_time:
            sublime.set_timeout(lambda:
                                self.display_current_class_and_function(
                                    view, 'selection_modified'), 0)
        else:
            sublime.set_timeout(lambda:
                                self.
                                display_current_class_and_function_delayed(
                                    view), int(1000 * Pref.wait_time))
        Pref.time = now

    def display_current_class_and_function_delayed(self, view):
        return
        now = time()
        if (now - Pref.time >= Pref.wait_time):
            self.display_current_class_and_function(
                view, 'selection_modified:delayed')

    # display the current class and function name
    def display_current_class_and_function(self, view, where):
        # print("display_current_class_and_function running from " + where)
        view_settings = view.settings()
        if view_settings.get('is_widget'):
            return

        for region in view.sel():
            region_row, region_col = view.rowcol(region.begin())

            if region_row != view_settings.get('function_name_status_row', -1):
                view_settings.set('function_name_status_row', region_row)
            else:
                return

            s = ""
            found = False

            fname = view.file_name()
            if Pref.display_file and None != fname:
                s = fname + " "

            # Look for any classes
            if Pref.display_class:
                class_regions = view.find_by_selector('entity.name.class')
                for r in reversed(class_regions):
                    row, col = view.rowcol(r.begin())
                    if row <= region_row:
                        s += view.substr(r)
                        found = True
                        break

            # Look for any functions
            if Pref.display_function:
                function_regions = view.find_by_selector('meta.function')
                if function_regions:
                    for r in reversed(function_regions):
                        row, col = view.rowcol(r.begin())
                        if row <= region_row:
                            if Pref.display_class and s:
                                s += "::"
                            lines = view.substr(r).splitlines()
                            name = clean_name.sub('', lines[0])

                            if Pref.display_arguments:
                                s += name.strip()
                            else:
                                # if 'C++' in view.settings().get('syntax'):
                                #     if Pref.display_class or len(
                                #             name.split('(')[0].split('::')) < 2:
                                #         s += name.split('(')[0].strip()
                                #     else:
                                #         s += name.split(
                                #             '(')[0].split('::')[1].strip()
                                # else:
                                s += name.split('(')[0].split(
                                    ':')[0].split(';')[0].strip()
                            found = True
                            break

            if Pref.display_visibility:
                s += self.MethodVisibility(view, s)

            if not found:
                view.erase_status('function')
                fname = view.file_name()
                if Pref.display_file and None != fname:
                    view.set_status('function', fname)
            else:
                view.set_status('function', s)

            return

        view.erase_status('function')

    def MethodVisibility(self, view, method):
        region_private = self.GetDeclarationRegion(view, 'private')

        region_protected = self.GetDeclarationRegion(view, 'protected')

        region_public = self.GetDeclarationRegion(view, 'public')

        region_published = self.GetDeclarationRegion(view, 'published')

        region_implementation = self.GetDeclarationRegion(
            view, 'implementation')
        # print(method)
        if method.find('.') >= 0:
            method = method.split('.')[1].split(';')[0]
        region_method = self.GetMethodRegion(view, method)
        if region_method is None or (region_private is None and
                                     region_protected is None and
                                     region_public is None and
                                     region_published is None):
            return ''

        if (region_implementation < region_method):
            return ''

        if self.TestaRegiaoPrivate(region_method, region_private,
                                   region_protected,
                                   region_public,
                                   region_published):
            return ' private'
        elif self.TestaRegiaoProtected(region_method, region_protected,
                                       region_public,
                                       region_published):
            return ' protected'
        elif self.TestaRegiaoPublic(region_method, region_public,
                                    region_published):
            return ' public'
        elif self.TestaRegiaoPublished(region_method, region_published):
            return ' published'
        else:
            return ''

    def TestaRegiaoPrivate(self, region_method, region_private,
                           region_protected, region_public,
                           region_published):

        if (region_private is None):
            return False

        if (region_protected is None) and (region_public is None) and \
                (region_published is None):
            return True

        if (region_method > region_private) and \
                (not (region_protected is None) and
                    (region_method < region_protected)):
            return True

        if (region_protected is None) and \
            ((not (region_public is None) and
              (region_method < region_public)) or
             (not (region_published is None) and
              (region_method < region_published))):
            return True

        return False

    def TestaRegiaoProtected(self, region_method, region_protected,
                             region_public, region_published):
        if (region_protected is None):
            return False

        if (region_public is None) and \
                (region_published is None):
            return True

        if (region_method > region_protected) and \
                ((not (region_public is None) and
                  (region_method < region_public))):
            return True

        if (region_public is None) and (not (region_published is None) and
                                        (region_method < region_published)):
            return True

        return False

    def TestaRegiaoPublic(self, region_method, region_public,
                          region_published):
        if (region_public is None):
            return False

        if (region_published is None):
            return True

        if (region_method > region_public) and \
                (not (region_published is None) and
                 (region_method < region_published)):
            return True

        return False

    def TestaRegiaoPublished(self, region_method, region_published):
        if (region_published is None):
            return False

        if (region_method > region_published):
            return True

        return False

    def GetDeclarationRegion(self, view, word):
        regions = [sublime.Region(view.size(), view.size())]
        for region in regions:
            region_row, region_col = view.rowcol(region.begin())
            function_regions = view.find_by_selector('keyword.visibility')
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

    def GetMethodRegion(self, view, word):
        for region in view.sel():
            region_row, region_col = view.rowcol(region.begin())
            function_regions = view.find_by_selector('meta.function')
            if function_regions:
                for r in function_regions:
                    row, col = view.rowcol(r.begin())
                    if row <= region_row:
                        lines = view.substr(r).splitlines()
                        name = clean_name_private.sub('', lines[0])
                        s = name.strip()
                        if s.find(word) >= 0:
                            return r
                            break
