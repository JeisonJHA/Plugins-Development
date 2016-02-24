import sublime_plugin
import re


class tryfinally(sublime_plugin.TextCommand):

    def run(self, edit):
        view = self.view
        selection_region = view.sel()[0]
        word_region = view.word(selection_region)
        word = view.substr(word_region).strip()
        word = re.sub('[\=\:\(\)\{\}\s]', '', word)
        for selectedReg in view.sel():
            line, regionColumn = view.rowcol(selectedReg.begin())
        linha = line + 1

        nav_line = linha - 1
        nav_pt = view.text_point(nav_line, 0)
        view.set_viewport_position(view.text_to_layout(nav_pt))
        qtdLinha = 0
        ponto = view.text_point(line, 0)
        texto_linha = view.substr(view.line(ponto))
        if texto_linha.find('.') > 0:
            if len(texto_linha) > 15:
                while texto_linha.find(';') < 0:
                    ponto = view.text_point(line, 0)
                    texto_linha = view.substr(view.line(ponto))
                    if texto_linha.find(';') < 0:
                        line = line + 1
                        qtdLinha = qtdLinha + 1
                    if (qtdLinha == 6):
                        print('muito grande')
                        break
                    pass

        fn_line = line + 1
        pt = view.text_point(fn_line, 0)
        view.insert(edit, pt, '\n' + 'try' + '\n')

        linha_selecao = fn_line + 2
        pt = view.text_point(linha_selecao, 0)
        view.insert(edit, pt, '  ' + view.substr(word_region) + ' \n')

        linha_finally = linha_selecao + 1 + qtdLinha
        pt = view.text_point(linha_finally, 0)
        view.insert(edit, pt, 'finally' + '\n')

        linha_freeandnil = linha_finally + 1
        pt = view.text_point(linha_freeandnil, 0)
        if word.find('.') >= 0:
            word = word.split(".")[0]
        view.insert(edit, pt, '  FreeAndNil(' + word + ');' + '\n')

        linha_end = linha_freeandnil + 1
        pt = view.text_point(linha_end, 0)
        view.insert(edit, pt, 'end;' + '\n')
