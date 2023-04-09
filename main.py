import os
from py_expression_eval import Parser
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.client.EventListener import EventListener

class BetterCalculator(EventListener):

    def on_event(self, event, extension):
        if isinstance(event, KeywordQueryEvent):
            return self.handle_query(event)
        elif isinstance(event, ItemEnterEvent):
            return self.handle_enter(event)

    def handle_query(self, event):
        expression = event.get_argument()

        if not expression:
            return

        try:
            parser = Parser()
            result = parser.parse(expression).evaluate({})
            return RenderResultListAction([
                ExtensionResultItem(
                    icon='icon.svg',
                    name=f"Result: {result}",
                    on_enter=ItemEnterEvent(f"Copy {result} to clipboard")
                )
            ])
        except Exception:
            return RenderResultListAction([
                ExtensionResultItem(
                    icon='icon.svg',
                    name="Invalid expression",
                    on_enter=None
                )
            ])

    def handle_enter(self, event):
        data = event.get_data()
        if data.startswith('Copy '):
            value = data[len('Copy '):]
            os.system(f'echo -n "{value}" | xclip -selection clipboard')

if __name__ == '__main__':
    from ulauncher.api.client.Extension import Extension
    from ulauncher.api.client.Client import Client
    from ulauncher.api.client.ClientMeta import ClientMeta
    from ulauncher.api.client.ClientException import ClientException

    meta = ClientMeta('Better Calculator')
    extension = Extension(meta)
    extension.set_event_listener(BetterCalculator())
    try:
        Client(extension).run()
    except ClientException as e:
        print('Error: %s' % e.get_message())
