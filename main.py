from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.storage.jsonstore import JsonStore

class EditScreen(Screen):
    def __init__(self, **kwargs):
        super(EditScreen, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Campo para el nombre de la biblioteca
        self.lib_name_input = TextInput(
            hint_text='Nombre de la biblioteca', size_hint_y=None, height=40)
        self.layout.add_widget(self.lib_name_input)
        
        # Campo para la pregunta de la flashcard
        self.question_input = TextInput(
            hint_text='Ingrese la pregunta', size_hint_y=None, height=40)
        self.layout.add_widget(self.question_input)
        
        # Campo para la respuesta de la flashcard
        self.answer_input = TextInput(
            hint_text='Ingrese la respuesta', size_hint_y=None, height=40)
        self.layout.add_widget(self.answer_input)
        
        # Botón para agregar una flashcard
        self.add_button = Button(text='Agregar Flashcard', size_hint_y=None, height=50)
        self.add_button.bind(on_press=self.add_flashcard)
        self.layout.add_widget(self.add_button)
        
        # Botón para guardar el nombre de la biblioteca
        self.update_lib_button = Button(
            text='Guardar Nombre de Biblioteca', size_hint_y=None, height=50)
        self.update_lib_button.bind(on_press=self.update_library_name)
        self.layout.add_widget(self.update_lib_button)
        
        # ScrollView para listar las flashcards
        self.scroll_view = ScrollView(size_hint=(1, 1))
        self.cards_container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        self.cards_container.bind(minimum_height=self.cards_container.setter('height'))
        self.scroll_view.add_widget(self.cards_container)
        self.layout.add_widget(self.scroll_view)
        
        # Botón para pasar a la pantalla de Play
        self.play_screen_button = Button(text='Ir a Play', size_hint_y=None, height=50)
        self.play_screen_button.bind(on_press=self.go_to_play)
        self.layout.add_widget(self.play_screen_button)
        
        self.add_widget(self.layout)
        self.refresh_flashcards()
    
    def update_library_name(self, instance):
        name = self.lib_name_input.text.strip()
        if name:
            self.app.library_name = name
            self.app.save_data()  # Guarda los cambios en el archivo
            print("Nombre de biblioteca actualizado a:", name)
    
    def add_flashcard(self, instance):
        question = self.question_input.text.strip()
        answer = self.answer_input.text.strip()
        if question and answer:
            self.app.flashcards.append({"question": question, "answer": answer})
            # Limpiar campos sin borrar flashcards ya guardadas
            self.question_input.text = ""
            self.answer_input.text = ""
            self.app.save_data()  # Guarda la flashcard añadida
            self.refresh_flashcards()
    
    def refresh_flashcards(self):
        # Limpiar el contenedor
        self.cards_container.clear_widgets()
        # Agregar cada flashcard con un botón para editarla
        for idx, card in enumerate(self.app.flashcards):
            card_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=10)
            card_label = Label(text=f"{idx+1}. {card['question']} - {card['answer']}",
                               halign="left", valign="middle")
            card_label.bind(size=card_label.setter('text_size'))
            card_layout.add_widget(card_label)
            edit_btn = Button(text='Editar', size_hint_x=None, width=80)
            edit_btn.bind(on_press=lambda inst, idx=idx: self.edit_flashcard(idx))
            card_layout.add_widget(edit_btn)
            self.cards_container.add_widget(card_layout)
    
    def edit_flashcard(self, index):
        # Popup para editar la flashcard
        card = self.app.flashcards[index]
        popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        popup_layout.add_widget(Label(text='Editar Pregunta:'))
        question_input = TextInput(text=card['question'], multiline=False)
        popup_layout.add_widget(question_input)
        popup_layout.add_widget(Label(text='Editar Respuesta:'))
        answer_input = TextInput(text=card['answer'], multiline=False)
        popup_layout.add_widget(answer_input)
        save_btn = Button(text='Guardar cambios', size_hint_y=None, height=40)
        popup_layout.add_widget(save_btn)
        
        popup = Popup(title="Editar Flashcard", content=popup_layout, size_hint=(0.8, 0.5))
        
        def save_changes(instance):
            new_question = question_input.text.strip()
            new_answer = answer_input.text.strip()
            if new_question and new_answer:
                self.app.flashcards[index] = {"question": new_question, "answer": new_answer}
                self.app.save_data()  # Guarda los cambios de la edición
                self.refresh_flashcards()
                popup.dismiss()
        
        save_btn.bind(on_press=save_changes)
        popup.open()
    
    def go_to_play(self, instance):
        self.manager.current = 'play'

class PlayScreen(Screen):
    def __init__(self, **kwargs):
        super(PlayScreen, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.current_index = 0
        self.showing_answer = False
        
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Label para mostrar la flashcard (pregunta o respuesta)
        self.flashcard_label = Label(text="Presiona 'Siguiente' para empezar", font_size=24)
        self.layout.add_widget(self.flashcard_label)
        
        # Botón para mostrar la respuesta o pasar a la siguiente flashcard
        self.next_button = Button(text='Siguiente', size_hint_y=None, height=50)
        self.next_button.bind(on_press=self.next_flashcard)
        self.layout.add_widget(self.next_button)
        
        # Botón para volver a la pantalla de edición
        self.back_button = Button(text='Volver a Editar', size_hint_y=None, height=50)
        self.back_button.bind(on_press=self.go_to_edit)
        self.layout.add_widget(self.back_button)
        
        self.add_widget(self.layout)
    
    def next_flashcard(self, instance):
        if not self.app.flashcards:
            self.flashcard_label.text = "No hay flashcards en la biblioteca."
            return
        
        if not self.showing_answer:
            # Muestra la pregunta de la flashcard actual
            card = self.app.flashcards[self.current_index]
            self.flashcard_label.text = f"Pregunta: {card['question']}\n\n(Presiona 'Siguiente' para ver la respuesta)"
            self.showing_answer = True
        else:
            # Muestra la respuesta y prepara la siguiente flashcard
            card = self.app.flashcards[self.current_index]
            self.flashcard_label.text = f"Pregunta: {card['question']}\nRespuesta: {card['answer']}"
            self.showing_answer = False
            self.current_index = (self.current_index + 1) % len(self.app.flashcards)
    
    def go_to_edit(self, instance):
        self.manager.current = 'edit'

class FlashcardApp(App):
    def build(self):
        # Usamos JsonStore para guardar la información de la biblioteca en un archivo
        self.store = JsonStore('flashcards.json')
        if self.store.exists('library'):
            data = self.store.get('library')
            self.library_name = data.get('name', "Mi Biblioteca")
            self.flashcards = data.get('flashcards', [])
        else:
            self.library_name = "Mi Biblioteca"
            self.flashcards = []
            self.save_data()  # Crea el archivo por primera vez
        
        sm = ScreenManager()
        self.edit_screen = EditScreen(name='edit')
        self.play_screen = PlayScreen(name='play')
        sm.add_widget(self.edit_screen)
        sm.add_widget(self.play_screen)
        return sm

    def save_data(self):
        self.store.put('library', name=self.library_name, flashcards=self.flashcards)

if __name__ == '__main__':
    FlashcardApp().run()
