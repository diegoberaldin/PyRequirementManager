
from src import model as mdl


class LaTeXPrinter(object):
    def __init__(self, target_file_path):
        self._target_file_path = target_file_path

    def run(self):
        with open(self._target_file_path, 'w') as output:
            text = self._generate_text()
            output.write(text)

    def _generate_text(self):
        raise NotImplementedError('Override me!')


class TablePrinter(LaTeXPrinter):
    def __init__(self, target_file_path):
        super(TablePrinter, self).__init__(target_file_path)

    def _generate_text(self):
        text = '\\rowcolors{3}{aubergine}{white}\n'
        text += self._get_table_definition()
        text += '\\toprule\n'
        text += self._get_headers()
        text += '\\midrule\n\\endhead\n'
        for element in self._get_content():
            text += ' & '.join(element) + '\\\\\n'
        text += '\\bottomrule\n'
        caption, label = self._get_caption_and_label()
        text += ('\\rowcolor{white}' + '\\caption{' + caption +
                 '}\\label{' + label + '}\n')
        text += '\\end{longtable}\n'
        return text

    def _get_table_definition(self):
        raise NotImplementedError('Override me!')

    def _get_headers(self):
        raise NotImplementedError('Override me!')

    def _get_content(self):
        """Returns an iterable of 3-tuples with the ID, the description and the
        parent of the item that needs to be printed.
        """
        raise NotImplementedError('Override me!')

    def _get_caption_and_label(self):
        """Returns the caption and label of the table to print.
        """
        raise NotImplementedError('Override me!')


class UseCaseTablePrinter(TablePrinter):
    def __init__(self, target_file_path):
        super(UseCaseTablePrinter, self).__init__(target_file_path)
        self._uc_id_list = mdl.dal.get_all_use_case_ids()

    def _get_table_definition(self):
        return '\\begin{longtable}{lp{.5\\textwidth}l}\n'

    def _get_headers(self):
        return ('\\sffamily\\bfseries ID & \\sffamily\\bfseries Descrizione '
                '& \\sffamily\\bfseries Padre\\\n')

    def _get_content(self):
        """Returns an iterable (generator) containing a 3-tuple with the
        ID, description and parent of every use case.
        """
        for uc_id in self._uc_id_list:
            uc = mdl.dal.get_use_case(uc_id)
            yield (uc.uc_id, uc.description, uc.parent_id or '--')

    def _get_caption_and_label(self):
        return ('Prospetto riepilogativo dei casi d\'uso', 'tab:uclist')


class RequirementTablePrinter(TablePrinter):
    def __init__(self, req_type, priority, target_file_path):
        super(RequirementTablePrinter, self).__init__(target_file_path)
        self._req_type = req_type
        self._priority = priority
        self._req_id_list = mdl.dal.get_all_requirement_ids_spec(
                    req_type, priority)

    def _get_table_definition(self):
        return '\\begin{longtable}{lp{.5\\textwidth}ll}\n'

    def _get_headers(self):
        return ('\\sffamily\\bfseries ID & \\sffamily\\bfseries Descrizione & '
                '\\sffamily\\bfseries Fonte & '
                '\\sffamily\\bfseries Padre\\\\\n')

    def _get_content(self):
        for req_id in self._req_id_list:
            req = mdl.dal.get_requirement(req_id)
            source = mdl.dal.get_source(req.source_id)
            yield (req.req_id, req.description, source.name,
                   req.parent_id or '--')

    def _get_caption_and_label(self):
        return ('Elenco dei requisiti {0} {1}.'.format(
                 ('funzionali' if self._req_type == 'F' else
                 'dichiarativi' if self._req_type == 'D' else
                 'prestazionali' if self._req_type == 'P' else 'qualitativi'),
                 ('obbligatori' if self._priority == 'O' else
                  'facoltativi' if self._priority == 'F' else 'desiderabili')),
                'tab:reqlist{0}{1}'.format(self._req_type, self._priority))


class UseCaseRequirementTrackPrinter(TablePrinter):
    def __init__(self, target_file_path):
        super(UseCaseRequirementTrackPrinter, self).__init__(target_file_path)
        self._uc_id_list = mdl.dal.get_all_use_case_ids()

    def _get_table_definition(self):
        return '\\begin{longtable}{lp{.8\textwidth}}\n'

    def _get_headers(self):
        return ('\\sffamily\\bfseries Caso d\'uso & '
                '\\sffamily\\bfseries Requisiti associati\\\\\n')

    def _get_content(self):
        for uc_id in self._uc_id_list:
            req_ids = mdl.dal.get_use_case_associated_requirements(uc_id)
            yield (uc_id, ', '.join(req_ids))

    def _get_caption_and_label(self):
        return ('Tracciamento requisiti -- casi d\'uso.', 'tab:ucreqtrack')
