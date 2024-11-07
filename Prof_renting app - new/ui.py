import os
import sqlite3
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from database import (
    add_user, get_user, add_room, update_room, get_available_rooms,
    get_rooms_count, book_room, get_all_users, remove_user,
    get_payments_by_customer, get_total_payments_by_landlord,
    add_payment
)

class RoomRentalApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')
        self.current_page = 0
        self.rooms_per_page = 3
        self.total_rooms = 0
        self.show_login_screen()
        return self.layout

    def show_login_screen(self):
        self.layout.clear_widgets()
        self.layout.add_widget(Label(text='Login'))
        self.username_input = TextInput(hint_text='Username')
        self.password_input = TextInput(hint_text='Password', password=True)
        self.role_layout = BoxLayout(orientation='horizontal')
        self.role_customer = ToggleButton(text='Customer', group='role')
        self.role_landlord = ToggleButton(text='Landlord', group='role')
        self.role_admin = ToggleButton(text='Admin', group='role')
        self.role_layout.add_widget(self.role_customer)
        self.role_layout.add_widget(self.role_landlord)
        self.role_layout.add_widget(self.role_admin)
        self.login_button = Button(text='Login')
        self.create_account_button = Button(text='Create Account')
        self.login_button.bind(on_press=self.login)
        self.create_account_button.bind(on_press=self.show_create_account_screen)
        self.layout.add_widget(self.username_input)
        self.layout.add_widget(self.password_input)
        self.layout.add_widget(self.role_layout)
        self.layout.add_widget(self.login_button)
        self.layout.add_widget(self.create_account_button)

    def show_create_account_screen(self, instance=None):
        self.layout.clear_widgets()
        self.layout.add_widget(Label(text='Create Account'))
        self.new_username_input = TextInput(hint_text='New Username')
        self.new_password_input = TextInput(hint_text='New Password', password=True)
        self.new_role_layout = BoxLayout(orientation='horizontal')
        self.new_role_customer = ToggleButton(text='Customer', group='new_role')
        self.new_role_landlord = ToggleButton(text='Landlord', group='new_role')
        self.new_role_layout.add_widget(self.new_role_customer)
        self.new_role_layout.add_widget(self.new_role_landlord)
        self.create_button = Button(text='Create Account')
        self.back_button = Button(text='Back')
        self.create_button.bind(on_press=self.create_account)
        self.back_button.bind(on_press=self.back_to_login)
        self.layout.add_widget(self.new_username_input)
        self.layout.add_widget(self.new_password_input)
        self.layout.add_widget(self.new_role_layout)
        self.layout.add_widget(self.create_button)
        self.layout.add_widget(self.back_button)

    def create_account(self, instance):
        username = self.new_username_input.text
        password = self.new_password_input.text
        role = 'landlord' if self.new_role_landlord.state == 'down' else 'customer'
        
        if not username or not password:
            self.layout.add_widget(Label(text='Please fill in all fields.'))
            return

        if add_user(username, password, role):
            self.show_login_screen()
        else:
            self.layout.add_widget(Label(text='Username already exists.'))

    def back_to_login(self, instance):
        self.show_login_screen()

    def login(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        role = 'admin' if self.role_admin.state == 'down' else 'landlord' if self.role_landlord.state == 'down' else 'customer'
        
        if not username or not password:
            self.layout.add_widget(Label(text='Please fill in all fields.'))
            return

        if username == 'Wiseman' and password == 'Wize30' and role == 'admin':
            self.admin_dashboard()
            return
        
        user = get_user(username)
        if user and user[2] == password and user[3] == role:
            self.layout.clear_widgets()
            if role == 'landlord':
                self.landlord_dashboard(user[0])
            elif role == 'customer':
                self.customer_dashboard(user[0])
        else:
            self.layout.add_widget(Label(text='Invalid username, password, or role'))

    def landlord_dashboard(self, landlord_id):
        self.layout.clear_widgets()
        self.layout.add_widget(Label(text='Landlord Dashboard'))
        self.room_title_input = TextInput(hint_text='Room Title')
        self.room_desc_input = TextInput(hint_text='Room Description')
        self.room_price_input = TextInput(hint_text='Room Price')
        self.image_path = None
        self.image_button = Button(text='Add Room Image')
        self.add_room_button = Button(text='Add Room')
        self.view_customers_button = Button(text='View Customers')
        self.view_payments_button = Button(text='View Total Payments')
        self.logout_button = Button(text='Logout')
        self.edit_room_button = Button(text='Edit Room')
        
        self.image_button.bind(on_press=lambda x: self.choose_image())
        self.add_room_button.bind(on_press=lambda x: self.add_room(landlord_id))
        self.view_customers_button.bind(on_press=lambda x: self.view_customers(landlord_id))
        self.view_payments_button.bind(on_press=lambda x: self.view_payments(landlord_id))
        self.logout_button.bind(on_press=lambda x: self.show_login_screen())
        self.edit_room_button.bind(on_press=lambda x: self.edit_room(landlord_id))

        self.layout.add_widget(self.room_title_input)
        self.layout.add_widget(self.room_desc_input)
        self.layout.add_widget(self.room_price_input)
        self.layout.add_widget(self.image_button)
        self.layout.add_widget(self.add_room_button)
        self.layout.add_widget(self.view_customers_button)
        self.layout.add_widget(self.view_payments_button)
        self.layout.add_widget(self.edit_room_button)
        self.layout.add_widget(self.logout_button)

    def choose_image(self):
        filechooser = FileChooserIconView()
        filechooser.bind(on_submit=lambda *x: self.load_image(x[1][0]))
        popup = Popup(title='Select Room Image', content=filechooser, size_hint=(0.9, 0.9))
        popup.open()

    def load_image(self, image_path):
        self.image_path = image_path
        print(f"Image selected: {image_path}")

    def add_room(self, landlord_id):
        title = self.room_title_input.text
        description = self.room_desc_input.text

        if not title or not description or not self.image_path:
            self.layout.add_widget(Label(text='Please fill in all fields and select an image.'))
            return

        try:
            price = float(self.room_price_input.text)
        except ValueError:
            self.layout.add_widget(Label(text='Please enter a valid price.'))
            return

        add_room(landlord_id, title, description, price, self.image_path)
        self.landlord_dashboard(landlord_id)

    def edit_room(self, landlord_id):
        self.layout.clear_widgets()
        self.layout.add_widget(Label(text='Edit Room'))
        self.room_id_input = TextInput(hint_text='Room ID')
        self.new_room_title_input = TextInput(hint_text='New Room Title')
        self.new_room_desc_input = TextInput(hint_text='New Room Description')
        self.new_room_price_input = TextInput(hint_text='New Room Price')
        self.new_image_path = None

        self.image_button = Button(text='Add New Room Image')
        self.update_room_button = Button(text='Update Room')
        self.back_button = Button(text='Back to Dashboard')

        self.image_button.bind(on_press=lambda x: self.choose_image())
        self.update_room_button.bind(on_press=lambda x: self.update_room())
        self.back_button.bind(on_press=lambda x: self.landlord_dashboard(landlord_id))

        self.layout.add_widget(self.room_id_input)
        self.layout.add_widget(self.new_room_title_input)
        self.layout.add_widget(self.new_room_desc_input)
        self.layout.add_widget(self.new_room_price_input)
        self.layout.add_widget(self.image_button)
        self.layout.add_widget(self.update_room_button)
        self.layout.add_widget(self.back_button)

    def update_room(self):
        room_id = self.room_id_input.text
        title = self.new_room_title_input.text
        description = self.new_room_desc_input.text

        if not room_id or not title or not description:
            self.layout.add_widget(Label(text='Please fill in all fields.'))
            return

        try:
            price = float(self.new_room_price_input.text)
        except ValueError:
            self.layout.add_widget(Label(text='Please enter a valid price.'))
            return

        image_path = self.image_path if self.image_path else self.new_image_path

        update_room(int(room_id), title, description, price, image_path)
        self.landlord_dashboard(int(room_id))

    def view_customers(self, landlord_id):
        self.layout.clear_widgets()
        self.layout.add_widget(Label(text='Customers Renting Your Rooms'))
        conn = sqlite3.connect('rental_app.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.username, r.title 
            FROM bookings b
            JOIN users u ON b.customer_id = u.id
            JOIN rooms r ON b.room_id = r.id
            WHERE r.landlord_id = ?
        ''', (landlord_id,))
        customers = cursor.fetchall()
        conn.close()
        for customer in customers:
            self.layout.add_widget(Label(text=f"{customer[0]} - Renting {customer[1]}"))
        back_button = Button(text='Back to Dashboard')
        back_button.bind(on_press=lambda x: self.landlord_dashboard(landlord_id))
        self.layout.add_widget(back_button)

    def view_payments(self, landlord_id):
        self.layout.clear_widgets()
        self.layout.add_widget(Label(text='Total Payments Received'))
        total_payments = get_total_payments_by_landlord(landlord_id)
        self.layout.add_widget(Label(text=f'Total Payments: R{total_payments}'))
        back_button = Button(text='Back to Dashboard')
        back_button.bind(on_press=lambda x: self.landlord_dashboard(landlord_id))
        self.layout.add_widget(back_button)

    def customer_dashboard(self, customer_id):
        self.layout.clear_widgets()
        self.layout.add_widget(Label(text='Customer Dashboard'))
        self.total_rooms = get_rooms_count()
        self.current_page = 0
        self.show_rooms(customer_id)
        self.next_button = Button(text='Next Page')
        self.prev_button = Button(text='Previous Page')
        self.next_button.bind(on_press=lambda x: self.change_page(1, customer_id))
        self.prev_button.bind(on_press=lambda x: self.change_page(-1, customer_id))
        self.layout.add_widget(self.prev_button)
        self.layout.add_widget(self.next_button)
        self.logout_button = Button(text='Logout')
        self.logout_button.bind(on_press=lambda x: self.show_login_screen())
        self.layout.add_widget(self.logout_button)

    def show_rooms(self, customer_id):
        self.layout.clear_widgets()
        self.layout.add_widget(Label(text='Available Rooms'))
        scroll_view = ScrollView()
        room_layout = GridLayout(cols=3, spacing=10, size_hint_y=None)
        room_layout.bind(minimum_height=room_layout.setter('height'))
        rooms = get_available_rooms(self.current_page * self.rooms_per_page, self.rooms_per_page)
        for room in rooms:
            room_box = BoxLayout(orientation='vertical', size_hint_y=None, height=250)
            room_image = Image(source=room[6], allow_stretch=True, keep_ratio=True)
            room_label = Label(text=f"{room[1]} - R{room[4]}")
            details_button = Button(text='View Details')
            details_button.bind(on_press=lambda x, room_id=room[0]: self.show_room_details(room_id, customer_id))
            room_box.add_widget(room_image)
            room_box.add_widget(room_label)
            room_box.add_widget(details_button)
            room_layout.add_widget(room_box)
        scroll_view.add_widget(room_layout)
        self.layout.add_widget(scroll_view)

    def show_room_details(self, room_id, customer_id):
        self.layout.clear_widgets()
        room_details = self.get_room_details(room_id)
        self.layout.add_widget(Label(text=f"Room Title: {room_details[1]}"))
        self.layout.add_widget(Label(text=f"Description: {room_details[3]}"))
        self.layout.add_widget(Label(text=f"Price: R{room_details[4]}"))
        book_button = Button(text='Book Room')
        book_button.bind(on_press=lambda x: self.book_room(room_id, customer_id))
        back_button = Button(text='Back to Rooms')
        back_button.bind(on_press=lambda x: self.show_rooms(customer_id))
        self.layout.add_widget(book_button)
        self.layout.add_widget(back_button)

    def book_room(self, room_id, customer_id):
        booking_id = book_room(room_id, customer_id)
        self.layout.clear_widgets()
        self.layout.add_widget(Label(text='Booking Successful!'))
        back_button = Button(text='Back to Rooms')
        back_button.bind(on_press=lambda x: self.customer_dashboard(customer_id))
        self.layout.add_widget(back_button)

    def change_page(self, direction, customer_id):
        self.current_page += direction
        if self.current_page < 0:
            self.current_page = 0
        elif self.current_page * self.rooms_per_page >= self.total_rooms:
            self.current_page -= direction  # Revert the page change if out of bounds
        self.show_rooms(customer_id)

    def get_room_details(self, room_id):
        conn = sqlite3.connect('rental_app.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM rooms WHERE id = ?', (room_id,))
        room_details = cursor.fetchone()
        conn.close()
        return room_details

if __name__ == '__main__':
    RoomRentalApp().run()