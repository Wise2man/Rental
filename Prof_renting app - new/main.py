from database import init_db, add_image_column
from ui import RoomRentalApp

if __name__ == '__main__':
    init_db()  # Initialize the database
    add_image_column()  # Add image_path column if it doesn't exist
    RoomRentalApp().run()