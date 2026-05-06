import os
import glob
import pandas as pd
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle

# ऐप का बैकग्राउंड डार्क (Neon थीम के लिए) सेट करना
Window.clearcolor = (0.05, 0.05, 0.08, 1) 

class NeonQuizApp(App):
    def build(self):
        # CSV डेटा लोड करें
        self.quiz_data = self.load_all_csv_data()
        self.current_index = 0
        self.time_left = 10
        
        # मेन स्क्रीन का लेआउट
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # ऊपर का हेडर (Subject और Question Number)
        self.header_label = Label(
            text="Subject: Loading...", 
            size_hint=(1, 0.1), 
            color=(0, 0.95, 1, 1), # Neon Blue
            font_size='20sp',
            bold=True
        )
        self.layout.add_widget(self.header_label)
        
        # टाइमर (Timer)
        self.timer_label = Label(
            text="Time: 10.0s", 
            size_hint=(1, 0.1), 
            color=(1, 0, 0.8, 1), # Neon Pink
            font_size='35sp',
            bold=True
        )
        self.layout.add_widget(self.timer_label)
        
        # सवाल (Question Text)
        self.q_label = Label(
            text="Loading Question...", 
            size_hint=(1, 0.3), 
            font_size='22sp', 
            halign='center',
            valign='middle',
            text_size=(Window.width - 60, None)
        )
        self.layout.add_widget(self.q_label)
        
        # 4 ऑप्शंस (Options A, B, C, D)
        self.opt_buttons = {}
        for opt in ['A', 'B', 'C', 'D']:
            btn = Button(
                text=opt, 
                size_hint=(1, 0.15), 
                background_normal='', # कस्टम कलर के लिए इसे खाली छोड़ना ज़रूरी है
                background_color=(0.1, 0.1, 0.15, 1),
                color=(1, 1, 1, 1),
                font_size='18sp',
                bold=True
            )
            btn.bind(on_press=self.check_answer)
            self.opt_buttons[opt] = btn
            self.layout.add_widget(btn)
            
        # पहला सवाल लोड करें
        self.load_question()
        return self.layout

    def load_all_csv_data(self):
        """आपका पुराना लॉजिक जो फोल्डर की सभी CSV फाइलों को पढ़ता है"""
        all_questions = []
        csv_files = glob.glob("*.csv")
        for file in csv_files:
            try:
                df = pd.read_csv(file)
                if all(col in df.columns for col in ['q', 'A', 'B', 'C', 'D', 'ans']):
                    if 'sub' not in df.columns: 
                        df['sub'] = file.replace(".csv", "").upper()
                    df = df.fillna("")
                    all_questions.extend(df.to_dict(orient='records'))
            except:
                pass
                
        # अगर कोई फाइल न मिले तो बैकअप सवाल
        if not all_questions:
            return [
                {"q": "अमेज़ॅन नदी किस महासागर में गिरती है?", "A": "आर्कटिक", "B": "अटलांटिक", "C": "हिंद", "D": "प्रशांत", "ans": "B", "sub": "Geography"},
                {"q": "भारतीय संविधान में कितने भाग (Parts) हैं?", "A": "22", "B": "25", "C": "20", "D": "18", "ans": "B", "sub": "Polity"}
            ]
        return all_questions

    def load_question(self):
        # अगर सारे सवाल खत्म हो जाएं
        if self.current_index >= len(self.quiz_data):
            self.q_label.text = "Quiz Completed! 🎉"
            self.timer_label.text = ""
            self.header_label.text = "Finish"
            for btn in self.opt_buttons.values():
                btn.disabled = True
            return

        q = self.quiz_data[self.current_index]
        self.header_label.text = f"{q.get('sub', 'GK')} | Q {self.current_index + 1}/{len(self.quiz_data)}"
        self.q_label.text = str(q['q'])
        
        self.opt_buttons['A'].text = f"A) {q['A']}"
        self.opt_buttons['B'].text = f"B) {q['B']}"
        self.opt_buttons['C'].text = f"C) {q['C']}"
        self.opt_buttons['D'].text = f"D) {q['D']}"
        
        # बटनों का रंग रीसेट करना और चालू करना
        for btn in self.opt_buttons.values():
            btn.background_color = (0.1, 0.1, 0.2, 1)
            btn.disabled = False
            
        # टाइमर रीसेट करना
        self.time_left = 10
        self.timer_label.text = f"{self.time_left}.0s"
        
        # पुराना टाइमर रोककर नया शुरू करें
        Clock.unschedule(self.update_timer)
        Clock.schedule_interval(self.update_timer, 1)

    def update_timer(self, dt):
        """हर 1 सेकंड में टाइमर अपडेट करता है"""
        self.time_left -= 1
        self.timer_label.text = f"{self.time_left}.0s"
        
        if self.time_left <= 0:
            Clock.unschedule(self.update_timer)
            self.show_correct_answer_and_next()

    def check_answer(self, instance):
        """जब कोई बटन दबाता है"""
        Clock.unschedule(self.update_timer) # टाइमर रोक दें
        
        q = self.quiz_data[self.current_index]
        correct_ans_key = str(q['ans']).upper().strip()
        
        # पता करें कि कौन सा विकल्प चुना गया
        selected_key = ""
        for key, btn in self.opt_buttons.items():
            if btn == instance:
                selected_key = key
            btn.disabled = True # सारे बटन लॉक कर दें
            
        # जवाब चेक करें
        if selected_key == correct_ans_key:
            instance.background_color = (0, 0.8, 0.2, 1) # सही जवाब - हरा
        else:
            instance.background_color = (0.9, 0.1, 0.1, 1) # गलत जवाब - लाल
            # सही जवाब को हरा कर दें
            if correct_ans_key in self.opt_buttons:
                self.opt_buttons[correct_ans_key].background_color = (0, 0.8, 0.2, 1)
                
        # 1.5 सेकंड बाद अगला सवाल
        Clock.schedule_once(self.next_question, 1.5)

    def show_correct_answer_and_next(self):
        """अगर टाइम आउट हो जाए तो सही जवाब दिखाएं"""
        q = self.quiz_data[self.current_index]
        correct_ans_key = str(q['ans']).upper().strip()
        
        for key, btn in self.opt_buttons.items():
            btn.disabled = True
            if key == correct_ans_key:
                btn.background_color = (0, 0.8, 0.2, 1) # हरा
                
        Clock.schedule_once(self.next_question, 1.5)

    def next_question(self, dt):
        self.current_index += 1
        self.load_question()

if __name__ == '__main__':
    NeonQuizApp().run()
