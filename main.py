import os
from py_expression_eval import Parser
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction

class BetterCalculatorExtension(Extension):
    def __init__(self):
        super(BetterCalculatorExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        expression = event.get_argument() or ''

        if expression == '':
            return RenderResultListAction([])

        fixed_expression = self.fix_missing_brackets(expression)

        try:
            parser = Parser()
            result = self.convert_float_to_int(parser.parse(fixed_expression).evaluate({}))
            return RenderResultListAction([
                ExtensionResultItem(
                    icon='images/icon.svg',
                    name=str(result),
                    description=fixed_expression,
                    on_enter=ExtensionCustomAction(f'Copy {result}')
                )
            ])
        except Exception:
            return RenderResultListAction([
                ExtensionResultItem(
                    icon='images/icon.svg',
                    name='Invalid Expression',
                    on_enter=None
                )
            ])

    def fix_missing_brackets(self, expression):
        open_bracket_count = 0
        close_bracket_count = 0
        pending_brackets = []

        for char in expression:
            if char == '(':
                open_bracket_count += 1
            elif char == ')':
                if open_bracket_count > close_bracket_count:
                    close_bracket_count += 1
                else:
                    pending_brackets.append('(')

        missing_close_brackets = open_bracket_count - close_bracket_count
        expression = ''.join(pending_brackets) + expression
        expression += ')' * missing_close_brackets

        return expression

    def convert_float_to_int(self, number):
        if type(number) != int and number.is_integer():
            return int(number)
        else:
            return number


class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        data = event.get_data()

        if data.startswith('Copy '):
            value = data[len('Copy '):]
            os.system(f'echo -n "{value}" | xclip -selection clipboard')
 

if __name__ == '__main__':
    BetterCalculatorExtension().run()
